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


def refresh(spec, out, proposal, report, root=ROOT):
    run(['git', 'checkout', 'HEAD', '--', REGISTRY, GENERATED], root)
    for path in (out, proposal, report):
        pathlib.Path(root, path).unlink(missing_ok=True)
    tool = str(pathlib.Path(root, 'tools', 'claim-index.py'))
    run([sys.executable, tool, 'author', 'build', '--spec', str(spec), '--out', str(out),
         '--proposal', str(proposal), '--report', str(report)], root)
    shutil.copyfile(pathlib.Path(root, proposal), pathlib.Path(root, REGISTRY))
    run([sys.executable, tool, 'render'], root)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('spec')
    parser.add_argument('--out', required=True)
    parser.add_argument('--proposal', required=True)
    parser.add_argument('--report', required=True)
    args = parser.parse_args(argv)
    refresh(args.spec, args.out, args.proposal, args.report)
    print('Registry rebuilt from HEAD with the spec; stage it with the entry.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
