"""Tests the hypothesis that the browser cases' in-suite times (5.2 s and 5.1 s on 17 October 2026, against 2.79 s
alone) come from contention for the CPU: the same case run alone and then beside 13 busy processes, one per other
allowed CPU, as the suite's parallel workers are.

Expected before the run: alone about 2.8 s, as measured before; under load at least 1.5 times that, toward the
in-suite 5.2 s.
Refuted by: a loaded time within 1.2 times the alone time, which would leave contention unable to explain the
in-suite doubling and point at work the suite adds.
Possible because: Chromium's MathJax start is a few CPU-bound seconds that the scheduler shares among 14 runnable
processes on 14 CPUs only if it does not favour the newcomer, which it may.
Positive control: the busy processes' own CPU count is printed, and the load must hold 13 processes busy for the
whole loaded run, else the loaded time measures nothing; checked by asserting each process is alive at the end.
Baseline: the alone time of the same case, measured first in this script.
Record checked: tools/tests/test_site.py's Browser docstring, which says each page spends about 0.75 s of CPU
starting MathJax and that the suite is bound by CPU; no registered claim applies (framework timing).
"""
import json
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'tools' / 'tests'))
import test_site  # noqa: E402

CASES = ['test_notebook_deep_links:links']   # the name the runner prints; a first run with '.cjs' ran no case


def run(label):
    modules = test_site.node_modules()
    result, elapsed = test_site.node('run_browser_tests.cjs', *CASES, modules=modules, timeout=60)
    cases = [json.loads(line) for line in result.stdout.splitlines() if line.startswith('{')]
    for case in cases:
        print(f'{label}: {case["name"]} ok={case["ok"]} seconds={case["seconds"]:.2f} {case.get("error", "")}')
    assert cases and all(c['ok'] for c in cases), f'a case failed, so its time measures nothing: {result.stderr[-500:]}'
    return [c['seconds'] for c in cases]


alone = run('alone')
busy = [subprocess.Popen([sys.executable, '-c', 'while True: pass']) for _ in range(13)]
time.sleep(0.5)
loaded = run('beside 13 busy processes')
alive = sum(p.poll() is None for p in busy)
for p in busy:
    p.kill()
print(f'busy processes alive at the end: {alive} of 13')
assert alive == 13, 'the load did not hold'
print(f'loaded / alone = {loaded[0] / alone[0]:.2f}')
