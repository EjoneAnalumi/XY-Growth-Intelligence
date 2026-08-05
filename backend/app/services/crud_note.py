from app.schemas.users import CurrentUser
from app.services.pipeline_repository import pipeline_repository


def create_note(data: dict, current_user: CurrentUser):
    return pipeline_repository.create_record("notes", data, current_user)


def get_notes():
    return pipeline_repository.list_records("notes")


def get_note(note_id: str):
    return pipeline_repository.get_record("notes", note_id)


def update_note(note_id: str, data: dict, current_user: CurrentUser):
    return pipeline_repository.update_record("notes", note_id, data, current_user)


def delete_note(note_id: str, current_user: CurrentUser):
    return pipeline_repository.archive_record("notes", note_id, current_user)
