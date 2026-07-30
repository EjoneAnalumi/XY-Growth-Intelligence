from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Body, Depends, HTTPException, Query, status

from app.core.auth import get_current_user, require_roles
from app.schemas.contacts import ContactCreate, ContactListResponse, ContactResponse
from app.schemas.users import CurrentUser
from app.services.growth_repository import InMemoryGrowthRepository, get_growth_repository

router = APIRouter(prefix="/contacts", tags=["contacts"])

WriterUser = Annotated[
    CurrentUser,
    Depends(require_roles("admin", "management", "business_development")),
]
ReaderUser = Annotated[CurrentUser, Depends(get_current_user)]
Repository = Annotated[InMemoryGrowthRepository, Depends(get_growth_repository)]


@router.get("", response_model=ContactListResponse)
def list_contacts(
    repository: Repository,
    current_user: ReaderUser,
    company_id: Annotated[UUID | None, Query()] = None,
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> ContactListResponse:
    contacts = repository.list_contacts(company_id=company_id, limit=limit, offset=offset)
    total = repository.count_contacts(company_id=company_id)
    return ContactListResponse(items=contacts, total=total)


@router.post(
    "",
    response_model=ContactResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        401: {"description": "Missing or invalid bearer token."},
        403: {"description": "User role cannot create contacts."},
        404: {"description": "Company not found."},
        422: {"description": "Invalid contact payload."},
    },
)
def create_contact(
    payload: Annotated[
        ContactCreate,
        Body(
            openapi_examples={
                "valid": {
                    "summary": "Valid contact",
                    "value": {
                        "company_id": "10000000-0000-4000-8000-000000000001",
                        "first_name": "Mira",
                        "last_name": "Vale",
                        "email": "mira.vale@northstar-robotics.example",
                        "decision_category": "champion",
                    },
                },
                "invalid": {
                    "summary": "Invalid contact",
                    "value": {
                        "company_id": "not-a-uuid",
                        "first_name": "",
                        "last_name": "",
                        "email": "not-an-email",
                    },
                },
            }
        ),
    ],
    current_user: WriterUser,
    repository: Repository,
) -> ContactResponse:
    contact = repository.create_contact(payload, current_user)

    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found.")

    return contact


@router.get("/{contact_id}", response_model=ContactResponse)
def get_contact(
    contact_id: UUID,
    repository: Repository,
    current_user: ReaderUser,
) -> ContactResponse:
    contact = repository.get_contact(contact_id)

    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found.")

    return contact
