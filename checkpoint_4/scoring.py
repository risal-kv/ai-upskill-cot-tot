from __future__ import annotations
from typing import List


def simple_score_state(board: List[List[str]], agent: str = "O") -> int:
    """
    Simple heuristic score for a Tic-Tac-Toe position from `agent`'s perspective.
    Higher is better for `agent`. Cells are 'X', 'O', or '-'.
    """
    opp = "X" if agent == "O" else "O"

    def lines(bd):
        return (
            [[bd[r][0], bd[r][1], bd[r][2]] for r in range(3)]
            + [[bd[0][c], bd[1][c], bd[2][c]] for c in range(3)]
            + [[bd[0][0], bd[1][1], bd[2][2]], [bd[0][2], bd[1][1], bd[2][0]]]
        )

    def is_win(bd, p):
        return any(L.count(p) == 3 for L in lines(bd))

    # Terminal dominance
    if is_win(board, agent):
        return 100
    if is_win(board, opp):
        return -100

    score = 0

    # Center / corners / edges
    if board[1][1] == agent:
        score += 3
    elif board[1][1] == opp:
        score -= 3

    for r, c in [(0, 0), (0, 2), (2, 0), (2, 2)]:
        if board[r][c] == agent:
            score += 2
        elif board[r][c] == opp:
            score -= 2

    for r, c in [(0, 1), (1, 0), (1, 2), (2, 1)]:
        if board[r][c] == agent:
            score += 1
        elif board[r][c] == opp:
            score -= 1

    # Immediate threats (two-in-a-row with one empty)
    for L in lines(board):
        if L.count(agent) == 2 and L.count("-") == 1:
            score += 5
        if L.count(opp) == 2 and L.count("-") == 1:
            score -= 6

    return score
