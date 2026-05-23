from __future__ import annotations

import sys
from pathlib import Path


APP_DIR = Path(__file__).resolve().parent / "plast_alum_manager"
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

from main import main as run_app  # noqa: E402


if __name__ == "__main__":
    raise SystemExit(run_app())
