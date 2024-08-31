from pydantic import BaseModel, Field

from schemas.depends import ISO31661Alfa2Enum


class LocationArgs(BaseModel):
    city: str
    state: str | None = None
    country: ISO31661Alfa2Enum
    other_args: list[str] = Field(default=[], description='Other info for location')
