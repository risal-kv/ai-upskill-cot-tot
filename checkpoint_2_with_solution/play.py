from __future__ import annotations
import asyncio
from typing import Set, Tuple

from .game import TicTacToe
from .llm import get_agent_move


async def play_tic_tac_toe(game: TicTacToe) -> str:
    """
    Play a complete tic-tac-toe game where Player A (X) is human input and Player B (O) is an AI agent.
    Player A (X) goes first, Player B (O) goes second.
    Returns the winner ('X', 'O') or 'Draw' if no winner.
    """
    available_positions: Set[Tuple[int, int]] = {(r, c) for r in range(3) for c in range(3)}
    current_player = 'X'  # Player A starts

    while available_positions:
        if current_player == 'X':
            # Human player input
            game.print_board()
            print(f"Player A ({current_player}), it's your turn!")
            while True:
                try:
                    row = int(input("Enter row (0-2): "))
                    col = int(input("Enter column (0-2): "))
                    if (row, col) in available_positions:
                        available_positions.remove((row, col))
                        won = game.make_move_x(row, col)
                        break
                    else:
                        print("Invalid move! Position already taken or out of bounds.")
                except ValueError:
                    print("Please enter valid integers for row and column.")
        else:
            # AI agent move
            row, col, reason = await get_agent_move(game, available_positions)
            available_positions.remove((row, col))
            won = game.make_move_o(row, col)
            print(f"Player B ({current_player}) plays at ({row}, {col})")
            print(f"Reasoning: {reason}")

        game.print_board()

        if won:
            return f"Player {'A' if current_player == 'X' else 'B'} ({current_player}) wins!"

        # Switch players
        current_player = 'O' if current_player == 'X' else 'X'

    return "Draw!"
