from __future__ import annotations
from typing import List, Optional, Set, Tuple, cast

from .config import SEARCH_MAX_DEPTH, OPENAI_MODEL, dbg
from .game import TicTacToe
from .schemas import Move, PathStep
from .scoring import simple_score_state
from .tree import ThoughtTree
from .llm import create_thoughts


async def find_best_path_with_tree(
    game: TicTacToe,
    to_move: str,  # "O" or "X"
    tree: ThoughtTree,
    parent_node_id: int,
    model_name: str = OPENAI_MODEL,
    api_key: Optional[str] = None,
    beam_width: int = 2,
    max_depth: int = SEARCH_MAX_DEPTH,
    depth: int = 0,
) -> tuple[int, List[PathStep]]:
    """
    - Scores are ALWAYS from O's perspective.
    - O-turns: keep top `beam_width` HIGHEST scores.
    - X-turns: keep top `beam_width` LOWEST scores.
    """
    node = tree.nodes[parent_node_id]
    dbg(depth, f"↳ Explore node #{node.id} (depth={depth}/{max_depth}, to_move={to_move}) | score_here={node.score_after}")

    # Terminal check
    if game.is_win('O'):
        node.terminal = True
        node.outcome = "O"
        dbg(depth, f"  ⛳ Terminal: O wins here.")
        return 100, []
    if game.is_win('X'):
        node.terminal = True
        node.outcome = "X"
        dbg(depth, f"  ⛔ Terminal: X wins here.")
        return -100, []
    if game.is_draw():
        node.terminal = True
        node.outcome = "draw"
        dbg(depth, f"  ⏹️ Terminal: draw.")
        return 0, []
    if depth >= max_depth:
        dbg(depth, f"  🪓 Depth cutoff at {max_depth}. Returning heuristic={node.score_after}")
        return node.score_after, []

    legal = game.available_positions()
    if not legal:
        dbg(depth, f"  ⚠️ No legal moves. Returning 0.")
        return 0, []

    # Get proposals from LLM
    proposals: List[Move] = await create_thoughts(game, legal, player=to_move, model_name=model_name, api_key=api_key)

    # Fallback: enumerate all legal moves if LLM returned nothing
    if not proposals:
        dbg(depth, f"  [fallback] Enumerating {len(legal)} legal moves.")
        proposals = [Move(row=r, col=c, reason="fallback: legal move") for (r, c) in sorted(legal)]

    # Score each candidate (always O's perspective), create child node in tree
    entries: List[tuple[Move, int, TicTacToe, int]] = []
    for m in proposals:
        next_state = game.apply_move(m.row, m.col, to_move)
        s = simple_score_state(next_state.board, agent="O")
        terminal = next_state.is_win('O') or next_state.is_win('X') or next_state.is_draw()
        outcome = "O" if next_state.is_win('O') else ("X" if next_state.is_win('X') else ("draw" if next_state.is_draw() else None))
        child_id = tree.add_child(parent_node_id, player=to_move, r=m.row, c=m.col, reason=m.reason, score_after=s, terminal=terminal, outcome=outcome)
        entries.append((m, s, next_state, child_id))

    # Beam selection
    if to_move == 'O':
        # keep highest scores
        entries.sort(key=lambda t: t[1], reverse=True)
    else:
        # X tries to minimize O's score
        entries.sort(key=lambda t: t[1])
    entries = entries[:beam_width]

    # Recurse
    best_score = None
    best_path: List[PathStep] = []

    for m, s, next_state, child_id in entries:
        score_down, path_down = await find_best_path_with_tree(
            next_state,
            to_move=('X' if to_move == 'O' else 'O'),
            tree=tree,
            parent_node_id=child_id,
            model_name=model_name,
            api_key=api_key,
            beam_width=beam_width,
            max_depth=max_depth,
            depth=depth + 1,
        )
        # For O, we maximize; for X, we minimize (still scoring from O's perspective)
        overall_score = score_down
        if best_score is None:
            best_score = overall_score
            best_path = [PathStep(player=to_move, row=m.row, col=m.col, reason=m.reason, score_after=s)] + path_down
        else:
            better = (to_move == 'O' and overall_score > best_score) or (to_move == 'X' and overall_score < best_score)
            if better:
                best_score = overall_score
                best_path = [PathStep(player=to_move, row=m.row, col=m.col, reason=m.reason, score_after=s)] + path_down

    assert best_score is not None
    return cast(int, best_score), best_path
