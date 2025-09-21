from __future__ import annotations
from textwrap import dedent
from typing import Optional, Set, Tuple, cast

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

from .config import OPENAI_API_KEY, OPENAI_MODEL, dbg
from .game import TicTacToe
from .schemas import Move


async def get_agent_move(game: TicTacToe, available_positions: Set[Tuple[int, int]], api_key: Optional[str] = None) -> tuple[int, int, str]:
    """
    Use OpenAI to predict the next move for the agent.
    Returns a tuple (row, col, reason) representing the agent's move.
    """
    # Create board state description
    board_str = ""
    for i, row in enumerate(game.board):
        board_str += f"Row {i}: {' '.join(row)}\n"

    available_str = ", ".join([f"({r},{c})" for r, c in sorted(available_positions)])

    prompt = dedent(f"""
        You are playing tic-tac-toe as player O. 
        Current board state:
        {board_str}
        Available positions: {available_str}

        Think step by step:
        1. Analyze the current board state
        2. Check if you can win in one move
        3. Check if you need to block the opponent from winning
        4. Otherwise, choose the best strategic position

        Choose your next move. Return row and col as integers (0-2).
    """).strip()

    dbg("[LLM prompt]\n", prompt)

    key = api_key or OPENAI_API_KEY
    if not key:
        raise RuntimeError("OPENAI_API_KEY is not set. Please set it in the environment.")

    llm = ChatOpenAI(model=OPENAI_MODEL, api_key=key)
    structured_llm = llm.with_structured_output(Move)

    response = cast(Move, await structured_llm.ainvoke([HumanMessage(content=prompt)]))
    return response.row, response.col, response.reason
