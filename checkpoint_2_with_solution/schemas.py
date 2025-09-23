from __future__ import annotations
from pydantic import BaseModel, Field


class Move(BaseModel):
    row: int = Field(description="Row index (0-2)")
    col: int = Field(description="Column index (0-2)")
    reason: str = Field(description="Reasoning for the move")
