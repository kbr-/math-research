"""No statement tested: time unreviewed_block on this session's real transcript and logs."""
import importlib.util, time, os
from pathlib import Path
spec = importlib.util.spec_from_file_location('sc', 'tools/hooks/stop_checks.py'); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
path = '/home/kbr/.claude/projects/-home-kbr-dev-math-auxiliary/d56a25e2-0e04-486a-8bda-c7425e77fcb8.jsonl'
print('transcript', round(os.path.getsize(path) / 1e6, 1), 'MB;', len(list(Path('research/logs').glob('*.jsonl'))), 'journals')
reply = 'The rank of the weighted kernel is nonzero, so the bound holds for every source.'
t = time.monotonic(); since = m.unreviewed_cycle(Path('.')); t1 = time.monotonic() - t
t = time.monotonic(); back = m.reviewer_returned(path, 0); t2 = time.monotonic() - t
t = time.monotonic(); blk = m.unreviewed_block(path, reply, Path('.')); t3 = time.monotonic() - t
print(f'open mathematics session start: {since} ({t1:.3f} s); a reviewer report in the tail: {back} ({t2:.3f} s); block: {blk is not None} ({t3:.3f} s)')
