"""
ToTChecker for Tic-Tac-Toe using LangChain's ToT framework.
"""
from __future__ import annotations
import re
from typing import Tuple

from langchain_experimental.tot.checker import ToTChecker
from langchain_experimental.tot.thought import ThoughtValidity

from .game import TicTacToe
from .scoring import simple_score_state


class TicTacToeChecker(ToTChecker):
    """
    Checker that evaluates tic-tac-toe moves using the scoring from checkpoint_3.
    """
    
    def __init__(self, game: TicTacToe, player: str):
        super().__init__()
        # Store in private attributes to avoid Pydantic field issues
        self._game = game
        self._player = player
        self._opponent = 'X' if player == 'O' else 'O'
    
    def evaluate(
        self,
        problem_description: str,
        thoughts: Tuple[str, ...] = (),
    ) -> ThoughtValidity:
        """
        Evaluate a sequence of thoughts (moves) for tic-tac-toe.
        Returns VALID_FINAL if it leads to a win, VALID_INTERMEDIATE if it's legal,
        or INVALID if the move is illegal.
        """
        if not thoughts:
            return ThoughtValidity.INVALID
        
        try:
            # Start from current game state
            current_game = self._game.copy()
            current_player = self._player
            
            # Apply each thought as a move
            for thought in thoughts:
                # Parse the move from the thought
                row, col = self._parse_move(thought)
                
                # Check if move is legal
                if current_game.board[row][col] != '-':
                    print(f"[Checker] Move ({row},{col}) is illegal (cell occupied)")
                    return ThoughtValidity.INVALID
                
                # Apply move
                current_game = current_game.apply_move(row, col, current_player)
                
                # Check immediate result after each move
                if current_game.is_win(self._player):
                    # If this wins for us, it's a final solution!
                    print(f"[Checker] Move ({row},{col}) leads to WIN! Returning VALID_FINAL")
                    return ThoughtValidity.VALID_FINAL
                elif current_game.is_win(self._opponent):
                    # If this leads to opponent win, invalid
                    print(f"[Checker] Move ({row},{col}) leads to opponent win - INVALID")
                    return ThoughtValidity.INVALID
                
                # Alternate players for next thought
                current_player = self._opponent if current_player == self._player else self._player
            
            # After all thoughts, check final state
            if current_game.is_draw():
                return ThoughtValidity.VALID_INTERMEDIATE
            
            # Game continues - this is a valid intermediate state
            # Evaluate position strength using checkpoint_3's scoring
            score = simple_score_state(current_game.board, agent=self._player)
            
            # For single-move thoughts, be more accepting
            if len(thoughts) == 1:
                # Any legal move is at least valid intermediate
                print(f"[Checker] Single move is VALID_INTERMEDIATE (score: {score})")
                return ThoughtValidity.VALID_INTERMEDIATE
            
            # For multi-move sequences, require positive score
            if score >= 0:
                print(f"[Checker] Multi-move sequence is VALID_INTERMEDIATE (score: {score})")
                return ThoughtValidity.VALID_INTERMEDIATE
            else:
                print(f"[Checker] Multi-move sequence is VALID_INTERMEDIATE despite negative score ({score})")
                return ThoughtValidity.VALID_INTERMEDIATE  # Still valid, just not optimal
                    
        except Exception as e:
            # Log for debugging
            print(f"[Checker Error] {e}")
            return ThoughtValidity.INVALID
    
    def _parse_move(self, thought: str) -> Tuple[int, int]:
        """
        Parse move from thought string.
        Handles various formats including narrative thoughts from LLM.
        """
        thought_lower = thought.lower()
        
        # Look for (row, col) pattern in the text
        # Matches (0,2), (1, 1), etc.
        tuple_matches = re.findall(r'\((\d)\s*,\s*(\d)\)', thought)
        if tuple_matches:
            row, col = int(tuple_matches[0][0]), int(tuple_matches[0][1])
            print(f"[Checker] Parsed move ({row},{col}) from thought: {thought[:80]}...")
            return row, col
        
        # Look for "at (row,col)" or "position (row,col)"
        pos_matches = re.findall(r'(?:at|position)\s*\((\d)\s*,\s*(\d)\)', thought_lower)
        if pos_matches:
            row, col = int(pos_matches[0][0]), int(pos_matches[0][1])
            print(f"[Checker] Parsed move ({row},{col}) from thought: {thought[:80]}...")
            return row, col
        
        # Look for "row: X, col: Y" format
        if 'row' in thought_lower and 'col' in thought_lower:
            row_match = re.search(r'row[:\s]+(\d)', thought_lower)
            col_match = re.search(r'col[:\s]+(\d)', thought_lower)
            if row_match and col_match:
                row, col = int(row_match.group(1)), int(col_match.group(1))
                print(f"[Checker] Parsed move ({row},{col}) from thought: {thought[:80]}...")
                return row, col
        
        # Look for standalone "X,Y" pattern
        simple_matches = re.findall(r'\b(\d)\s*,\s*(\d)\b', thought)
        if simple_matches:
            row, col = int(simple_matches[0][0]), int(simple_matches[0][1])
            if 0 <= row < 3 and 0 <= col < 3:
                print(f"[Checker] Parsed move ({row},{col}) from thought: {thought[:80]}...")
                return row, col
        
        print(f"[Checker] Failed to parse thought: {thought[:80]}... Error: Cannot parse move from: {thought}")
        raise ValueError(f"Cannot parse move from: {thought}")

