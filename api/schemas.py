from __future__ import annotations
from typing import List, Literal, Optional
from pydantic import BaseModel, Field, model_validator


class MoveRequest(BaseModel):
    mode: Literal['cot', 'tot']
    # Frontend uses 1D board[0..8] with null, 'X', 'O'
    board: List[Optional[str]] = Field(min_length=9, max_length=9)
    player: Literal['X', 'O'] = 'O'  # AI plays as which mark
    beam: Optional[int] = None
    depth: Optional[int] = None

    @model_validator(mode='after')
    def _validate_board(self) -> 'MoveRequest':
        if len(self.board) != 9:
            raise ValueError('board must have 9 cells')
        for v in self.board:
            if v is not None and v not in {'X', 'O'}:
                raise ValueError("board cells must be null|'X'|'O'")
        return self


class CotResponse(BaseModel):
    mode: Literal['cot']
    move: int  # 0..8 index
    reasoning: str


class TreeNode(BaseModel):
    id: Optional[str] = None
    thought: str
    reason: str
    score: Optional[float] = None  # normalized 0..1 for UI percent
    children: Optional[List['TreeNode']] = None


class TotResponse(BaseModel):
    mode: Literal['tot']
    move: int  # 0..8 index
    reasoning: str
    tree: TreeNode


AiResponse = CotResponse | TotResponse 