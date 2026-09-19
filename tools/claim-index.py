#!/usr/bin/env python3
"""Import, render, validate, and export the authoritative claim registry."""
import argparse
import json
from pathlib import Path
import subprocess
import sys

from claim_registry import (ROOT, REGISTRY, MARKDOWN, import_markdown, load, render,
                            reconcile, check_targets, exported, require, write_json)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--registry', type=Path, default=REGISTRY)
    sub = parser.add_subparsers(dest='command', required=True)
    imp = sub.add_parser('import', help='One-time legacy import; refuses overwrite')
    imp.add_argument('--revision', required=True)
    imp.add_argument('--out', type=Path, required=True)
    imp.add_argument('--report', type=Path, required=True)
    ren = sub.add_parser('render')
    ren.add_argument('--out', type=Path, default=MARKDOWN)
    val = sub.add_parser('validate')
    val.add_argument('--markdown', type=Path, default=MARKDOWN)
    val.add_argument('--out', type=Path)
    val.add_argument('--baseline', help='Check a pristine migration against an immutable Git revision')
    exp = sub.add_parser('export')
    exp.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    if args.command == 'import':
        require(not args.out.exists() and not args.report.exists(), 'Output/report already exists')
        revision = subprocess.check_output(['git', 'rev-parse', args.revision + '^{commit}'], cwd=ROOT, text=True).strip()
        text = subprocess.check_output(['git', 'show', revision + ':research/CLAIM_INDEX.md'], cwd=ROOT, text=True)
        data = import_markdown(text)
        report = reconcile(text, data, revision)
        write_json(args.out, data)
        write_json(args.report, report)
        print(f"Imported {len(data['claims'])} claims; original fields and links reconciled.")
        return 0
    data = load(args.registry)
    if args.command == 'render':
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(render(data))
        print(f"Rendered {len(data['claims'])} claims.")
    elif args.command == 'export':
        write_json(args.out, exported(data))
        print(f"Exported {len(data['claims'])} claims and {len(data['relationships'])} relationships.")
    else:
        report = check_targets(data)
        report['claims'] = len(data['claims'])
        report['generated_markdown_current'] = args.markdown.is_file() and args.markdown.read_text() == render(data)
        if args.baseline:
            text = subprocess.check_output(['git', 'show', args.baseline + ':research/CLAIM_INDEX.md'], cwd=ROOT, text=True)
            report['reconciliation'] = reconcile(text, data, args.baseline)
        report['passed'] = report['passed'] and report['generated_markdown_current']
        if args.out:
            write_json(args.out, report)
        print(json.dumps(report, indent=2))
        return 0 if report['passed'] else 1
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (ValueError, OSError, subprocess.CalledProcessError) as exc:
        sys.exit(f'claim-index: {exc}')
