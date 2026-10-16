"""No statement tested: time each path of the Stop hook's Unreviewed check on this session's real transcript and
logs (one-off provenance; it names the session's transcript by its absolute path)."""
import importlib.util, os, time
from pathlib import Path
spec = importlib.util.spec_from_file_location('sc', 'tools/hooks/stop_checks.py'); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
path = '/home/kbr/.claude/projects/-home-kbr-dev-math-auxiliary/d56a25e2-0e04-486a-8bda-c7425e77fcb8.jsonl'
print('transcript', round(os.path.getsize(path) / 1e6, 1), 'MB;', len(list(Path('research/logs').glob('*.jsonl'))), 'journals')
t = time.monotonic(); since = m.unreviewed_cycle(Path('.')); print(f'unreviewed_cycle: {since} in {time.monotonic()-t:.3f} s')
for hours in (1, 8):
    t = time.monotonic(); back = m.reviewer_returned(path, time.time() - 3600 * hours)
    print(f'reviewer_returned since {hours} h ago: {back} in {time.monotonic()-t:.3f} s')
# Worst case: the same transcript through a link whose subagents directory does not exist, so no report counts
# as a reviewer's and the read goes back to its 64 MB limit.
worst = '/home/kbr/.claude/jobs/d56a25e2/tmp/worst/t.jsonl'
t = time.monotonic(); back = m.reviewer_returned(worst, 0); print(f'worst case (64 MB, no reviewer): {back} in {time.monotonic()-t:.3f} s')
