"""No statement tested: times uncited_matches_report on the latest entry of the real notebook."""
import importlib.util, sys, time
from pathlib import Path
sys.path.insert(0, 'tools')
spec = importlib.util.spec_from_file_location('ft', 'tools/finish-turn.py'); ft = importlib.util.module_from_spec(spec); spec.loader.exec_module(ft)
body = Path('notebook.html').read_text()
for anchor in ('entry-2026-10-16-common-span-branching', 'entry-2026-10-16-matched-image-goal-review'):
    at = body.index(f'<article id="{anchor}"'); entry = body[at:body.index('</article>', at)]
    t = time.monotonic(); lines = ft.uncited_matches_report(entry); print(anchor, f'{time.monotonic()-t:.2f} s')
    print('\n'.join(lines))
