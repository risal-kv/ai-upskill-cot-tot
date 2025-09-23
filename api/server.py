from __future__ import annotations
import os
from typing import List, Optional, Set, Tuple

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

from api.schemas import MoveRequest, CotResponse, TotResponse, TreeNode

# Load env
load_dotenv()

app = FastAPI(title="TicTacToe AI API", version="1.0.0")

# Configure CORS (adjust origins as needed)
origins_env = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:5173")
origins = [o.strip() for o in origins_env.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Utilities to convert between representations ---

def board1d_to_matrix(board: List[Optional[str]]) -> List[List[str]]:
    def cell(v: Optional[str]) -> str:
        return '-' if v is None else v
    return [
        [cell(board[0]), cell(board[1]), cell(board[2])],
        [cell(board[3]), cell(board[4]), cell(board[5])],
        [cell(board[6]), cell(board[7]), cell(board[8])],
    ]


def pos_to_index(r: int, c: int) -> int:
    return r * 3 + c


def available_positions_from_matrix(board: List[List[str]]) -> Set[Tuple[int, int]]:
    positions: Set[Tuple[int, int]] = {(r, c) for r in range(3) for c in range(3) if board[r][c] == '-'}
    print("[API] available_positions:", sorted(positions))
    return positions


# --- CoT adapter ---
from checkpoint_2.game import TicTacToe as TTT2
from checkpoint_2.llm import get_agent_move

async def run_cot(board_1d: List[Optional[str]], player: str) -> CotResponse:
    game = TTT2()
    game.board = board1d_to_matrix(board_1d)
    avail = available_positions_from_matrix(game.board)
    r, c, reason = await get_agent_move(game, avail)
    move_idx = pos_to_index(r, c)
    return CotResponse(mode='cot', move=move_idx, reasoning=reason)


# --- ToT adapter ---
from checkpoint_3.game import TicTacToe as TTT3
from checkpoint_3.scoring import simple_score_state
from checkpoint_3.tree import ThoughtTree, ThoughtNode
from checkpoint_3.search import find_best_path_with_tree


def normalize_score(score_after: int) -> float:
    # map rough [-100..100] to [0..1]
    v = (score_after + 100.0) / 200.0
    if v < 0.0:
        return 0.0
    if v > 1.0:
        return 1.0
    return v


def node_to_treenode(tree: ThoughtTree, nid: int) -> TreeNode:
    n = tree.nodes[nid]
    if n.r is None or n.c is None:
        thought = "root"
    else:
        thought = f"{n.player}→({n.r},{n.c})"
        if n.terminal and n.outcome:
            thought += f" [terminal: {n.outcome}]"
    score = n.score_after if isinstance(n.score_after, (int, float)) else None
    children = [node_to_treenode(tree, cid) for cid in n.children] if n.children else []
    return TreeNode(
        id=str(n.id),
        thought=thought,
        reason=n.reason or "",
        score=score,
        children=children or None,
    )


async def run_tot(board_1d: List[Optional[str]], player: str, beam: Optional[int], depth: Optional[int]) -> TotResponse:
    game = TTT3()
    game.board = board1d_to_matrix(board_1d)

    # Seed tree with current state's heuristic (always score from O's perspective in scoring)
    start_score = simple_score_state(game.board, agent="O")
    tree = ThoughtTree()
    root_id = tree.add_root(score_after=start_score)

    best_score, best_path = await find_best_path_with_tree(
        game,
        to_move=player,
        tree=tree,
        parent_node_id=root_id,
        beam_width=beam or 2,
        max_depth=depth or 2,
    )

    # Take first step as move
    if not best_path:
        raise HTTPException(status_code=400, detail="No path found by ToT search")
    first = best_path[0]
    move_idx = pos_to_index(first.row, first.col)

    # Serialize thought tree to UI TreeNode
    ui_tree = node_to_treenode(tree, tree.root_id) if tree.root_id is not None else TreeNode(thought='root', reason='', children=[])

    # Derive a summary reasoning (optional): use top step's reason
    reasoning = first.reason or ""

    return TotResponse(mode='tot', move=move_idx, reasoning=reasoning, tree=ui_tree)


@app.get("/healthz")
async def healthz():
    return {"ok": True}


@app.post("/api/v1/move")
async def move(req: MoveRequest):
    if req.mode == 'cot':
        return await run_cot(req.board, player=req.player)
    elif req.mode == 'tot':
        return await run_tot(req.board, player=req.player, beam=req.beam, depth=req.depth)
    else:
        raise HTTPException(status_code=400, detail="Invalid mode") 