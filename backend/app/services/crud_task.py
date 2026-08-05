from app.schemas.users import CurrentUser
from app.services.pipeline_repository import pipeline_repository


def create_task(data: dict, current_user: CurrentUser):
    return pipeline_repository.create_record("tasks", data, current_user)


def get_tasks():
    return pipeline_repository.list_records("tasks")


def get_task(task_id: str):
    return pipeline_repository.get_record("tasks", task_id)


def update_task(task_id: str, data: dict, current_user: CurrentUser):
    return pipeline_repository.update_record("tasks", task_id, data, current_user)


def delete_task(task_id: str, current_user: CurrentUser):
    return pipeline_repository.archive_record("tasks", task_id, current_user)
