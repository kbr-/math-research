#!/usr/bin/env python3
"""Resolve only parallel notebook/index additions in a paused Git rebase.

Run from the affected worktree. If overview paragraphs differ, --overview-file
must contain the complete reviewed Formal verification paragraph. This tool
does not stage files or continue Git operations. Other conflict shapes require
manual review; no historical article or index row may be changed or removed.
"""

import argparse
import json
from pathlib import Path
import re
import subprocess
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from claim_registry import load as load_registry, validate as validate_registry, render as render_index
from claim_registry import parse_json


ARTICLE = re.compile(r'<article\b[^>]*id="([^"]+)"[^>]*>.*?</article>', re.S)
OVERVIEW = re.compile(r'<p><strong>Formal verification\.</strong>.*?</p>', re.S)
MARKER = '<!-- Append new dated mathematical entries here, preserving earlier entries. -->'


def require(condition, message):
    if not condition:
        raise ValueError(message)


def articles(text):
    matches = list(ARTICLE.finditer(text))
    ids = [m.group(1) for m in matches]
    require(len(ids) == len(set(ids)), 'Duplicate article IDs.')
    require(len(matches) == len(re.findall(r'<article\b', text)),
            'Unrecognized article markup; review manually.')
    return {m.group(1): m.group() for m in matches}


def overview(text):
    matches = OVERVIEW.findall(text)
    require(len(matches) == 1, 'Expected one Formal verification paragraph.')
    return matches[0]


def merge_notebook(base, ours, theirs, reviewed_overview=None):
    records = [articles(s) for s in (base, ours, theirs)]
    for branch in records[1:]:
        require(list(branch)[:len(records[0])] == list(records[0]),
                'Historical article order changed.')
        for key, body in records[0].items():
            require(branch.get(key) == body, f'Historical article changed: {key}')
    for key in records[1].keys() & records[2].keys():
        require(records[1][key] == records[2][key], f'Conflicting article: {key}')
    scaffolds = []
    for text in (base, ours, theirs):
        require(text.count(MARKER) == 1, 'Missing or duplicate append marker.')
        overview(text)
        scaffolds.append(' '.join(OVERVIEW.sub('', ARTICLE.sub('', text)).split()))
    require(scaffolds[0] == scaffolds[1] == scaffolds[2],
            'Changes outside articles/verification overview require manual review.')
    left, right = overview(ours), overview(theirs)
    if reviewed_overview is None:
        require(left == right, 'Supply --overview-file with the reviewed combined paragraph.')
        combined_overview = left
    else:
        combined_overview = reviewed_overview.strip()
        require(OVERVIEW.fullmatch(combined_overview) is not None,
                'Overview file must contain exactly the Formal verification paragraph.')
        require(combined_overview.count('<p>') == combined_overview.count('</p>') == 1,
                'Overview file contains more than one paragraph.')
        require('<article' not in combined_overview and MARKER not in combined_overview,
                'Invalid overview content.')
    additions = [body for key, body in records[2].items() if key not in records[1]]
    merged = ours.replace(MARKER, '\n\n'.join(additions) + '\n\n' + MARKER)
    merged = merged.replace(left, combined_overview, 1)
    require(len(articles(merged)) == len(records[1].keys() | records[2].keys()),
            'Merged article count mismatch.')
    return merged


def merge_index(base, ours, theirs):
    # Ignore blank-line placement, but require exact nonblank content. Row edits,
    # insertions elsewhere, removals, or changed prose fail closed.
    original = base.rstrip()
    original_lines = [line for line in original.splitlines() if line.strip()]
    extra = []
    for branch in (ours, theirs):
        lines = [line for line in branch.splitlines() if line.strip()]
        require(lines[:len(original_lines)] == original_lines,
                'Existing index content changed.')
        rows = lines[len(original_lines):]
        require(all(line.startswith('| `') and line.endswith('|') for line in rows),
                'Index changes are not solely appended claim rows.')
        extra.extend(rows)
    def label(row):
        return row.split('`', 2)[1]
    known = {label(row): row for row in original.splitlines() if row.startswith('| `')}
    additions = []
    for row in extra:
        key = label(row)
        if key in known:
            require(known[key] == row, f'Conflicting index row: {key}')
        else:
            known[key] = row
            additions.append(row)
    return original + '\n' + '\n'.join(additions) + '\n'


def merge_registry(base, ours, theirs):
    """Union additions only; refuse semantic edits to existing claims or edges."""
    records = [validate_registry(parse_json(text)) for text in (base, ours, theirs)]
    original = records[0]
    for branch in records[1:]:
        require({k: v for k, v in branch.items() if k not in ('claims', 'relationships')} ==
                {k: v for k, v in original.items() if k not in ('claims', 'relationships')},
                'Registry metadata changed; review manually.')
        for field in ('claims', 'relationships'):
            require(branch[field][:len(original[field])] == original[field],
                    f'Existing {field} changed; review manually.')
    result = dict(original)
    for field in ('claims', 'relationships'):
        result[field] = list(original[field])
        known = {item['id']: item for item in result[field]}
        for branch in records[1:]:
            for item in branch[field][len(original[field]):]:
                if item['id'] in known:
                    require(known[item['id']] == item, f'Conflicting {field} ID: {item["id"]}')
                else:
                    result[field].append(item)
                    known[item['id']] = item
    validate_registry(result)
    return json.dumps(result, ensure_ascii=False, indent=2) + '\n'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--overview-file', type=Path,
                        help='complete reviewed HTML Formal verification paragraph')
    args = parser.parse_args()
    root = Path(subprocess.check_output(['git', 'rev-parse', '--show-toplevel'], text=True).strip())
    def git(*argv):
        return subprocess.check_output(['git', '-C', str(root), *argv], text=True)
    require(any((Path(git('rev-parse', '--git-path', name).strip())).exists()
                for name in ('rebase-merge', 'rebase-apply')), 'No rebase is in progress.')
    conflicts = set(git('diff', '--name-only', '--diff-filter=U').splitlines())
    registry_path = 'research/claims/index.json'
    allowed = {'notebook.html', 'research/CLAIM_INDEX.md', registry_path}
    require(conflicts and conflicts <= allowed, 'Unrelated conflicts require manual review.')
    reviewed = args.overview_file.read_text() if args.overview_file else None
    outputs = {}
    touched = set(conflicts)
    structured = (root / registry_path).exists()
    if structured and conflicts & {registry_path, 'research/CLAIM_INDEX.md'}:
        touched.add('research/CLAIM_INDEX.md')
        touched.add(registry_path)
    originals = {name: (root / name).read_bytes() for name in touched}
    for name in sorted(conflicts - ({'research/CLAIM_INDEX.md'} if structured else set())):
        stages = [git('show', f':{stage}:{name}') for stage in (1, 2, 3)]
        outputs[name] = (merge_notebook(*stages, reviewed) if name == 'notebook.html' else
                         merge_registry(*stages) if name == registry_path else merge_index(*stages))
    if structured and conflicts & {registry_path, 'research/CLAIM_INDEX.md'}:
        registry = (json.loads(outputs[registry_path]) if registry_path in outputs else
                    load_registry(root / registry_path))
        outputs['research/CLAIM_INDEX.md'] = render_index(registry)
    # Validate all files before writing either one. Leave Git staging explicit.
    for name, original in originals.items():
        require((root / name).read_bytes() == original, 'File changed during review; retry.')
    for name, output in outputs.items():
        (root / name).write_text(output)
    print('Resolved append-only content in: ' + ', '.join(sorted(outputs)))
    print('Review the diff, stage the resolved files, then run git rebase --continue.')


if __name__ == '__main__':
    try:
        main()
    except (ValueError, subprocess.CalledProcessError) as error:
        raise SystemExit(f'Refusing automatic resolution: {error}')
