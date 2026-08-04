from app.repositories.note_repository import NoteRepository


repository = NoteRepository()


def create_note(data: dict):
    return repository.create(data)


def get_notes():
    return repository.get_all()


def get_note(note_id: str):
    return repository.get_by_id(note_id)


def update_note(note_id: str, data: dict):
    return repository.update(
        note_id,
        data
    )


def delete_note(note_id: str):
    return repository.delete(
        note_id
    )