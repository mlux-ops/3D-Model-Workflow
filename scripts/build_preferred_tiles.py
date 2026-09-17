"""Preferred-material entry point. R1 2x2 builder is archived, not for delivery."""
from pathlib import Path
import runpy

if __name__ == '__main__':
    runpy.run_path(str(Path(__file__).with_name('rebuild_preferred_variation.py')), run_name='__main__')