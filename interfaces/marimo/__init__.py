import subprocess
import sys
from pathlib import Path

_app = Path(__file__).parent / "statement_importer.py"

def run():
    subprocess.run(["marimo", "run", str(_app)] + sys.argv[1:])

def edit():
    subprocess.run(["marimo", "edit", str(_app)] + sys.argv[1:])
