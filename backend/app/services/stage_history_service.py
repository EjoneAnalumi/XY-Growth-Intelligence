from app.schemas.users import CurrentUser
from app.services.pipeline_repository import pipeline_repository


def create_stage_history(data: dict, current_user: CurrentUser):
    return pipeline_repository.create_stage_history(data, current_user)


def get_stage_history(opportunity_id: str):
    return pipeline_repository.list_stage_history(opportunity_id)
