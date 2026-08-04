from app.repositories.task_repository import TaskRepository

repository = TaskRepository()


def create_task(data: dict):
    return repository.create(data)


def get_tasks():
    return repository.get_all()


def get_task(task_id: str):
    return repository.get_by_id(task_id)


def update_task(task_id: str, data: dict):
    return repository.update(task_id, data)


def delete_task(task_id: str):
    return repository.delete(task_id)
