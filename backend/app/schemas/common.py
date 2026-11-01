from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")


class ORM(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class Page(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    page_size: int


class PageParams(BaseModel):
    page: int = Field(1, ge=1)
    page_size: int = Field(50, ge=1, le=200)
    sort: str | None = None  # "-created_at"


class JobAccepted(BaseModel):
    job_id: str
    run_id: str | None = None
    status: str = "queued"


class JobOut(ORM):
    id: str
    run_id: str
    kind: str
    status: str
    step: str | None
    progress: int
    result: dict | None
    error: str | None


class ReasonIn(BaseModel):
    reason: str = Field(min_length=2, max_length=120)
