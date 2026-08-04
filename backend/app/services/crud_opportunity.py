from app.repositories.opportunity_repository import OpportunityRepository

repository = OpportunityRepository()


def create_opportunity(data: dict):
    return repository.create(data)


def get_opportunities():
    return repository.get_all()


def get_opportunity(opportunity_id: str):
    return repository.get_by_id(opportunity_id)


def get_opportunity_by_id(opportunity_id: str):
    return repository.get_by_id(opportunity_id)


def update_opportunity(opportunity_id: str, data: dict):
    return repository.update(opportunity_id, data)


def delete_opportunity(opportunity_id: str):
    return repository.delete(opportunity_id)
