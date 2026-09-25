#!/usr/bin/env python3
"""Run the claim-index CI job locally or in CI, reporting every failing check with its reason.

The workflow .github/workflows/claim-index.yml runs this script, and
tools/verify-checkout.py --public-history runs it before publication, so a push cannot
reach CI with a failure this job would find.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
import os
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
TESTS = ('claim_attention', 'fossick', 'claim_registry', 'claim_duplicates', 'claim_authoring',
         'claim_notices', 'claim_article_evidence', 'claim_article_finalizer', 'finish_turn',
         'record_citations', 'claim_dependencies', 'claim_graph', 'merge_formalization_appends',
         'claim_maintenance', 'claim_registration', 'merge_claim_registry', 'remap_revisions')


def checks(base):
    py = sys.executable
    yield 'claim index validation', [py, 'tools/claim-index.py', 'validate']
    yield 'attention history', [py, 'tools/claim-attention.py', 'check']
    for name in TESTS:
        yield f'test_{name}', [py, '-m', 'unittest', 'discover', '-s', 'tools/tests', '-p', f'test_{name}.py']
    yield 'claim graph audit', [py, 'tools/claim-index.py', 'graph', 'audit']
    yield 'recorded revisions are ancestors of HEAD', [py, 'tools/remap-revisions.py', '--check']
    yield f'changed-claim contract against {base}', [py, 'tools/claim-index.py', 'changed', '--base', base]


def reason(output, limit=15):
    """The lines that explain a failure: error lines when present, else the output's tail."""
    lines = [line for line in output.splitlines() if line.strip()]
    keys = ('error', 'fail', 'stale', 'traceback', 'assert', '"passed": false')
    flagged = [line for line in lines if any(k in line.lower() for k in keys)]
    return '\n'.join((flagged or lines)[-limit:]) or 'no output'


def annotate(title, text):
    """GitHub shows only this message in the job summary, so it must carry the reason."""
    escape = lambda s: s.replace('%', '%25').replace('\r', '%0D').replace('\n', '%0A')
    print(f'::error title={escape(title).replace(",", "%2C").replace(":", "%3A")}::{escape(text)}')


def run(base, jobs=8):
    """Checks are independent (read-only, tests in their own temporary directories), so they
    run concurrently; results are reported in the fixed order of checks()."""
    listed = list(checks(base))
    def execute(command):
        start = time.monotonic()
        result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True)
        return result, time.monotonic() - start
    with ThreadPoolExecutor(max_workers=jobs) as pool:
        results = list(pool.map(execute, [command for _, command in listed]))
    failures = []
    for (title, _), (result, seconds) in zip(listed, results):
        if result.returncode == 0:
            print(f'ok    {seconds:5.1f} s  {title}')
            continue
        text = reason(result.stdout + '\n' + result.stderr)
        failures.append((title, text))
        print(f'FAIL  {seconds:5.1f} s  {title}\n' + '\n'.join('      ' + line for line in text.splitlines()))
        if os.environ.get('GITHUB_ACTIONS') == 'true':
            annotate(title, text)
    return failures


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base', default='origin/main',
                        help='Revision the changed-claim contract compares against (EMPTY audits all claims)')
    parser.add_argument('--jobs', type=int, default=8, help='Checks run at once (default 8)')
    args = parser.parse_args()
    failures = run(args.base, args.jobs)
    print(f'{len(failures)} failing claim-index checks' if failures else 'All claim-index checks pass.')
    return 1 if failures else 0


if __name__ == '__main__':
    sys.exit(main())
