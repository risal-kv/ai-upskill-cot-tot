from __future__ import annotations
import argparse

from checkpoint_3.config import SEARCH_MAX_DEPTH
from checkpoint_3.play import play_interactive


def main():
    parser = argparse.ArgumentParser(description="Tic-Tac-Toe with Thought Tree (modular)")
    parser.add_argument("--beam", type=int, default=2, help="Beam width for search (default: 2)")
    parser.add_argument("--depth", type=int, default=SEARCH_MAX_DEPTH, help="Max search depth (default: from config)")
    args = parser.parse_args()

    play_interactive(beam_width=args.beam, max_depth=args.depth)


if __name__ == "__main__":
    main()
