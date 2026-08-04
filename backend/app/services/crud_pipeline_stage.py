from app.repositories.pipeline_stage_repository import PipelineStageRepository


repository = PipelineStageRepository()


def create_pipeline_stage(data: dict):
    return repository.create(data)


def get_pipeline_stages():
    return repository.get_all()


def get_pipeline_stage(stage_id: str):
    return repository.get_by_id(stage_id)


def update_pipeline_stage(stage_id: str, data: dict):
    return repository.update(stage_id, data)


def delete_pipeline_stage(stage_id: str):
    return repository.delete(stage_id)
