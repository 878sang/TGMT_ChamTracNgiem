"""Load the active answer-sheet layout."""

import json
import os
from functools import lru_cache
from typing import Any


PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LAYOUTS_DIR = os.path.join(PROJECT_ROOT, "templates", "layouts")
ACTIVE_LAYOUT_NAME = "thpt50"


@lru_cache(maxsize=8)
def load_layout(layout_name: str = ACTIVE_LAYOUT_NAME) -> dict[str, Any]:
    path = os.path.join(LAYOUTS_DIR, f"{layout_name}.json")
    try:
        with open(path, encoding="utf-8") as layout_file:
            layout = json.load(layout_file)
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(f"Cannot load layout '{layout_name}' from {path}: {error}") from error

    required = ("canvas_w", "canvas_h", "capacity", "markers", "blocks", "id_blocks")
    missing = [key for key in required if key not in layout]
    if missing:
        raise ValueError(f"Layout '{layout_name}' is missing required fields: {missing}")
    return layout
