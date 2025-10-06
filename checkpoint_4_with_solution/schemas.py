from __future__ import annotations
from typing import List
from pydantic import BaseModel, Field


class Move(BaseModel):
    row: int = Field(description="Row index (0-2)")
    col: int = Field(description="Column index (0-2)")
    reason: str = Field(description="Brief justification for the move")


class MoveSet(BaseModel):
    moves: List[Move] = Field(description="Candidate moves in priority order")


class PathStep(BaseModel):
    player: str
    row: int
    col: int
    reason: str
    score_after: int  # score of the resulting state (always from O's perspective)
