#!/usr/bin/env python3
"""Import, render, validate, and export the authoritative claim registry."""
import argparse
import json
from pathlib import Path
import subprocess
import sys

from claim_registry import (ROOT, REGISTRY, MARKDOWN, import_markdown, load, render,
                            reconcile, check_targets, exported, require, write_json, upgrade)
from claim_reviews import coverage, FIELDS
from claim_graph import query as graph_query, audit as graph_audit
from claim_maintenance import check_revision
from claim_views import bundle_files


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
    ren.add_argument('--views-out', type=Path, help='Also write navigable topic/lifecycle views to this directory')
    val = sub.add_parser('validate')
    val.add_argument('--markdown', type=Path, default=MARKDOWN)
    val.add_argument('--out', type=Path)
    val.add_argument('--views-dir', type=Path, help='Check derived topic/lifecycle files in this directory')
    val.add_argument('--baseline', help='Check a pristine migration against an immutable Git revision')
    exp = sub.add_parser('export')
    exp.add_argument('--out', type=Path, required=True)
    up = sub.add_parser('upgrade', help='Lossless v1 to v2 expansion, without inferred reviews')
    up.add_argument('--out', type=Path, required=True)
    cov = sub.add_parser('coverage', help='Report field-level unreviewed, pending and stale metadata')
    cov.add_argument('--field', choices=FIELDS)
    cov.add_argument('--state', choices=['unreviewed', 'reviewed', 'pending', 'not_applicable', 'stale'])
    cov.add_argument('--topic')
    cov.add_argument('-n', type=int, default=20)
    cov.add_argument('--out', type=Path, help='Save the complete report, including unshown rows')
    cov.add_argument('--json', action='store_true')
    sub.add_parser('list', add_help=False, help='Minimal listing; forwards filters/fields/format to search')
    sub.add_parser('views', add_help=False, help='Derived topics, lifecycle views and duplicate candidates')
    sub.add_parser('author', add_help=False, help='Source-backed template/proposal authoring')
    changed = sub.add_parser('changed', help='Check metadata completeness relative to a Git revision')
    changed.add_argument('--base', default='HEAD')
    changed.add_argument('--out', type=Path)
    graph = sub.add_parser('graph', help='Typed graph traversal and audit')
    graph.add_argument('mode', choices=['predecessors','successors','ancestors','descendants','cites','impact','audit'])
    graph.add_argument('claim', nargs='?')
    graph.add_argument('--namespace', default='current', choices=['current','historical','external'])
    graph.add_argument('--type', action='append', dest='types',
                       choices=['depends_on','cites','refines','supersedes','corrects',
                                'rediscovers','formalizes','applies','obstructs'])
    graph.add_argument('--include-unreviewed', action='store_true')
    graph.add_argument('-n', type=int, default=20)
    graph.add_argument('--out', type=Path)
    args, rest = parser.parse_known_args()
    if args.command in ('views', 'author'):
        tool = 'claim_views.py' if args.command == 'views' else 'claim_authoring.py'
        return subprocess.call([sys.executable, str(ROOT/'tools'/tool), '--registry', str(args.registry), *rest])
    if args.command == 'list':
        return subprocess.call([sys.executable, str(ROOT/'tools/search-claims.py'),
                                '--registry', str(args.registry), '--list', *rest])
    if rest:
        parser.error('unrecognized arguments: ' + ' '.join(rest))
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
    if args.command == 'changed':
        report = check_revision(data, args.base)
        if args.out:
            write_json(args.out, report)
        print(json.dumps(report, indent=2))
        return 0 if report['passed'] else 1
    elif args.command == 'graph':
        require(args.n > 0, 'Graph limit must be positive')
        if args.mode == 'audit':
            report = graph_audit(data)
        else:
            require(args.claim is not None, 'Graph traversal requires a claim ID')
            report = graph_query(data, args.claim, args.mode, args.types or ('depends_on',),
                                 args.include_unreviewed, args.namespace)
        if args.out:
            write_json(args.out, report)
        display = dict(report)
        if 'nodes' in display:
            display['nodes'] = report['nodes'][:args.n]
            display['omitted'] = max(0, len(report['nodes'])-args.n)
        print(json.dumps(display, indent=2))
    elif args.command == 'upgrade':
        write_json(args.out, upgrade(data))
        print(f"Upgraded {len(data['claims'])} claims without inferring metadata.")
    elif args.command == 'coverage':
        require(args.n > 0, 'Coverage limit must be positive')
        report = coverage(data)
        if args.out:
            write_json(args.out, report)
        rows = [r for r in report['fields'] if (not args.field or r['field'] == args.field)
                and (not args.state or r['state'] == args.state)
                and (not args.topic or args.topic in r['topics'])]
        if args.json:
            print(json.dumps(dict(report, fields=rows[:args.n], omitted=max(0, len(rows)-args.n)), indent=2))
        else:
            print(json.dumps(report['counts'], indent=2))
            for row in rows[:args.n]:
                print(f"{row['id']}\t{row['field']}\t{row['state']}\t{row['next_action'] or ''}")
            print(f'{len(rows)} matching field reviews; {max(0,len(rows)-args.n)} omitted.')
    elif args.command == 'render':
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(render(data))
        views = args.views_out
        if views is None and args.out.resolve() == MARKDOWN.resolve() and args.registry.resolve() == REGISTRY.resolve():
            views = REGISTRY.parent / 'views'
        if views is not None:
            views.mkdir(parents=True, exist_ok=True)
            for filename, content in bundle_files(data).items():
                (views / filename).write_text(content)
        print(f"Rendered {len(data['claims'])} claims.")
    elif args.command == 'export':
        write_json(args.out, exported(data))
        print(f"Exported {len(data['claims'])} claims and {len(data['relationships'])} relationships.")
    else:
        report = check_targets(data)
        report['claims'] = len(data['claims'])
        report['generated_markdown_current'] = args.markdown.is_file() and args.markdown.read_text() == render(data)
        views = args.views_dir
        if views is None and args.markdown.resolve() == MARKDOWN.resolve() and args.registry.resolve() == REGISTRY.resolve():
            views = REGISTRY.parent / 'views'
        if views is not None:
            report['stale_topic_views'] = [name for name, content in bundle_files(data).items()
                if not (views / name).is_file() or (views / name).read_text() != content]
            report['passed'] = report['passed'] and not report['stale_topic_views']
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
