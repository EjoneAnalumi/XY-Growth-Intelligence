from datetime import UTC, datetime
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


def get_growth_repository() -> InMemoryGrowthRepository:
    return repository
