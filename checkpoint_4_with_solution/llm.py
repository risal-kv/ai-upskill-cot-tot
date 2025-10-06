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
    Use ToTChain to propose candidate moves for `player`.
    Returns a list[Move] ordered by quality.
    """
    board_str = ""
    for i, row in enumerate(game.board):
        board_str += f"Row {i}: {' '.join(row)}\n"

    avail_sorted = sorted(list(available_positions))
    available_str = ", ".join([f"({r},{c})" for r, c in avail_sorted]) if avail_sorted else "none"

    # Create problem description for ToTChain
    problem = dedent(f"""
        You are playing tic-tac-toe as player {player}.
        Current board:
        {board_str}
        Legal (available) positions: {available_str}

        Your goal is to find the best move. Consider:
        1. Can you win in the next move?
        2. Do you need to block the opponent from winning?
        3. Which moves create the most strategic advantage?

        Propose your next move in the format: (row, col) where row and col are 0, 1, or 2.
        For example: "Place {player} at (1,1) to control the center"
    """).strip()

    key = api_key or OPENAI_API_KEY or os.environ.get("OPENAI_API_KEY")
    if not key:
        dbg(0, "[LLM] No API key; returning empty proposal list.")
        return []

    try:
        # Create LLM and checker
        llm = ChatOpenAI(model=model_name, api_key=key, temperature=0.7)
        checker = TicTacToeChecker(game, player)
        
        # Create ToTChain with c=3 (generate 3 thoughts per step)
        tot_chain = ToTChain(
            llm=llm,
            checker=checker,
            c=3,  # number of thoughts to generate
            k=5,  # max iterations
            verbose=VERBOSE
        )
        
        if VERBOSE:
            dbg(0, f"[LLM-ToT] Using ToTChain to propose moves for {player}")
        
        # Run ToT reasoning
        result = tot_chain.invoke({"problem_description": problem})
        
        # Extract moves from ToT result
        response_text = result.get("response", "")
        
        if response_text == "No solution found":
            # ToTChain didn't find a complete solution, but we can still use intermediate moves
            # Fall back to generating moves with regular LLM
            if VERBOSE:
                dbg(0, f"[LLM-ToT] No solution found by ToTChain, falling back to structured output")
            return await _fallback_move_generation(game, available_positions, player, model_name, key)
        
        # Parse the move from the response
        moves = _parse_moves_from_text(response_text, available_positions)
        
        if VERBOSE:
            dbg(0, f"[LLM-ToT] Extracted {len(moves)} moves from ToT result")
        
        return moves[:VERBOSE_PROPOSALS_MAX]
        
    except Exception as e:
        if VERBOSE:
            dbg(0, f"[LLM-ToT] Error: {e}, falling back to structured output")
        





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
