from datetime import UTC, datetime
from uuid import UUID, uuid4

from app.schemas.companies import CompanyCreate, CompanyResponse
from app.schemas.contacts import ContactCreate, ContactResponse
from app.schemas.users import CurrentUser


class InMemoryGrowthRepository:
    def __init__(self) -> None:
        self._companies: dict[UUID, CompanyResponse] = {}
        self._contacts: dict[UUID, ContactResponse] = {}

    def reset(self) -> None:
        self._companies.clear()
        self._contacts.clear()

    def list_companies(self) -> list[CompanyResponse]:
        return list(self._companies.values())

    def create_company(self, payload: CompanyCreate, current_user: CurrentUser) -> CompanyResponse:
        now = datetime.now(UTC)
        user_id = UUID(current_user.id)
        company = CompanyResponse(
            **payload.model_dump(),
            id=uuid4(),
            created_by=user_id,
            updated_by=user_id,
            created_at=now,
            updated_at=now,
        )

        self._companies[company.id] = company
        return company

    def get_company(self, company_id: UUID) -> CompanyResponse | None:
        return self._companies.get(company_id)

    def list_contacts(self, company_id: UUID | None = None) -> list[ContactResponse]:
        contacts = list(self._contacts.values())

        if company_id is None:
            return contacts

        return [contact for contact in contacts if contact.company_id == company_id]

    def create_contact(
        self,
        payload: ContactCreate,
        current_user: CurrentUser,
    ) -> ContactResponse | None:
        if payload.company_id not in self._companies:
            return None

        now = datetime.now(UTC)
        user_id = UUID(current_user.id)
        contact = ContactResponse(
            **payload.model_dump(),
            id=uuid4(),
            owner_id=user_id,
            created_by=user_id,
            updated_by=user_id,
            created_at=now,
            updated_at=now,
        )

        self._contacts[contact.id] = contact
        return contact

    def get_contact(self, contact_id: UUID) -> ContactResponse | None:
        return self._contacts.get(contact_id)


repository = InMemoryGrowthRepository()


def get_growth_repository() -> InMemoryGrowthRepository:
    return repository
