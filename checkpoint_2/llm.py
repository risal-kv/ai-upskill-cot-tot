from __future__ import annotations
import random
from textwrap import dedent
from typing import Optional, Set, Tuple, cast

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

from .config import OPENAI_API_KEY, OPENAI_MODEL, dbg
from .game import TicTacToe
from .schemas import Move


async def get_agent_move(game: TicTacToe, available_positions: Set[Tuple[int, int]], api_key: Optional[str] = None) -> tuple[int, int, str]:
    """
    Select a random move from available positions and return (row, col, reason).
    """

    if not available_positions:
        raise RuntimeError("No available positions to choose from")

    # TODO: Implement the get_agent_move function

    row, col = random.choice(sorted(list(available_positions)))
    reason = "Randomly generated position"
    return row, col, reason
