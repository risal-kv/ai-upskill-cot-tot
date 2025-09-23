from __future__ import annotations
import argparse
import asyncio

from checkpoint_2.play import play_tic_tac_toe
from checkpoint_2.game import TicTacToe

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

import os
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

def main():
    parser = argparse.ArgumentParser(description="Tic-Tac-Toe (checkpoint_2 modular)")
    _ = parser.parse_args()  # reserved for future flags

    game = TicTacToe()
    result = asyncio.run(play_tic_tac_toe(game))
    print("Result:", result)


if __name__ == "__main__":
    main()
