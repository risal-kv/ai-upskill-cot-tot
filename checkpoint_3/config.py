# Central configuration and debug utilities
from __future__ import annotations

import os
from typing import Any

# =========================
# CONFIG (toggle prints)
# =========================
SHOW_ASCII_TREE_EACH_AGENT_MOVE = True
SHOW_DOT_EACH_AGENT_MOVE = False  # set True if you want DOT printed too
OPENAI_MODEL = "gpt-4o-mini"
# Prefer env var; do NOT hardcode a key in the modularized code
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
VERBOSE = True  # master verbosity switch
VERBOSE_PROPOSALS_MAX = 100  # print at most this many proposals per node
SEARCH_MAX_DEPTH = 2  # configurable search depth

# Visualization config (optional consumers)
RENDER_NX_EACH_AGENT_MOVE = False
RENDER_FINAL_GRAPH = False
VIZ_OUTPUT_DIR = "viz_out"
VIZ_BASENAME = "thought_tree"
VIZ_DPI = 220
VIZ_FIGSIZE = (11, 8.5)
VIZ_LAYOUT = "dot"  # "dot" (requires pygraphviz) or "spring"


def dbg(depth: int, *msg: Any) -> None:
    """Depth-indented debug print, governed by VERBOSE."""
    if VERBOSE:
        indent = "│   " * depth
        print(f"{indent}{' '.join(str(m) for m in msg)}")
