#!/usr/bin/env python3
"""Rebuild a cycle's claim registration after its entry changed.

    ./compute.sh --threads 1 --category local_processing python3 tools/claim_refresh.py SPEC \
        --out REQUEST --proposal PROPOSAL --report REPORT

A claim's reviews hash the evidence it was built from, so an edit to the entry after
`claim-index.py author build` leaves them stale, and the finisher refuses the commit.  The repair is
always the same: restore the registry and its generated index from HEAD, remove that build's outputs,
build again with the same paths, copy the proposal over the registry and render.  On 16 October 2026
it was done by hand four times in one session; this command does it in one step.
"""
import argparse
import pathlib
import shutil
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
REGISTRY = 'research/claims/index.json'
GENERATED = 'research/CLAIM_INDEX.md'


def run(command, root):
    print('+', ' '.join(command), flush=True)
    subprocess.run(command, cwd=root, check=True)


def committed_claims(spec, root):
    """The spec's claim IDs that HEAD's registry already holds: author build appends only, so for those the
    rebuild cannot work, and the refresh refuses before it touches any output (17 October 2026: run on a
    committed claim, it deleted and rewrote the committed build request and only then failed)."""
    import json
    path = pathlib.Path(root, spec)
    if not path.exists():
        return []
    ids = [item['id'] for item in json.loads(path.read_text()).get('claims', [])]
    held = subprocess.run(['git', 'show', f'HEAD:{REGISTRY}'], cwd=root, capture_output=True, text=True)
    if held.returncode:
        return []
    known = {claim['id'] for claim in json.loads(held.stdout).get('claims', [])}
    return [i for i in ids if i in known]


def refresh(spec, out, proposal, report, root=ROOT, summaries_checked=False):
    held = committed_claims(spec, root)
    if held:
        raise SystemExit('claim_refresh.py: HEAD already registers ' + ', '.join(held) + ': a rebuild appends '
                         'and cannot refresh a committed claim; refresh its reviews through the registry\'s '
                         'reviewed metadata edit (research/claims/README.md). Nothing was changed.')
    run(['git', 'checkout', 'HEAD', '--', REGISTRY, GENERATED], root)
    for path in (out, proposal, report):
        pathlib.Path(root, path).unlink(missing_ok=True)
    tool = str(pathlib.Path(root, 'tools', 'claim-index.py'))
    # A refresh always follows an entry edit, so the build refuses until the agent has compared the
    # spec summaries with the entry statements it prints and says so (16 October 2026: the refusal,
    # added to author build, broke this caller, which passed no way to answer it).
    run([sys.executable, tool, 'author', 'build', '--spec', str(spec), '--out', str(out),
         '--proposal', str(proposal), '--report', str(report)]
        + (['--summaries-checked'] if summaries_checked else []), root)
    shutil.copyfile(pathlib.Path(root, proposal), pathlib.Path(root, REGISTRY))
    # Once copied, the proposal is a second full registry (50 MB on 16 October 2026); left in scratch,
    # one per refresh, they filled the session's 500 MB cap.
    pathlib.Path(root, proposal).unlink()
    run([sys.executable, tool, 'render'], root)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('spec')
    parser.add_argument('--out', required=True)
    parser.add_argument('--proposal', required=True)
    parser.add_argument('--report', required=True)
    parser.add_argument('--summaries-checked', action='store_true',
                        help="passed to author build: the spec's summaries were compared with the entry")
    args = parser.parse_args(argv)
    refresh(args.spec, args.out, args.proposal, args.report, summaries_checked=args.summaries_checked)
    print('Registry rebuilt from HEAD with the spec; stage it with the entry.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
