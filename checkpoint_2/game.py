from __future__ import annotations
from typing import List


class TicTacToe:
    def __init__(self):
        # 3x3 grid initialized with '-'
        self.board: List[List[str]] = [['-' for _ in range(3)] for _ in range(3)]

    def print_board(self) -> None:
        """Pretty-print the board to the terminal."""
        print("-------CURRENT STATE-------")
        for row in self.board:
            print(' '.join(row))
        # Optional spacer
        print("---------------------------")

    def make_move_x(self, row: int, col: int) -> bool:
        """
        Place 'X' at (row, col) if valid, then return True if that move wins the game, else False.
        If the move is invalid (out of bounds or cell occupied), returns False and does nothing.
        """
        return self._make_move('X', row, col)

    def make_move_o(self, row: int, col: int) -> bool:
        """
        Place 'O' at (row, col) if valid, then return True if that move wins the game, else False.
        If the move is invalid (out of bounds or cell occupied), returns False and does nothing.
        """
        return self._make_move('O', row, col)

    # --- Internal helpers ---

    def _make_move(self, player: str, row: int, col: int) -> bool:
        if not (0 <= row < 3 and 0 <= col < 3):
            return False  # out of bounds
        if self.board[row][col] != '-':
            return False  # already occupied

        self.board[row][col] = player
        return self._check_win(player)

    def _check_win(self, player: str) -> bool:
        b = self.board

        # Rows
        for r in range(3):
            if all(b[r][c] == player for c in range(3)):
                return True

        # Columns
        for c in range(3):
            if all(b[r][c] == player for r in range(3)):
                return True

        # Diagonals
        if all(b[i][i] == player for i in range(3)):
            return True
        if all(b[i][2 - i] == player for i in range(3)):
            return True

        return False
