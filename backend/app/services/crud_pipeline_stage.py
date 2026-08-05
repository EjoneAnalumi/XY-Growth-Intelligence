from app.schemas.users import CurrentUser
from app.services.pipeline_repository import pipeline_repository


def create_pipeline_stage(data: dict, current_user: CurrentUser):
    return pipeline_repository.create_record("pipeline_stages", data, current_user)


def get_pipeline_stages():
    return pipeline_repository.list_records("pipeline_stages")


def get_pipeline_stage(stage_id: str):
    return pipeline_repository.get_record("pipeline_stages", stage_id)


def update_pipeline_stage(stage_id: str, data: dict, current_user: CurrentUser):
    return pipeline_repository.update_record("pipeline_stages", stage_id, data, current_user)


def delete_pipeline_stage(stage_id: str, current_user: CurrentUser):
    return pipeline_repository.archive_record("pipeline_stages", stage_id, current_user)
