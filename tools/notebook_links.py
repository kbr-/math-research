#!/usr/bin/env python3
"""Check and repair a notebook's links to repository files.

Every notebook, side notebooks too, names a repository file by its path from the repository root
(tools/SIDE_NOTEBOOKS.md). Links under private/ name git-ignored files that exist only in the shared
checkout and are skipped; so are anchors, absolute paths and links with a scheme.

Usage: notebook_links.py check NOTEBOOK.html   (lists relative links that do not resolve from the root;
                                               exit 1 when there are any)
       notebook_links.py fix NOTEBOOK.html     (rewrites each <a> href that resolves from the notebook's
                                               folder but not from the root into its root path; the
                                               fragment and query are kept; refreshes the claim
                                               registry's evidence hashes the rewrite changes)"""
# SPDX-License-Identifier: MIT
import html
import json
import os
import posixpath
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
A_HREF = re.compile(r'(<a\b[^>]*?\bhref=")([^"]*)(")')


def file_path(href):
    """The relative repository path a link names, or None for a link this tool leaves alone."""
    parts = urlsplit(html.unescape(href))
    if parts.scheme or parts.netloc or not parts.path or parts.path.startswith('/'):
        return None
    path = unquote(parts.path)
    return None if posixpath.normpath(path).split('/')[0] == 'private' else path


def from_root(path, root):
    return (root / path).exists() and (root / path).resolve().is_relative_to(root.resolve())


def unresolved(text, root=ROOT):
    """Each distinct relative link of `text` that names no file from the repository root, in order."""
    found = []
    for href in (m.group(2) for m in A_HREF.finditer(text)):
        path = file_path(href)
        if path is not None and not from_root(path, root) and href not in found:
            found.append(href)
    return found


def fix(text, notebook, root=ROOT):
    """(text with every folder-relative link rewritten to its root path, number of links rewritten)."""
    root, folder = root.resolve(), Path(notebook).resolve().parent
    rewritten = []

    def repair(match):
        href = match.group(2)
        path = file_path(href)
        if path is None or from_root(path, root):
            return match.group(0)
        target = Path(os.path.normpath(folder / path))
        if not target.exists() or not target.is_relative_to(root):
            return match.group(0)
        rest = href[len(href.split('#')[0].split('?')[0]):]
        rewritten.append(href)
        return match.group(1) + target.relative_to(root).as_posix() + rest + match.group(3)
    return A_HREF.sub(repair, text), len(rewritten)


def rewrite_with_evidence(notebook, text, root=ROOT):
    """Write `text` to `notebook`, refreshing the claim registry's evidence hashes the rewrite changes:
    a stored hash is replaced only when it matched the notebook before and the new text hashes differently,
    so a hash already stale stays stale. Returns the number of hashes refreshed."""
    registry = root / 'research/claims/index.json'
    if not registry.exists():
        notebook.write_text(text)
        return 0
    from claim_registry import write_json
    from claim_reviews import Evidence
    data, path = json.loads(registry.read_text()), notebook.resolve()

    def hashes(evidence, items):
        found = {}
        for key, item in items:
            try:
                found[key] = evidence.sha256(item['target'], item.get('normalization'))
            except (OSError, ValueError):
                found[key] = None
        return found
    evidence = Evidence(root)
    items = [(id(item), item) for claim in data['claims'] for review in claim.get('reviews', {}).values()
             for item in review.get('evidence', [])
             if (evidence.local(item['target']) or (None,))[0] is not None
             and Path(evidence.local(item['target'])[0]).resolve() == path]
    before = hashes(evidence, items)
    notebook.write_text(text)
    after = hashes(Evidence(root), items)
    refreshed = 0
    for key, item in items:
        if item['sha256'] == before[key] and after[key] not in (None, before[key]):
            item['sha256'] = after[key]
            refreshed += 1
    if refreshed:
        write_json(registry, data)
    return refreshed


def main(argv):
    if len(argv) != 3 or argv[1] not in ('check', 'fix'):
        print(__doc__, file=sys.stderr)
        return 2
    notebook = Path(argv[2])
    top = subprocess.run(['git', 'rev-parse', '--show-toplevel'], cwd=notebook.resolve().parent,
                         capture_output=True, text=True)
    root = Path(top.stdout.strip()) if top.returncode == 0 else ROOT    # the notebook's own repository
    text = notebook.read_text()
    if argv[1] == 'fix':
        text, count = fix(text, notebook, root)
        refreshed = rewrite_with_evidence(notebook, text, root)
        print(f'{notebook}: {count} links rewritten to their path from the repository root; '
              f'{refreshed} claim evidence hashes refreshed')
    missing = unresolved(text, root)
    for href in missing:
        print(f'{notebook}: does not resolve from the repository root: {href}')
    return 1 if missing else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
