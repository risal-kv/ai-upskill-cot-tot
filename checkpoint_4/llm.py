from __future__ import annotations
import os
import re
from typing import List, Set, Tuple, Optional, cast
from textwrap import dedent

from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from langchain_experimental.tot.base import ToTChain

from .config import OPENAI_API_KEY, OPENAI_MODEL, VERBOSE, VERBOSE_PROPOSALS_MAX, dbg
from .game import TicTacToe
from .schemas import Move, MoveSet
from .tot_checker import TicTacToeChecker

from dotenv import load_dotenv

load_dotenv()  # take environment variables from .env.


async def create_thoughts(
    game: TicTacToe,
    available_positions: Set[Tuple[int, int]],
    player: str,  # "O" (agent) or "X" (user)
    model_name: str = OPENAI_MODEL,
    api_key: Optional[str] = None,
) -> List[Move]:
    """
    Use the LLM to propose candidate moves for `player`.
    Returns a list[Move] ordered by the model's priority (best-first).
    """
    board_str = ""
    for i, row in enumerate(game.board):
        board_str += f"Row {i}: {' '.join(row)}\n"

    avail_sorted = sorted(list(available_positions))
    available_str = ", ".join([f"({r},{c})" for r, c in avail_sorted]) if avail_sorted else "none"

    prompt = dedent(f"""
        You are playing tic-tac-toe as player {player}.
        Current board:
        {board_str}
        Legal (available) positions: {available_str}

        Produce a list of distinct candidate moves that are legal (must exist in the available set).
        Return JSON only in this exact shape:
        {{
          "moves": [
            {{"row": int, "col": int, "reason": "brief justification"}},
            ...
          ]
        }}

        Guidelines:
        - If there is an immediate winning move for {player}, include it first.
        - Else, include any necessary blocks against the opponent's immediate win.
        - Otherwise, include strong strategic moves (center, forks, corners, edges).
        - Do not repeat positions; keep the list concise and ordered (best-first).
    """).strip()

    key = api_key or OPENAI_API_KEY or os.environ.get("OPENAI_API_KEY")
    if not key:
        # No key? Return empty list; caller will fall back to enumerating legal moves.
        print("Debugging here ", os.environ.get("OPENAI_API_KEY"))
        dbg(0, "[LLM] No API key; returning empty proposal list.")
        return []

    llm = ChatOpenAI(model=model_name, api_key=key)
    structured_llm = llm.with_structured_output(MoveSet)

    response = cast(MoveSet, await structured_llm.ainvoke([HumanMessage(content=prompt)]))
    if VERBOSE:
        dbg(0, f"[LLM] Proposed {len(response.moves)} moves for {player} (pre-filter).")

    # Filter out any illegal positions, just in case
    legal_moves = [m for m in response.moves if (m.row, m.col) in available_positions]
    # Deduplicate while keeping order
    seen = set()
    unique: List[Move] = []
    for m in legal_moves[: VERBOSE_PROPOSALS_MAX]:
        k = (m.row, m.col)
        if k not in seen:
            seen.add(k)
            unique.append(m)

    if VERBOSE:
        dbg(0, f"[LLM] Using {len(unique)} legal & unique moves for {player}.")
    return unique


def _parse_moves_from_text(text: str, available_positions: Set[Tuple[int, int]]) -> List[Move]:
    """
    Parse move coordinates from text response.
    Looks for patterns like (row, col) or "row X, col Y"
    """
    moves: List[Move] = []
    
    # Look for (row, col) pattern
    tuple_matches = re.findall(r'\((\d)\s*,\s*(\d)\)', text)
    for row_str, col_str in tuple_matches:
        row, col = int(row_str), int(col_str)
        if (row, col) in available_positions:
            # Extract some context around this coordinate for the reason
            idx = text.find(f"({row},{col})")
            if idx == -1:
                idx = text.find(f"({row}, {col})")
            
            # Get surrounding text as reason
            start = max(0, idx - 50)
            end = min(len(text), idx + 100)
            reason = text[start:end].strip()
            
            moves.append(Move(row=row, col=col, reason=reason))
    
    # Look for "row: X, col: Y" pattern
    row_col_matches = re.findall(r'row[:\s]+(\d).*?col[:\s]+(\d)', text.lower())
    for row_str, col_str in row_col_matches:
        row, col = int(row_str), int(col_str)
        if (row, col) in available_positions and (row, col) not in [(m.row, m.col) for m in moves]:
            reason = f"Move at row {row}, col {col}"
            moves.append(Move(row=row, col=col, reason=reason))
    
    # If no moves found, return empty list (caller will handle fallback)
    return moves
