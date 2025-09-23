from __future__ import annotations
from typing import List, Set, Tuple

class TicTacToe:
    """Simple 3x3 Tic-Tac-Toe board with '-', 'X', 'O'."""
    def __init__(self):
        self.board: List[List[str]] = [['-' for _ in range(3)] for _ in range(3)]

    def copy(self) -> "TicTacToe":
        g = TicTacToe()
        g.board = [row[:] for row in self.board]
        return g

    def print_board(self) -> None:
        print("\n------- CURRENT STATE -------")
        for row in self.board:
            print(' '.join(row))
        print("-----------------------------\n")

    def available_positions(self) -> Set[Tuple[int, int]]:
        return {(r, c) for r in range(3) for c in range(3) if self.board[r][c] == '-'}

    def is_win(self, p: str) -> bool:
        b = self.board
        # rows/cols
        for i in range(3):
            if all(b[i][c] == p for c in range(3)): return True
            if all(b[r][i] == p for r in range(3)): return True
        # diagonals
        if all(b[i][i] == p for i in range(3)): return True
        if all(b[i][2 - i] == p for i in range(3)): return True
        return False

    def is_draw(self) -> bool:
        return all(c != '-' for r in range(3) for c in self.board[r]) and not self.is_win('X') and not self.is_win('O')

    def apply_move(self, r: int, c: int, player: str) -> "TicTacToe":
        if not (0 <= r < 3 and 0 <= c < 3):
            raise ValueError("Out of bounds")
        if self.board[r][c] != '-':
            raise ValueError("Cell occupied")
        g = self.copy()
        g.board[r][c] = player
        return g

    def make_move(self, player: str, r: int, c: int) -> bool:
        """Mutates board; returns True if this move wins."""
        if not (0 <= r < 3 and 0 <= c < 3): return False
        if self.board[r][c] != '-': return False
        self.board[r][c] = player
        return self.is_win(player)

    def make_move_x(self, r: int, c: int) -> bool:
        return self.make_move('X', r, c)

    def make_move_o(self, r: int, c: int) -> bool:
        return self.make_move('O', r, c)
