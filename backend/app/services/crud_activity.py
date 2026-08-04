from app.repositories.activity_repository import ActivityRepository


repository = ActivityRepository()


def create_activity(data: dict):
    return repository.create(data)


def get_activities():
    return repository.get_all()


def get_activity(activity_id: str):
    return repository.get_by_id(activity_id)


def update_activity(activity_id: str, data: dict):
    return repository.update(
        activity_id,
        data
    )


def delete_activity(activity_id: str):
    return repository.delete(
        activity_id
    )