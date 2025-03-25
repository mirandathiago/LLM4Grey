from pydantic import BaseModel, Field
from typing import Literal

class OutputFormat(BaseModel):
    inclusion: Literal["Yes", "No"] = Field(
        ..., 
        description="Indicates whether the discussion should be included in the review ('Yes' or 'No')"
    )
    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="A value between 0 and 1 that reflects how strongly the discussion should be included in the review."
    )
    justification: str = Field(
        ..., 
        description="Textual justification explaining the inclusion or exclusion decision"
    )
