from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.core.auth import get_current_user, require_roles
from app.schemas.users import CurrentUser
from app.services.administration import DEFAULT_WEIGHTS, administration_repository

router = APIRouter(tags=["administration"])
Admin = Annotated[CurrentUser, Depends(require_roles("admin"))]
Reader = Annotated[CurrentUser, Depends(get_current_user)]


class IcpWeights(BaseModel):
    model_config = ConfigDict(extra="forbid")
    weights: dict[str, int]

    @model_validator(mode="after")
    def validate_weights(self):
        if set(self.weights) != set(DEFAULT_WEIGHTS):
            raise ValueError("Provide all eight supported ICP rules.")
        if any(value < 1 or value > 100 for value in self.weights.values()):
            raise ValueError("Each weight must be between 1 and 100.")
        if sum(self.weights.values()) != 100:
            raise ValueError("ICP weights must sum to 100.")
        return self


class ServiceInput(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    name: str = Field(min_length=1, max_length=120)
    description: str = Field(default="", max_length=2000)
    active: bool = True


@router.get("/icp-rules", response_model=IcpWeights)
def get_rules(user: Reader):
    return {"weights": administration_repository.get_weights()}


@router.put("/icp-rules", response_model=IcpWeights)
def update_rules(payload: IcpWeights, user: Admin):
    administration_repository.save_weights(payload.weights, user)
    return payload


@router.get("/services")
def list_services(user: Reader):
    return {"items": administration_repository.list_services()}


@router.post("/services", status_code=201)
def create_service(payload: ServiceInput, user: Admin):
    return administration_repository.save_service(payload.model_dump(), user)


@router.put("/services/{service_id}")
def update_service(service_id: UUID, payload: ServiceInput, user: Admin):
    result = administration_repository.save_service(payload.model_dump(), user, service_id)
    if result is None:
        raise HTTPException(404, "Service not found.")
    return result
