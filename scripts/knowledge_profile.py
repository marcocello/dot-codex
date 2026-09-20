#!/usr/bin/env python3
"""Compatibility launcher; knowledge-tool-connect owns all profile logic."""
from pathlib import Path
import runpy

if __name__ == "__main__":
    runpy.run_path(str(Path(__file__).resolve().parents[1] / "skills/knowledge-tool-connect/scripts/knowledge_profile.py"), run_name="__main__")
