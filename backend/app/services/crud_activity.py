from app.schemas.users import CurrentUser
from app.services.pipeline_repository import pipeline_repository


def create_activity(data: dict, current_user: CurrentUser):
    return pipeline_repository.create_record("activities", data, current_user)


def get_activities():
    return pipeline_repository.list_records("activities")


def get_activity(activity_id: str):
    return pipeline_repository.get_record("activities", activity_id)


def update_activity(activity_id: str, data: dict, current_user: CurrentUser):
    return pipeline_repository.update_record("activities", activity_id, data, current_user)


def delete_activity(activity_id: str, current_user: CurrentUser):
    return pipeline_repository.archive_record("activities", activity_id, current_user)
