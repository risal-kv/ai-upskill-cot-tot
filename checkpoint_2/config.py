# Central configuration and debug utilities for checkpoint_2
from __future__ import annotations

import os
from typing import Any

from dotenv import load_dotenv

load_dotenv()

OPENAI_MODEL = "gpt-4o-mini"
# Prefer env var; do NOT hardcode a key in modular code
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
VERBOSE = True


def dbg(*msg: Any) -> None:
    if VERBOSE:
        print(" ".join(str(m) for m in msg))
