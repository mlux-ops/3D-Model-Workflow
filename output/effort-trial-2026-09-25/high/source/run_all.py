"""Rebuild everything in order: sources -> floor validation -> atlas -> review/report."""
import runpy, os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
for s in ['prep_sources.py', 'validate_floor.py', 'build_atlas.py', 'review_atlas.py']:
    print('==', s, flush=True)
    runpy.run_path(s, run_name='__main__')
