#!/usr/bin/env python3
"""The registered claims behind a publication's statements.

    tools/publication_claims.py SECTION_OR_LABEL ...

Every statement of a publication is derived from registered claims, but the registry reaches it only
through Lean files: research/results/*/statement-links.json maps each label of a section to the Lean
files that formalize it, and a claim's metadata names those files.  So a statement looked up by its
label in the registry is not found (16 October 2026: Braun's cor:polylog-exclusion was cited as
unregistered, although audit:ordinary-restriction-affine-family is its claim).  This tool follows the
chain; notebook-append refuses an entry that links a publication file in a sentence citing no claim.
"""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]


def statement_links(root=ROOT):
    """[(section file name, label, [Lean files])] from every saved statement-links map."""
    rows = []
    for path in sorted(root.glob('research/results/*/statement-links.json')):
        for item in json.loads(path.read_text())['statements']:
            rows.append((item['section'], item['label'], item.get('lean_files', [])))
    return rows


def lean_references(claim):
    """The Lean file references a claim records: formalization.references and each artifact's references.
    Reading only these fields keeps a lookup fast (serializing every claim took 2.6 s) and exact (a raw-text
    scan attributed occurrences in the registry's top-level relationships to unrelated claims)."""
    form = claim.get('formalization') or {}
    refs = list(form.get('references') or [])
    for artifact in form.get('artifacts') or []:
        refs.extend(artifact.get('references') or [])
    return refs


def claims_naming(lean_files, registry):
    """The registered claim identifiers whose formalization references name one of the Lean files."""
    return [claim['id'] for claim in registry
            if any(name in ref for ref in lean_references(claim) for name in lean_files)]


def lookup(keys, root=ROOT):
    """{(section, label): [claim ids]} for the statements whose section file or label is among keys."""
    names = {pathlib.PurePath(key).name for key in keys} | set(keys)
    rows = [row for row in statement_links(root) if row[0] in names or row[1] in names]
    if not rows:
        return {}
    data = json.loads((root / 'research/claims/index.json').read_text())
    registry = data['claims'] if isinstance(data, dict) else data
    return {(section, label): claims_naming(files, registry) for section, label, files in rows}


def main(argv):
    if not argv:
        print(__doc__.strip().splitlines()[2].strip(), file=sys.stderr)
        return 2
    result = lookup(argv)
    if not result:
        print('No statement-links entry matches; search the registry by the statement\'s content '
              '(tools/search-claims.py WORDS).')
        return 1
    for (section, label), ids in result.items():
        print(f'{section}\t{label}\t{" ".join(ids) or "(no claim names its Lean files)"}')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
