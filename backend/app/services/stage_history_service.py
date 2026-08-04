from app.repositories.stage_history_repository import StageHistoryRepository

repository = StageHistoryRepository()


def create_stage_history(data: dict):
    return repository.create(data)
