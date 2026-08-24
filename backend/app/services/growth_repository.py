from datetime import UTC, datetime
from os import getenv
from uuid import UUID, uuid4

from app.schemas.companies import CompanyCreate, CompanyResponse
from app.schemas.contacts import ContactCreate, ContactResponse
from app.schemas.icp import IcpScoreResponse
from app.schemas.users import CurrentUser
from app.scoring.icp import IcpScore


class InMemoryGrowthRepository:
    def __init__(self) -> None:
        self._companies: dict[UUID, CompanyResponse] = {}
        self._contacts: dict[UUID, ContactResponse] = {}
        self._icp_scores: dict[UUID, list[IcpScoreResponse]] = {}

    def reset(self) -> None:
        self._companies.clear()
        self._contacts.clear()
        self._icp_scores.clear()

    def list_companies(self, limit: int, offset: int) -> list[CompanyResponse]:
        companies = list(self._companies.values())
        return companies[offset : offset + limit]

    def count_companies(self) -> int:
        return len(self._companies)

    def find_company_duplicates(self, companies: list[CompanyCreate]) -> list[str]:
        existing_names = {company.name.casefold() for company in self._companies.values()}
        existing_domains = {
            company.domain.casefold()
            for company in self._companies.values()
            if company.domain is not None
        }
        duplicates: list[str] = []
        for company in companies:
            if company.name.casefold() in existing_names:
                duplicates.append("name")
            if company.domain is not None and company.domain.casefold() in existing_domains:
                duplicates.append("domain")
        return sorted(set(duplicates))

    def get_company_fit_scores(self) -> dict[str, int | None]:
        return {str(company.id): company.fit_score for company in self._companies.values()}

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

    def update_company(self, company_id: UUID, payload: dict, current_user: CurrentUser):
        company = self.get_company(company_id)
        if company is None:
            return None
        updated = company.model_copy(
            update={**payload, "updated_by": UUID(current_user.id), "updated_at": datetime.now(UTC)}
        )
        self._companies[company_id] = updated
        return updated

    def archive_company(self, company_id: UUID, current_user: CurrentUser):
        company = self._companies.pop(company_id, None)
        if company is None:
            return None
        for contact_id in [
            key for key, item in self._contacts.items() if item.company_id == company_id
        ]:
            self._contacts.pop(contact_id)
        return company.model_copy(
            update={"status": "inactive", "updated_by": UUID(current_user.id)}
        )

    def list_contacts(
        self,
        company_id: UUID | None,
        limit: int,
        offset: int,
    ) -> list[ContactResponse]:
        contacts = list(self._contacts.values())

        if company_id is not None:
            contacts = [contact for contact in contacts if contact.company_id == company_id]

        return contacts[offset : offset + limit]

    def count_contacts(self, company_id: UUID | None) -> int:
        if company_id is None:
            return len(self._contacts)

        return sum(1 for contact in self._contacts.values() if contact.company_id == company_id)

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

    def update_contact(self, contact_id: UUID, payload: dict, current_user: CurrentUser):
        contact = self.get_contact(contact_id)
        if contact is None:
            return None
        company_id = payload.get("company_id", contact.company_id)
        if company_id not in self._companies:
            return None
        updated = contact.model_copy(
            update={**payload, "updated_by": UUID(current_user.id), "updated_at": datetime.now(UTC)}
        )
        self._contacts[contact_id] = updated
        return updated

    def archive_contact(self, contact_id: UUID, current_user: CurrentUser):
        contact = self._contacts.pop(contact_id, None)
        if contact is None:
            return None
        return contact.model_copy(update={"updated_by": UUID(current_user.id)})

    def save_icp_score(
        self,
        company_id: UUID,
        score: IcpScore,
        current_user: CurrentUser,
    ) -> IcpScoreResponse | None:
        company = self.get_company(company_id)

        if company is None:
            return None

        now = datetime.now(UTC)
        result = IcpScoreResponse(
            id=uuid4(),
            company_id=company_id,
            score=score.score,
            max_score=score.max_score,
            tier=score.tier,
            explanations=score.explanations,
            calculated_by=UUID(current_user.id),
            calculated_at=now,
        )
        self._icp_scores.setdefault(company_id, []).append(result)
        self._companies[company_id] = company.model_copy(update={"fit_score": score.score})
        return result

    def get_latest_icp_score(self, company_id: UUID) -> IcpScoreResponse | None:
        scores = self._icp_scores.get(company_id, [])

        if not scores:
            return None

        return scores[-1]


repository = InMemoryGrowthRepository()


def get_growth_repository():
    database_url = getenv("DATABASE_URL")
    if database_url:
        from app.services.postgres_growth_repository import PostgresGrowthRepository

        return PostgresGrowthRepository(database_url)
    return repository
