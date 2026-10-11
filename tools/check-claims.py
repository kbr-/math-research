#!/usr/bin/env python3
"""Run the claim-index CI job locally or in CI, reporting every failing check with its reason.

The workflow .github/workflows/claim-index.yml runs this script, and
tools/verify-checkout.py --public-history runs it before publication, so a push cannot
reach CI with a failure this job would find. Outside GitHub Actions, whose runners are several
times slower, it also fails a run in which a check takes longer than LIMIT_S (the changed-claim contract:
LIMIT_S plus PER_CLAIM_S for each claim changed since the base), so a slowdown is noticed. With
--warn-over-limit, as a push runs it, an overrun is a note instead: a push carries changes and may
meet a loaded machine, and a performance regression must not block publishing.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parents[1]
LIMIT_S = 5.0  # About twice this job's time on the project machine, when little changed since the base.
# The changed-claim contract rechecks every claim changed since the base, so its time grows with their
# number: measured on 11 October 2026 on this repository, inside this job 1.9 s against HEAD and 8.3 to 9.1 s
# against a published base 879 commits and 1178 changed claims behind (about 6 ms a claim).  A count found 712
# normalizations of 711 distinct texts and 806 excerpts of 793 distinct anchors, so the cited evidence is not
# rehashed; the rest is parsing five notebooks and loading the registry.  The contract then ran its
# registration of entries, its evidence hashing by source file and the registry's validation in forked workers:
# 4.9 s alone at that scope (three runs, 4.86 to 4.88 s), about 3 ms a claim over its time against HEAD.  The
# contract's own limit grows by 6 ms a claim, twice that cost; the other checks keep the fixed limit.
PER_CLAIM_S = 0.006
SCOPE = {'claims': 0, 'times': None}


def changed_claims(output):
    """The number of claims the changed-claim contract reviewed, from its JSON report; 0 if unreadable."""
    try:
        return len(json.loads(output[output.index('{'):output.rindex('}') + 1])['required_reviews'])
    except (ValueError, KeyError, TypeError):
        return 0
TESTS = ('claim_attention', 'fossick', 'claim_registry', 'claim_duplicates', 'claim_authoring',
         'claim_notices', 'claim_article_evidence', 'claim_article_finalizer', 'finish_turn',
         'record_citations', 'claim_dependencies', 'claim_graph', 'merge_formalization_appends',
         'claim_maintenance', 'claim_registration', 'merge_claim_registry', 'remap_revisions')


def checks(base):
    py = sys.executable
    yield 'claim index validation', [py, 'tools/claim-index.py', 'validate']
    yield 'attention history', [py, 'tools/claim-attention.py', 'check']
    # The suite's own time limit is for the whole suite on the project machine.
    yield 'claim tests', [py, 'tools/tests/run.py', '--limit', 'inf', *(f'test_{name}' for name in TESTS)]
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


def measured(command):
    """Run one check: its result, its wall time, and the CPU time of the process and the children it waited
    for.  A busy machine stretches wall time and not CPU time, which is how the two are told apart."""
    start = time.monotonic()
    with tempfile.TemporaryFile('w+') as out, tempfile.TemporaryFile('w+') as err:
        process = subprocess.Popen(command, cwd=ROOT, text=True, stdout=out, stderr=err)
        _, status, usage = os.wait4(process.pid, 0)
        process.returncode = os.waitstatus_to_exitcode(status)
        out.seek(0)
        err.seek(0)
        result = subprocess.CompletedProcess(command, process.returncode, out.read(), err.read())
    return result, time.monotonic() - start, usage.ru_utime + usage.ru_stime


def run(base, jobs=8):
    """Checks are independent (read-only, tests in their own temporary directories), so they
    run concurrently; results are reported in the fixed order of checks()."""
    listed = list(checks(base))
    with ThreadPoolExecutor(max_workers=jobs) as pool:
        results = list(pool.map(measured, [command for _, command in listed]))
    failures = []
    # The contract is the last check listed.
    SCOPE.update(claims=changed_claims(results[-1][0].stdout),
                 times=[(title, seconds, cpu) for (title, _), (_, seconds, cpu) in zip(listed, results)])
    for (title, _), (result, seconds, _) in zip(listed, results):
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
    parser.add_argument('--limit', type=float, default=LIMIT_S,
                        help=f'Wall-time limit in seconds outside GitHub Actions (default {LIMIT_S:g})')
    parser.add_argument('--warn-over-limit', action='store_true',
                        help='Report a run over the limit as a note instead of failing')
    args = parser.parse_args()
    start = time.monotonic()
    failures = run(args.base, args.jobs)
    elapsed = time.monotonic() - start
    times = SCOPE['times']
    if times is None:      # no per-check times: the whole run against the fixed limit
        over = [(elapsed, args.limit)] if elapsed > args.limit else []
    else:
        # The checks run at once, so each is held to the limit by its own time; only the contract's grows.
        scaled = args.limit + PER_CLAIM_S * SCOPE['claims']
        if SCOPE['claims']:
            print(f'Changed scope: {SCOPE["claims"]} claims since {args.base}; the contract\'s limit is '
                  f'{args.limit:g} s plus {PER_CLAIM_S * 1000:g} ms for each, {scaled:.1f} s; the other checks keep '
                  f'{args.limit:g} s.')
        over = []
        for index, (title, seconds, cpu) in enumerate(times):
            limit = scaled if index == len(times) - 1 else args.limit
            if seconds <= limit:
                continue
            if cpu is not None and cpu <= limit:
                # Over in wall time and within the limit in CPU time: the machine was busy, not the check slow.
                print(f'Note: {title} took {seconds:.1f} s of wall time and {cpu:.1f} s of CPU time, within its '
                      f'{limit:g} s limit: the machine was busy.')
                continue
            over.append((seconds, limit))
    slow = bool(over) and os.environ.get('GITHUB_ACTIONS') != 'true'
    if slow:
        shown, limit = over[0]
        print(f'{"Note: took" if args.warn_over_limit else "Took"} {shown:.1f} s, over the {limit:g} s '
              'limit; the times above show which checks.')
    print(f'{len(failures)} failing claim-index checks' if failures else 'All claim-index checks pass.')
    return 1 if failures or (slow and not args.warn_over_limit) else 0


if __name__ == '__main__':
    sys.exit(main())
