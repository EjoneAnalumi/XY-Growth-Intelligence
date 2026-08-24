from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Body, Depends, HTTPException, Query, Response, status

from app.core.auth import get_current_user, require_roles
from app.schemas.companies import (
    CompanyCreate,
    CompanyImportResponse,
    CompanyListResponse,
    CompanyResponse,
    CompanyUpdate,
)
from app.schemas.icp import IcpScoreResponse
from app.schemas.users import CurrentUser
from app.scoring.icp import IcpScoringEngine
from app.services.company_csv import CompanyCsvError, export_company_csv, parse_company_csv
from app.services.company_csv_repository import (
    CompanyCsvDuplicateError,
    CompanyCsvPersistenceError,
    get_postgres_company_csv_repository,
)
from app.services.growth_repository import InMemoryGrowthRepository, get_growth_repository

router = APIRouter(prefix="/companies", tags=["companies"])

WriterUser = Annotated[
    CurrentUser,
    Depends(require_roles("admin", "management", "business_development")),
]
ReaderUser = Annotated[CurrentUser, Depends(get_current_user)]
Repository = Annotated[InMemoryGrowthRepository, Depends(get_growth_repository)]


@router.get("", response_model=CompanyListResponse)
def list_companies(
    repository: Repository,
    current_user: ReaderUser,
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> CompanyListResponse:
    companies = repository.list_companies(limit=limit, offset=offset)
    return CompanyListResponse(items=companies, total=repository.count_companies())


@router.post(
    "",
    response_model=CompanyResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        401: {"description": "Missing or invalid bearer token."},
        403: {"description": "User role cannot create companies."},
        422: {"description": "Invalid company payload."},
    },
)
def create_company(
    payload: Annotated[
        CompanyCreate,
        Body(
            openapi_examples={
                "valid": {
                    "summary": "Valid company",
                    "value": {
                        "name": "Northstar Robotics Labs",
                        "domain": "northstar-robotics.example",
                        "industry": "Manufacturing Technology",
                        "headquarters_country": "United States",
                        "lead_source": "conference",
                    },
                },
                "invalid": {
                    "summary": "Invalid company",
                    "value": {"name": "", "employee_count": -5},
                },
            }
        ),
    ],
    current_user: WriterUser,
    repository: Repository,
) -> CompanyResponse:
    return repository.create_company(payload, current_user)


@router.post("/import", response_model=CompanyImportResponse, status_code=status.HTTP_201_CREATED)
def import_companies(
    csv_payload: Annotated[bytes, Body(media_type="text/csv")],
    current_user: WriterUser,
    repository: Repository,
) -> CompanyImportResponse:
    try:
        companies = parse_company_csv(csv_payload)
    except CompanyCsvError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "code": exc.code,
                "issues": [issue.model_dump(exclude_none=True) for issue in exc.issues],
            },
        ) from exc
    postgres_repository = get_postgres_company_csv_repository()
    duplicate_fields = (
        repository.find_company_duplicates(companies) if postgres_repository is None else []
    )
    if duplicate_fields:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "code": "duplicate_company",
                "fields": duplicate_fields,
            },
        )
    try:
        if postgres_repository is not None:
            created = postgres_repository.import_companies(companies, current_user)
        else:
            for company in companies:
                repository.create_company(company, current_user)
            created = len(companies)
    except CompanyCsvDuplicateError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"code": "duplicate_company", "fields": exc.fields},
        ) from exc
    except CompanyCsvPersistenceError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="CSV import is temporarily unavailable.",
        ) from exc
    return CompanyImportResponse(created=created)


@router.get("/export", response_class=Response)
def export_companies(repository: Repository, current_user: ReaderUser) -> Response:
    postgres_repository = get_postgres_company_csv_repository()
    try:
        companies = (
            postgres_repository.export_companies()
            if postgres_repository is not None
            else [
                CompanyCreate.model_validate(company.model_dump())
                for company in repository.list_companies(100000, 0)
            ]
        )
    except CompanyCsvPersistenceError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="CSV export is temporarily unavailable.",
        ) from exc
    return Response(
        content=export_company_csv(companies),
        media_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="companies.csv"'},
    )


@router.get("/{company_id}", response_model=CompanyResponse)
def get_company(
    company_id: UUID,
    repository: Repository,
    current_user: ReaderUser,
) -> CompanyResponse:
    company = repository.get_company(company_id)

    if company is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found.")

    return company


@router.patch("/{company_id}", response_model=CompanyResponse)
def update_company(
    company_id: UUID,
    payload: CompanyUpdate,
    repository: Repository,
    current_user: WriterUser,
) -> CompanyResponse:
    company = repository.update_company(
        company_id, payload.model_dump(exclude_unset=True), current_user
    )
    if company is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found.")
    return company


@router.delete("/{company_id}", response_model=CompanyResponse)
def archive_company(
    company_id: UUID,
    repository: Repository,
    current_user: WriterUser,
) -> CompanyResponse:
    company = repository.archive_company(company_id, current_user)
    if company is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found.")
    return company


@router.post(
    "/{company_id}/calculate-icp",
    response_model=IcpScoreResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        401: {"description": "Missing or invalid bearer token."},
        403: {"description": "User role cannot calculate ICP scores."},
        404: {"description": "Company not found."},
    },
)
def calculate_company_icp(
    company_id: UUID,
    repository: Repository,
    current_user: WriterUser,
) -> IcpScoreResponse:
    company = repository.get_company(company_id)

    if company is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found.")

    score = IcpScoringEngine().calculate(company)
    result = repository.save_icp_score(company_id, score, current_user)

    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found.")

    return result
