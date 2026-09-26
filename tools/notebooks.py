"""Notebook identities and source resolution shared by tools and serving.

Main stays implicit. Each side notebook is registered by its own notebook.json,
so independently created threads do not contend on a central catalogue file.
"""
# SPDX-License-Identifier: MIT
import json
import re
import subprocess
from pathlib import Path
from urllib.parse import urlparse, unquote

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = 'https://kbr.is-a.dev/math-research/'
NAME = re.compile(r'[a-z][a-z0-9]*(?:-[a-z0-9]+)*\Z')


def valid_name(name):
    if not isinstance(name, str) or not NAME.fullmatch(name) or name in {'main', 'index', 'revision', 'search'}:
        raise ValueError('Use a unique lowercase hyphenated thread name (main is reserved)')
    return name


def catalogue(root=ROOT):
    root = Path(root).resolve()
    result = {'main': dict(name='main', title='Main research notebook', status='active',
                          source='notebook.html', route='', budgets='research/context-budgets.json', parent=None)}
    directory = root / 'research/branches'
    if directory.is_symlink():
        raise ValueError('Notebook directory must not be a symlink')
    for path in sorted(directory.glob('*/notebook.json')):
        if path.parent.name.startswith('.'):
            continue  # Incomplete atomic setup is not a registered notebook.
        name = valid_name(path.parent.name)
        if path.is_symlink() or path.parent.is_symlink():
            raise ValueError('Notebook registration must not use symlinks')
        meta = json.loads(path.read_text())
        if set(meta) != {'version','name','title','status','parent','origin'} or meta['version'] != 1:
            raise ValueError(f'Invalid notebook metadata: {path}')
        if meta['name'] != name or not isinstance(meta['title'], str) or not meta['title'].strip():
            raise ValueError(f'Invalid notebook identity: {path}')
        if meta['status'] not in {'active','completed','abandoned'}:
            raise ValueError(f'Invalid notebook status: {name}')
        if not isinstance(meta['parent'], str) or (meta['origin'] is not None and not isinstance(meta['origin'], str)):
            raise ValueError(f'Invalid notebook parent/origin: {name}')
        for leaf in ('notebook.html', 'context-budgets.json'):
            target = path.parent / leaf
            if not target.is_file() or target.is_symlink():
                raise ValueError(f'Missing or unsafe notebook file: {target}')
        result[name] = dict(meta, source=f'research/branches/{name}/notebook.html',
                            route=f'branches/{name}/', budgets=f'research/branches/{name}/context-budgets.json')
    for name, item in result.items():
        seen = {name}; parent = item['parent']
        while parent is not None:
            if parent not in result or parent in seen:
                raise ValueError(f'Invalid notebook ancestry: {name}')
            seen.add(parent); parent = result[parent]['parent']
    return result


def selection_file(root=ROOT):
    value = subprocess.check_output(['git','rev-parse','--git-path','noemesis-notebook'],cwd=root,text=True,stderr=subprocess.DEVNULL).strip()
    path = Path(value)
    return path if path.is_absolute() else Path(root)/path


def selected(name=None, root=ROOT, items=None):
    """Pass `items`, a catalogue, to avoid rereading it on every call in a loop."""
    if name is None:
        try:
            path = selection_file(root)
            name = path.read_text().strip() if path.exists() else 'main'
        except subprocess.CalledProcessError:
            name = 'main'
    if items is None:
        items = catalogue(root)
    if name not in items:
        raise ValueError(f'Unknown notebook: {name}')
    return items[name]


def select(name, root=ROOT):
    item = selected(name, root)
    path = selection_file(root)
    path.write_text(item['name']+'\n')
    return item


def paths(root=ROOT):
    return [Path(root)/item['source'] for item in catalogue(root).values()]


def public_target(target, root=ROOT, items=None):
    """Resolve our public notebook URLs; external URLs return None. `items` as for selected."""
    p = urlparse(target)
    if p.scheme not in ('http','https') or p.netloc not in ('kbr.is-a.dev','kbr-.github.io'):
        return None
    path = unquote(p.path).rstrip('/')
    if path == '/math-research':
        return Path(root)/'notebook.html', unquote(p.fragment)
    prefix = '/math-research/branches/'
    if path.startswith(prefix):
        name = path[len(prefix):]
        item = selected(name, root, items)
        return Path(root)/item['source'], unquote(p.fragment)
    return None


def resolve_anchor(anchor, name=None, root=ROOT):
    """Explicit selection is local; bare anchors must be globally unambiguous."""
    items = [selected(name,root)] if name is not None else catalogue(root).values()
    matches = [item for item in items if re.search(r'\bid=[\"\']'+re.escape(anchor.removeprefix('#'))+r'[\"\']',
                                                  (Path(root)/item['source']).read_text())]
    if len(matches) != 1:
        raise ValueError(f'Anchor {anchor!r} has {len(matches)} notebook matches; specify --notebook')
    return matches[0]
