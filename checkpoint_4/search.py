from __future__ import annotations
from typing import List, Optional, Tuple, cast

from .config import SEARCH_MAX_DEPTH, OPENAI_MODEL, dbg
from .game import TicTacToe
from .schemas import Move, PathStep
from .scoring import simple_score_state
from .tree import ThoughtTree
from .llm import create_thoughts


# ---------------------------
# Helper functions (no recursion)
# ---------------------------

def _evaluate_terminal(game: TicTacToe, node) -> Optional[Tuple[int, List[PathStep]]]:
    """
    If the current game state is terminal, mark the node and return the score (from O's perspective).
    Otherwise return None.
    """
    if game.is_win('O'):
        node.terminal = True
        node.outcome = "O"
        dbg(0, f"  ⛳ Terminal: O wins here.")
        return 100, []
    if game.is_win('X'):
        node.terminal = True
        node.outcome = "X"
        dbg(0, f"  ⛔ Terminal: X wins here.")
        return -100, []
    if game.is_draw():
        node.terminal = True
        node.outcome = "draw"
        dbg(0, f"  ⏹️ Terminal: draw.")
        return 0, []
    return None


def _depth_cutoff(depth: int, max_depth: int, node_score_after: int) -> Optional[Tuple[int, List[PathStep]]]:
    """
    If search depth reached, return the heuristic score; otherwise None.
    """
    if depth >= max_depth:
        dbg(depth, f"  🪓 Depth cutoff at {max_depth}. Returning heuristic={node_score_after}")
        return node_score_after, []
    return None


async def _fetch_proposals(
    game: TicTacToe,
    legal: List[Tuple[int, int]],
    to_move: str,
    model_name: str,
    api_key: Optional[str],
) -> List[Move]:
    """
    Ask the LLM for candidate moves; if none, fall back to enumerating legal moves.
    """
    proposals: List[Move] = await create_thoughts(game, legal, player=to_move, model_name=model_name, api_key=api_key)
    if not proposals:
        dbg(0, f"  [fallback] Enumerating {len(legal)} legal moves.")
        proposals = [Move(row=r, col=c, reason="fallback: legal move") for (r, c) in sorted(legal)]
    return proposals


def _score_and_expand_children(
    game: TicTacToe,
    proposals: List[Move],
    to_move: str,
    tree: ThoughtTree,
    parent_node_id: int,
) -> List[tuple[Move, int, TicTacToe, int]]:
    """
    For each proposal, apply the move, score from O's perspective, mark terminal/outcome,
    and add a child node to the tree. Return a list of (move, score, next_state, child_id).
    """
    entries: List[tuple[Move, int, TicTacToe, int]] = []
    for m in proposals:
        next_state = game.apply_move(m.row, m.col, to_move)
        s = simple_score_state(next_state.board, agent="O")
        terminal = next_state.is_win('O') or next_state.is_win('X') or next_state.is_draw()
        outcome = (
            "O" if next_state.is_win('O')
            else ("X" if next_state.is_win('X')
                  else ("draw" if next_state.is_draw() else None))
        )
        child_id = tree.add_child(
            parent_node_id,
            player=to_move,
            r=m.row,
            c=m.col,
            reason=m.reason,
            score_after=s,
            terminal=terminal,
            outcome=outcome,
        )
        entries.append((m, s, next_state, child_id))
    return entries


def _beam_select(
    entries: List[tuple[Move, int, TicTacToe, int]],
    to_move: str,
    beam_width: int,
) -> List[tuple[Move, int, TicTacToe, int]]:
    """
    Keep top-k by score depending on player:
      - O keeps highest scores
      - X keeps lowest scores
    """
    if to_move == 'O':
        entries.sort(key=lambda t: t[1], reverse=True)
    else:
        entries.sort(key=lambda t: t[1])
    return entries[:beam_width]


# ---------------------------
# Main (recursion preserved)
# ---------------------------

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

    # 1) Terminal-state handling (uses _evaluate_terminal)
    terminal_eval = _evaluate_terminal(game, node)
    if terminal_eval is not None:
        return terminal_eval

    # 2) Depth cutoff check (uses _depth_cutoff)
    cutoff_eval = _depth_cutoff(depth, max_depth, node.score_after)
    if cutoff_eval is not None:
        return cutoff_eval

    # 3) Legal moves retrieval
    legal = game.available_positions()
    if not legal:
        dbg(depth, f"  ⚠️ No legal moves. Returning 0.")
        return 0, []

    # 4) Candidate generation (uses _fetch_proposals)
    proposals: List[Move] = await _fetch_proposals(
        game=game,
        legal=legal,
        to_move=to_move,
        model_name=model_name,
        api_key=api_key,
    )

    # 5) Scoring and child-node expansion (uses _score_and_expand_children)
    entries = _score_and_expand_children(
        game=game,
        proposals=proposals,
        to_move=to_move,
        tree=tree,
        parent_node_id=parent_node_id,
    )

    # 6) Beam selection (uses _beam_select)
    entries = _beam_select(entries, to_move=to_move, beam_width=beam_width)

    # 7) Recurse into selected children (recursion remains here)
    best_score: Optional[int] = None
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
        overall_score = score_down  # already from O's perspective

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