#!/usr/bin/env python3
"""Source-checkout launcher for DriveForge."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from driveforge.cli import main  # noqa: E402

raise SystemExit(main())
