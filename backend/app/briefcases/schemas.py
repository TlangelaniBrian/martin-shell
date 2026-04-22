import uuid
from datetime import datetime

from pydantic import BaseModel, Field, model_validator


class ReasonCaseRead(BaseModel):
    id: uuid.UUID
    case_id: int
    content: str | None
    order: int
    created_at: datetime
    case_name: str | None = None
    court: str | None = None
    citation: str | None = None
    date_decided: str | None = None

    model_config = {"from_attributes": True}

    @model_validator(mode="before")
    @classmethod
    def flatten_case(cls, data):
        """Pull case fields from the joined Case relationship."""
        if hasattr(data, "case") and data.case:
            case = data.case
            data = {
                "id": data.id,
                "case_id": data.case_id,
                "content": data.content,
                "order": data.order,
                "created_at": data.created_at,
                "case_name": case.case_name,
                "court": case.court,
                "citation": case.citation,
                "date_decided": str(case.date_decided) if case.date_decided else None,
            }
        return data


class ReasonRead(BaseModel):
    id: uuid.UUID
    title: str
    description: str | None
    content: str | None
    order: int
    created_at: datetime
    cases: list[ReasonCaseRead] = []

    model_config = {"from_attributes": True}


class BriefcaseRead(BaseModel):
    id: uuid.UUID
    name: str
    description: str | None
    created_at: datetime
    updated_at: datetime
    reasons: list[ReasonRead] = []

    model_config = {"from_attributes": True}


class BriefcaseListResponse(BaseModel):
    briefcases: list[BriefcaseRead]
    total: int


class BriefcaseCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=256)
    description: str | None = Field(None, max_length=2000)


class BriefcaseUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=256)
    description: str | None = Field(None, max_length=2000)


class ReasonCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=256)
    description: str | None = Field(None, max_length=2000)


class ReasonUpdate(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=256)
    description: str | None = Field(None, max_length=2000)
    content: str | None = Field(None, max_length=50_000)


class ReasonReorder(BaseModel):
    reason_ids: list[uuid.UUID]


class ReasonCaseCreate(BaseModel):
    case_id: int
    content: str | None = Field(None, max_length=50_000)


class ReasonCaseUpdate(BaseModel):
    content: str | None = Field(None, max_length=50_000)
    order: int | None = None


class ContentVersionRead(BaseModel):
    id: uuid.UUID
    content: str
    version: int
    created_at: datetime

    model_config = {"from_attributes": True}
