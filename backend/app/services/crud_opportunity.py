from app.schemas.users import CurrentUser
from app.services.pipeline_repository import pipeline_repository


def create_opportunity(data: dict, current_user: CurrentUser):
    return pipeline_repository.create_record("opportunities", data, current_user)


def get_opportunities():
    return pipeline_repository.list_records("opportunities")


def get_opportunity_by_id(opportunity_id: str):
    return pipeline_repository.get_record("opportunities", opportunity_id)


def update_opportunity(opportunity_id: str, data: dict, current_user: CurrentUser):
    return pipeline_repository.update_record("opportunities", opportunity_id, data, current_user)


def delete_opportunity(opportunity_id: str, current_user: CurrentUser):
    return pipeline_repository.archive_record("opportunities", opportunity_id, current_user)
