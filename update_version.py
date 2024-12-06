#!/usr/bin/env python3
import contextlib
import sys
from pathlib import Path
from scripts.update_version import cli

# Add scripts directory to Python path
scripts_dir = Path(__file__).parent / "scripts"
sys.path.insert(0, str(scripts_dir))

if __name__ == "__main__":
    with contextlib.suppress(KeyboardInterrupt):
        cli()
