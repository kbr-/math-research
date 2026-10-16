"""No statement tested: time the Stop hook's Unreviewed check on its blocking path with real data. A scratch root
links every real research/logs journal and adds one newest open session with a mathematics phase; the reply is
checked against this session's real transcript (one-off provenance with absolute paths)."""
import importlib.util, json, os, shutil, time
from pathlib import Path
spec = importlib.util.spec_from_file_location('sc', 'tools/hooks/stop_checks.py'); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
transcript = '/home/kbr/.claude/projects/-home-kbr-dev-math-auxiliary/d56a25e2-0e04-486a-8bda-c7425e77fcb8.jsonl'
root = Path('/home/kbr/.claude/jobs/d56a25e2/tmp/blockroot'); shutil.rmtree(root, ignore_errors=True)
logs = root / 'research/logs'; logs.mkdir(parents=True)
for p in Path('research/logs').glob('*.jsonl'):
    (logs / p.name).symlink_to(p.resolve())
now = time.time()
(logs / 'open-math-trial.jsonl').write_text(json.dumps({'event': 'start', 'unix_s': now, 'agent': 'claude'}) + '\n'
                                            + json.dumps({'event': 'phase', 'category': 'mathematics'}) + '\n')
print(len(list(logs.glob('*.jsonl'))), 'journals;', round(os.path.getsize(transcript) / 1e6, 1), 'MB transcript')
t = time.monotonic(); since = m.unreviewed_cycle(root); print(f'unreviewed_cycle found start {since == now} in {time.monotonic()-t:.3f} s')
reply = 'The rank of the weighted kernel is nonzero, so the bound holds for every source.'
t = time.monotonic(); blk = m.unreviewed_block(transcript, reply, root); print(f'unreviewed_block blocks: {blk is not None} in {time.monotonic()-t:.3f} s')
shutil.rmtree(root)
