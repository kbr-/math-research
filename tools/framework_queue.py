"""The main notebook's shared framework queue; classification is supplied by the author.

All paths are in the caller's worktree. Main means its registered main notebook,
not another checkout. Queue CLI writes share a lock; transfers write the destination
first so an interrupted transfer can be retried without losing an item.
"""
import contextlib
import datetime
import fcntl
import html
import json
import os
from pathlib import Path
import re
import tempfile

SECTION = re.compile(r'<section id="framework-queue"[^>]*>(.*?)</section>', re.S)


def attribute(attrs, name):
    match = re.search(r'\b' + re.escape(name) + r'="([^"]*)"', attrs)
    return html.unescape(match.group(1)) if match else None


def scope(attrs):
    return attribute(attrs, 'data-queue')


def origin(root, path):
    from notebooks import catalogue
    relative = Path(path).resolve().relative_to(Path(root).resolve()).as_posix()
    for name, meta in catalogue(root).items():
        if meta['source'] == relative:
            return name, relative
    raise ValueError(f'{relative} is not a registered notebook')


def key(node):
    return f'{attribute(node.attrs, "data-framework-origin")}::{node.kind}:{node.ident}'


def closed(root, ledger=None):
    """Closed identities retain framework ownership; they cannot silently become new tasks."""
    import lead_queue as q
    ledger = q.closure_ledger(root) if ledger is None else ledger
    return {ident: row for (notebook, ident), row in ledger.items()
            if notebook == 'notebook.html#framework-queue'}


def parse(body):
    import lead_queue as q
    found = SECTION.search(body)
    if not found:
        return []
    listed = re.search(r'<ol>(.*)</ol>', found.group(1), re.S)
    nodes = q.parse_nodes(listed.group(1) if listed else '')
    seen = set()
    for node in nodes:
        if node.children or not attribute(node.attrs, 'data-framework-origin'):
            raise ValueError('Framework items are flat and retain data-framework-origin')
        if scope(node.attrs) != 'framework' or key(node) in seen:
            raise ValueError(f'Invalid or duplicate framework item: {key(node)}')
        q.summary_attribute(q.item_summary(node.attrs))
        seen.add(key(node))
    return nodes


def rewrite(body, nodes):
    import lead_queue as q
    section = ('<section id="framework-queue">\n<h2>Framework queue</h2>\n'
               '<p>Shared tooling, workflow, infrastructure and framework ideas from every notebook. '
               'Independent of the mathematical research queue and its draining rules.</p>\n<ol>\n'
               + q.render_nodes(nodes) + '\n</ol>\n</section>\n')
    if SECTION.search(body):
        return SECTION.sub(lambda _: section.rstrip(), body, count=1)
    marker = '<section id="research-record"'
    at = body.find(marker)
    if at < 0:
        raise ValueError('Main notebook has no research record')
    return body[:at] + section + body[at:]


def transferred(node, notebook, source, parent=None):
    """Preserve the original payload and identifiers, making local links work from main."""
    copy = node.copy()
    copy.children = []
    copy.attrs = re.sub(r'\sdata-queue="[^"]*"', '', copy.attrs)
    copy.attrs += f' data-queue="framework" data-framework-origin="{html.escape(notebook)}"'
    copy.attrs += f' data-framework-source="{html.escape(source)}"'
    if parent:
        copy.attrs += f' data-framework-parent="{html.escape(parent)}"'
    if source != 'notebook.html':
        from notebooks import PUBLIC
        copy.text = re.sub(r'href="#([^\"]*)"',
                           lambda m: f'href="{PUBLIC}branches/{notebook}/#{m.group(1)}"', copy.text)
    return copy


def put(nodes, node):
    old = next((n for n in nodes if key(n) == key(node)), None)
    if old:
        if old.text != node.text or old.attrs != node.attrs:
            raise ValueError(f'{key(node)} already exists with different text or metadata')
        return False
    nodes.append(node)
    return True


@contextlib.contextmanager
def locked(root):
    directory = Path(root) / 'research/logs'
    directory.mkdir(parents=True, exist_ok=True)
    with (directory / 'queue.lock').open('a') as stream:
        fcntl.flock(stream, fcntl.LOCK_EX)
        yield


def write_files(root, originals, updates):
    """Check all inputs before mutation; main first makes partial transfers safely retryable."""
    root = Path(root)
    for relative, original in originals.items():
        if (root / relative).read_text() != original:
            raise ValueError(f'{relative} changed during queue operation; retry from current files')
    for relative in sorted(updates, key=lambda p: (p != 'notebook.html', p)):
        if updates[relative] == originals[relative]:
            continue
        path = root / relative
        fd, temporary = tempfile.mkstemp(prefix='.queue-', dir=path.parent)
        try:
            with os.fdopen(fd, 'w') as stream:
                stream.write(updates[relative])
                stream.flush()
                os.fsync(stream.fileno())
            os.chmod(temporary, path.stat().st_mode)
            os.replace(temporary, path)
        finally:
            if os.path.exists(temporary):
                os.unlink(temporary)


def add(root, path, kind, ident, source, text, summary):
    import lead_queue as q
    notebook, relative = origin(root, path)
    main = Path(root) / 'notebook.html'
    body = main.read_text()
    nodes = parse(body)
    node = q.Node(kind, ident, f' data-{kind}="{html.escape(ident)}" data-source="{html.escape(source)}"'
                  + q.summary_attribute(summary), q.added_text(source, text))
    problems = q.added_admit(q.render_nodes([node]), None, node.item)
    if not text.strip():
        problems.append('The full question must not be empty')
    if problems:
        raise ValueError('; '.join(problems))
    node = transferred(node, notebook, relative)
    if key(node) in closed(root):
        raise ValueError(f'{key(node)} is closed; use a new identifier for new work')
    if any(key(n) == key(node) for n in nodes):
        raise ValueError(f'{key(node)} is already queued')
    if kind == 'build' and q.build_evidence(text, user_source=bool(q.USER_SOURCE_RE.search(source))):
        raise ValueError(q.build_evidence(text, user_source=bool(q.USER_SOURCE_RE.search(source))))
    nodes.append(node)
    write_files(root, {'notebook.html': body}, {'notebook.html': rewrite(body, nodes)})
    return key(node)


def append(root, path):
    """Route source-listed framework items immediately, including otherwise waiting sub-ideas."""
    import lead_queue as q
    body = Path(path).read_text()
    articles = q.record_articles(body)
    tag, text = articles[-1] if articles else ('', '')
    q.check_source_summaries(tag, text)
    resolved = {item for group in q.listed_closures(tag, text) for item in group}
    shared = [(kind, ident) for kind, ident in q.arrivals_of(tag, text)
              if (kind, ident) not in resolved and scope(q.listed_item(kind, text, ident)[0]) == 'framework']
    if not shared:
        math, count = q.append_new(body)
        check_math_ownership(math, path, root)
        if Path(path).read_text() != body:
            raise ValueError('Notebook changed during append')
        Path(path).write_text(math)
        return math, count, 0
    notebook, relative = origin(root, path)
    originals = {relative: body}
    originals.setdefault('notebook.html', (Path(root) / 'notebook.html').read_text())
    nodes = parse(originals['notebook.html'])
    finished = closed(root)
    added = 0
    for kind, ident in shared:
        listed = q.listed_item(kind, text, ident)
        if listed and scope(listed[0]) == 'framework':
            parent = attribute(listed[0], 'data-parent')
            item = transferred(q.new_node(body, (kind, ident), require_summary=True), notebook, relative, parent)
            if key(item) not in finished:
                added += put(nodes, item)
    math, count = q.append_new(body)
    updates = {relative: math}
    updates['notebook.html'] = rewrite(math if relative == 'notebook.html' else originals['notebook.html'], nodes)
    write_files(root, originals, updates)
    return math, count, added


def migrate(root, spec):
    """Move exactly the inventoried items, preserving remaining mathematical queue order."""
    import lead_queue as q
    from notebooks import catalogue
    entries = spec['items']
    requested = {(r['notebook'], r['qualified_id']) for r in entries}
    if len(requested) != len(entries):
        raise ValueError('Migration specification repeats an item')
    books = catalogue(root)
    originals = {meta['source']: (Path(root) / meta['source']).read_text() for meta in books.values()}
    updates = dict(originals)
    central = parse(originals['notebook.html'])
    finished = closed(root)
    moved = []
    for notebook, meta in books.items():
        body = originals[meta['source']]
        found = q.parse_tree(body)
        if not found:
            continue
        retained = []
        for top in found[1]:
            keep = top.copy()
            keep.children = []
            for node in [top, *top.children]:
                if (notebook, q.qualified(node)) in requested:
                    item = transferred(node, notebook, meta['source'], q.qualified(top) if node is not top else None)
                    if key(item) not in finished:
                        put(central, item)
                    moved.append((notebook, q.qualified(node)))
                elif node is not top:
                    keep.children.append(node)
            if (notebook, q.qualified(top)) in requested:
                retained.extend(keep.children)
            else:
                retained.append(keep)
        updates[meta['source']] = q.rewrite(body, retained, q.draining_after(found[0], retained))
    available = {(attribute(n.attrs, 'data-framework-origin'), q.qualified(n)) for n in central}
    available.update(tuple(ident.split('::', 1)) for ident in finished)
    if not requested <= available:
        raise ValueError(f'Migration items missing: {sorted(requested - available)}')
    updates['notebook.html'] = rewrite(updates['notebook.html'], central)
    write_files(root, originals, updates)
    return len(moved), len(central)


def math_baseline(head, body, path, root, main_body=None):
    """Allow a transfer only when main holds an exact copy, including summary and origin."""
    import lead_queue as q
    if not head or path is None or root is None:
        return head
    before, after = q.parse_tree(head), q.parse_tree(body)
    if not before or not after or set(q.every_item(before[1])) <= set(q.every_item(after[1])):
        return head
    if main_body is None and not SECTION.search(body) and not (Path(root) / 'notebook.html').exists():
        return head
    candidate = main_body if main_body is not None else (
        body if SECTION.search(body) else (Path(root) / 'notebook.html').read_text())
    if not SECTION.search(candidate):
        return head
    notebook, relative = origin(root, path)
    central = parse(candidate)
    copies = {key(n): n for n in central}
    present = set(q.every_item(after[1]))
    retained = []
    changed = False
    for top in before[1]:
        keep = top.copy()
        keep.children = []
        removed = set()
        for node in [top, *top.children]:
            expected = transferred(node, notebook, relative, q.qualified(top) if node is not top else None)
            actual = copies.get(key(expected))
            if node.item not in present and actual and actual.text == expected.text and actual.attrs == expected.attrs:
                removed.add(node.item)
                changed = True
            elif node is not top:
                keep.children.append(node)
        retained.extend(keep.children if top.item in removed else [keep])
    return q.rewrite(head, retained, q.draining_after(before[0], retained)) if changed else head


def validate(body, path, root, head=None, ledger=None):
    """Enforce single ownership and complete metadata, independently of mathematical gates."""
    if path is None or root is None:
        return
    if not SECTION.search(body) and not (head and SECTION.search(head)):
        return
    if head and SECTION.search(head) and not SECTION.search(body):
        raise ValueError('The main notebook keeps its framework queue section even when empty')
    notebook, _ = origin(root, path)
    if SECTION.search(body) and notebook != 'main':
        raise ValueError('The framework queue lives only in the main notebook')
    nodes = parse(body)
    finished = closed(root, ledger)
    reused = {key(n) for n in nodes}.intersection(finished)
    if reused:
        raise ValueError(f'Closed framework identifiers cannot be reused: {sorted(reused)}')
    if head and notebook == 'main':
        old = {key(n): n for n in parse(head)}
        current = {key(n) for n in nodes}
        import lead_queue as q
        ledger = q.closure_ledger(root) if ledger is None else ledger
        for removed in old.keys() - current:
            row = ledger.get(('notebook.html#framework-queue', removed))
            if not row or q.closure_problems(row, root):
                raise ValueError(f'{removed} left the framework queue without a reviewed framework-close record')


def check_math_ownership(body, path, root, main_body=None, ledger=None):
    """A historical framework source cannot be promoted back into the mathematical queue."""
    import lead_queue as q
    if path is None or root is None:
        return
    if not Path(path).resolve().is_relative_to(Path(root).resolve()):
        return
    main = Path(root) / 'notebook.html'
    if main_body is None:
        if not main.exists():
            return
        main_body = body if Path(path).resolve() == main.resolve() else main.read_text()
    if not SECTION.search(main_body):
        return
    notebook, _ = origin(root, path)
    owned = {(n.kind, n.ident) for n in parse(main_body)
             if attribute(n.attrs, 'data-framework-origin') == notebook}
    for ident in closed(root, ledger):
        owner, item = ident.split('::', 1)
        if owner == notebook:
            owned.add(tuple(item.split(':', 1)))
    tree = q.parse_tree(body)
    overlap = owned.intersection(q.every_item(tree[1]) if tree else [])
    if overlap:
        raise ValueError(f'Items already owned by the framework queue: {sorted(overlap)}; use framework-status/edit/close')


def check_routed(head, body, path, root, main_body, ledger=None):
    """A commit may not retain a newly authored framework task only in a side record."""
    import lead_queue as q
    old = len(q.record_articles(head))
    shared = []
    for tag, text in q.record_articles(body)[old:]:
        resolved = {item for group in q.listed_closures(tag, text) for item in group}
        for item in q.arrivals_of(tag, text):
            if item not in resolved and scope(q.listed_item(item[0], text, item[1])[0]) == 'framework':
                shared.append(item)
    if not shared:
        return
    notebook, relative = origin(root, path)
    central = {key(n): n for n in parse(main_body)}
    finished = closed(root, ledger)
    for kind, ident in shared:
        wanted = f'{notebook}::{kind}:{ident}'
        if wanted in finished and not q.closure_problems(finished[wanted], root):
            continue
        if wanted not in central:
            raise ValueError(f'{wanted} is not in the staged main framework queue; run append and stage notebook.html')
        listed = q.item_source(body, kind, ident)
        expected = transferred(q.new_node(body, (kind, ident), require_summary=True), notebook, relative,
                               attribute(listed[0], 'data-parent'))
        if (central[wanted].text, central[wanted].attrs) != (expected.text, expected.attrs):
            raise ValueError(f'{wanted}: staged framework description or metadata differs from its new source item')


def command(root, argv):
    """Framework list/status/edit/close share origin-qualified identifiers across notebooks."""
    import argparse
    import lead_queue as q
    parser = argparse.ArgumentParser(prog='lead_queue.py ' + argv[1])
    action = argv[1]
    if action == 'migrate-framework':
        parser.add_argument('spec')
        args = parser.parse_args(argv[2:])
        moved, total = migrate(root, json.loads(Path(args.spec).read_text()))
        print(f'Moved {moved} items; {total} items in the main framework queue.')
        return 0
    if action != 'framework-list':
        parser.add_argument('item', help='ORIGIN::KIND:ID from framework-list')
    if action == 'framework-edit':
        parser.add_argument('text')
        parser.add_argument('--summary', required=True)
    if action == 'framework-close':
        parser.add_argument('--record', required=True)
        parser.add_argument('--path', action='append', required=True)
        parser.add_argument('--note', required=True)
    args = parser.parse_args(argv[2:])
    main = Path(root) / 'notebook.html'
    body = main.read_text()
    nodes = parse(body)
    if action == 'framework-list':
        for node in nodes:
            print(key(node) + '\t' + q.item_preview(node))
        return 0
    node = next((n for n in nodes if key(n) == args.item), None)
    if node is None:
        raise ValueError(f'Unknown framework item: {args.item}; use framework-list')
    if action == 'framework-status':
        print(key(node) + '\n' + html.unescape(q.strip_tags_tight(node.text)))
        print('Source: ' + str(attribute(node.attrs, 'data-framework-source')))
        if attribute(node.attrs, 'data-framework-parent'):
            print('Original parent: ' + attribute(node.attrs, 'data-framework-parent'))
        return 0
    if action == 'framework-edit':
        node.text = html.escape(args.text, quote=False)
        node.attrs = re.sub(r'\sdata-summary="[^"]*"', '', node.attrs) + q.summary_attribute(args.summary)
    else:
        row = dict(notebook='notebook.html#framework-queue', ident=key(node), text=node.text,
                   record=args.record, paths=args.path, note=args.note, date=datetime.date.today().isoformat())
        problems = q.closure_problems(row, root)
        if problems:
            raise ValueError('; '.join(problems))
        # Evidence first: interruption can leave an extra record, never an unexplained removal.
        with (Path(root) / q.CLOSURES).open('a') as stream:
            stream.write(json.dumps(row) + '\n')
        nodes.remove(node)
    write_files(root, {'notebook.html': body}, {'notebook.html': rewrite(body, nodes)})
    print(f'{action}: {args.item}; stage notebook.html' +
          (f' and {q.CLOSURES}' if action == 'framework-close' else ''))
    return 0
