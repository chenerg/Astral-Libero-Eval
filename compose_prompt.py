#!/usr/bin/env python3
"""Build PROMPT.txt from PROMPT_BASE.txt + LESSONS.md."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent
base = (ROOT / "PROMPT_BASE.txt").read_text()
lessons = (ROOT / "LESSONS.md").read_text()
if "{{LESSONS}}" not in base:
    raise SystemExit("PROMPT_BASE.txt missing {{LESSONS}} placeholder")
(ROOT / "PROMPT.txt").write_text(base.replace("{{LESSONS}}", lessons.rstrip() + "\n"))
print("wrote", ROOT / "PROMPT.txt")
