from __future__ import annotations
import asyncio
from typing import Optional, List

from .config import (
    SHOW_ASCII_TREE_EACH_AGENT_MOVE,
    SHOW_DOT_EACH_AGENT_MOVE,
    SEARCH_MAX_DEPTH,
    dbg,
)
from .game import TicTacToe
from .tree import ThoughtTree
from .scoring import simple_score_state
from .search import find_best_path_with_tree


async def agent_move_with_tree(
    game: TicTacToe,
    beam_width: int = 2,
    max_depth: int = SEARCH_MAX_DEPTH,
    api_key: Optional[str] = None,
) -> None:
    """
    Build a fresh tree from the current state, choose the first step of the best path, and play it.
    """
    # Initialize tree with current state's heuristic score
    start_score = simple_score_state(game.board, agent="O")
    tree = ThoughtTree()
    root_id = tree.add_root(score_after=start_score)

    # Compute best path from current state assuming 'O' to move
    best_score, best_path = await find_best_path_with_tree(
        game,
        to_move="O",
        tree=tree,
        parent_node_id=root_id,
        beam_width=beam_width,
        max_depth=max_depth,
        api_key=api_key,
    )

    if SHOW_ASCII_TREE_EACH_AGENT_MOVE:
        print("\n=== Thought Tree (ASCII) ===")
        print(tree.pretty())

    if SHOW_DOT_EACH_AGENT_MOVE:
        print("\n=== Graphviz DOT ===")
        print(tree.to_dot())

    # Take the first step on the best path if available
    if not best_path:
        dbg(0, "[Agent] No path found; skipping move.")
        return

    step = best_path[0]
    won = game.make_move('O', step.row, step.col)
    print(f"Agent (O) plays ({step.row},{step.col}). Reason: {step.reason}")
    game.print_board()
    if won:
        print("Agent (O) wins!")


def play_interactive(
    beam_width: int = 2,
    max_depth: int = SEARCH_MAX_DEPTH,
):
    """
    Human (X) vs Agent (O) using the tree search for agent turns.
    """
    game = TicTacToe()
    game.print_board()

    while True:
        # Human move
        try:
            raw = input("Your move as X (format: r c), or 'q' to quit: ").strip()
            if raw.lower() in {"q", "quit", "exit"}:
                print("Goodbye!")
                break
            r_s, c_s = raw.split()
            r, c = int(r_s), int(c_s)
        except Exception:
            print("Invalid input. Please enter two integers 0..2, e.g. '1 2'.")
            continue

        if game.board[r][c] != '-':
            print("Cell is occupied. Try again.")
            continue

        human_won = game.make_move('X', r, c)
        game.print_board()
        if human_won:
            print("You (X) win! 🎉")
            break
        if game.is_draw():
            print("It's a draw.")
            break

        # Agent move
        asyncio.run(agent_move_with_tree(game, beam_width=beam_width, max_depth=max_depth))
        if game.is_win('O'):
            break
        if game.is_draw():
            print("It's a draw.")
            break
