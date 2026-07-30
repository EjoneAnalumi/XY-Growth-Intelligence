from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Body, Depends, HTTPException, status

from app.core.auth import get_current_user, require_roles
from app.schemas.companies import CompanyCreate, CompanyListResponse, CompanyResponse
from app.schemas.users import CurrentUser
from app.services.growth_repository import InMemoryGrowthRepository, get_growth_repository

router = APIRouter(prefix="/companies", tags=["companies"])

WriterUser = Annotated[
    CurrentUser,
    Depends(require_roles("admin", "management", "business_development")),
]
ReaderUser = Annotated[CurrentUser, Depends(get_current_user)]
Repository = Annotated[InMemoryGrowthRepository, Depends(get_growth_repository)]


@router.get("", response_model=CompanyListResponse)
def list_companies(repository: Repository, current_user: ReaderUser) -> CompanyListResponse:
    companies = repository.list_companies()
    return CompanyListResponse(items=companies, total=len(companies))


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
