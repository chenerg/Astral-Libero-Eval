#!/usr/bin/env python3
"""Rebuild viz/ when any run transcript/result/ctrl log is newer than data.js."""
import sys
import time
from pathlib import Path

VIZ = Path(__file__).resolve().parent
sys.path.insert(0, str(VIZ))
from build import is_stale, main as build_main  # noqa: E402


def main() -> None:
    while True:
        if is_stale():
            print("viz: runs changed, rebuilding", flush=True)
            try:
                build_main(["--no-win"])
            except Exception as exc:
                print("viz: build failed", exc, flush=True)
        time.sleep(20)


if __name__ == "__main__":
    main()

