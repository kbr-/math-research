#!/usr/bin/env python3
"""The lead and bridge queue (user, 3 October 2026: "I don't want promising leads/bridges to be dropped").

Every Outside lead and Absurd bridge that passed its cheap test in a route review waits in one FIFO queue,
the living section <section id="lead-queue">, the last section before the Research record.  It has no word
budget (notebook_context.py skips it) and restoration reads only its head (resume.py).  Rules, checked by
finish-turn.py against HEAD:

- The queue holds passed review items once each.  A review appends its newly passed items at the end.
- A research entry develops at most one item, always the head, tagged data-lead or data-bridge="ANCHOR:N",
  and states <strong>Follow-up.</strong> Closed (a reason the attempt found), Developed (no remaining
  application to an open statement) or Continuing (it still bears on one; user, 3 October 2026: squeeze
  items, do not close them at their first usable result).  Closed and Developed remove the item; a
  Continuing item keeps the head for up to SPELL consecutive research entries, so its context is not
  restored from scratch each time, and then moves to the tail.
- A research entry may instead settle a batch of the first items (at most TRIAGE_MAX) under <h4>Queue triage</h4>,
  one <li data-lead="ANCHOR:N"> block each, with the care each would get alone: at least TRIAGE_WORDS words, cited
  evidence, outcome Closed or Developed only.  Research entries may also carry Outside leads and Absurd bridges;
  their passed items join the tail like a review's.
- A queue audit (data-kind="audit") lists, under the same two headings, ideas that earlier reviews named outside
  the standard sections, each <li data-source="REVIEW-ANCHOR">; all its items are queued, at their source's
  place in record order when the queue is created.
- Sub-ideas sit under the item they belong to (user, 3 October 2026: "I want it to look like a nested list of
  entries"), one level deep: a sub-idea listed by an entry developing X joins X (or X's parent), one naming
  data-parent="KIND:ID" joins that item, others go to the tail.  The head or its first sub-idea may be developed;
  developing a sub-idea counts toward its parent's spell, and the parent moves to the tail with its sub-ideas.  A
  parent is not Developed while it has sub-ideas; a Closed parent closes them, except those the entry's follow-up
  list keeps Continuing, which go to the tail.  Backpressure counts top-level items.
- Sub-ideas (user, 3 October 2026): any Research-record entry may list, under <h4>Sub-ideas</h4>, questions to
  research and checks to run (<li data-sub="check">) and things to build (<li data-sub="build">) that it names and
  leaves undone; they join the tail with no test, as ANCHOR:sN, N counted over the whole list.  A check is Developed
  when the developing entry answers it citing evidence that resolves (a registered claim ID, an anchor, a repository
  file); a build when its task opens (a link to an existing tasks/ID/) or the thing exists and its path is linked.
  Every relative link of an entry developing either must resolve.
- An entry reopens an item closed too early with a follow-up list item <li data-lead="ANCHOR:N"> ending
  <strong>Follow-up.</strong> Reopened: <reason>; `append` puts it at the tail.
- Backpressure: at CAP items the section carries data-draining="true"; then every research entry develops
  the head until the queue is down to FLOOR items, when the flag is removed.
- Per notebook, the section's attributes say which entry kinds count (data-counted, default research: they
  develop items, count toward spells and are held to the head while draining), whether backpressure applies
  (data-backpressure="off" turns it off) and which modules beside this file add kinds (data-kind-modules, each
  with a kinds(lead_queue) function).  A notebook without route items is checked once it has a queue section.
- The user may pick any item out of order (user, 3 October 2026): the developing entry's tag carries
  data-picked="user" and its text a paragraph <strong>Picked.</strong> with the user's words in quotation marks.
  A picked entry satisfies draining and neither counts toward nor ends any spell.
- The user may also reorder the queue (user, 3 October 2026): an entry tagged data-picked="user", quoting them in
  its Picked. paragraph, lists under <h4>Queue order</h4> one <ol> of <li data-KIND="ID"></li>, every top-level
  item it leaves once, in the new order; sub-ideas stay under their parent.  It develops no item and settles no
  triage batch, and while the queue drains it is an uncounted kind (an audit).  `append` applies the order after
  the entry's other changes.
- An item that waits on the user's answer stays queued, marked data-waits: a follow-up list item for it ending
  <strong>Follow-up.</strong> Waiting: <the request> sets the mark, one ending Unblocked: <the answer> removes it.
  The head is the first item not waiting, and its first sub-idea not waiting; draining asks nothing when every
  item waits.

Usage: lead_queue.py init NOTEBOOK.html  (adds the section, oldest items first, if it is absent)
       lead_queue.py head NOTEBOOK.html  (the first HEAD_READ items, as restoration prints them)
       lead_queue.py done NOTEBOOK.html Closed|Developed|Continuing  (after appending the entry developing an
                                            item, and before append)
       lead_queue.py triage NOTEBOOK.html  (after appending an entry with a Queue triage batch)
       lead_queue.py append NOTEBOOK.html  (after the last entry, and done: items its follow-up list closes leave,
                                            its newly listed items join the queue, the items it reopens go to
                                            the tail, its Waiting and Unblocked marks apply)
       lead_queue.py init NOTEBOOK.html [--counted KINDS] [--backpressure off] [--kind-modules MODULES]
       lead_queue.py check NOTEBOOK.html [--base REV]  (the staged notebook against REV's, default HEAD;
                                            exit 0 when it passes, 1 when refused, 3 when it cannot run)"""
import functools
import html
import importlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

CAP, FLOOR, HEAD_READ = 50, 20, 5
SPELL = 4   # consecutive research entries a Continuing head keeps the head (user, 3 October 2026)
# A research entry may settle the first TRIAGE_MAX queue items at once (user, 3 October 2026), each with the care
# it would get alone: its own block of at least TRIAGE_WORDS words citing its evidence, outcome Closed or Developed
# only; an item still bearing on an open statement is not batched but gets its own spell.
TRIAGE_MAX, TRIAGE_WORDS = 4, 80
TRIAGE_RE = re.compile(r'<h4>Queue triage</h4>\s*<ul>(.*?)</ul>', re.S)
CLAIM_RE = re.compile(r'\b(?:lem|thm|prop|cor|conj|check|ex|def|obs|local):[A-Za-z0-9.-]+')
EVIDENCE_RE = re.compile(CLAIM_RE.pattern + r'|href="(?!https?:|mailto:)[^"]+"')
HREF_RE = re.compile(r'href="([^"]+)"')
# A file URL of this repository (build_pages.SOURCE_URL), the form notebooks link files in: its repository path.
REPO_FILE_RE = re.compile(r'https://github\.com/kbr-/math-research/(?:blob|tree)/[^/]+/([^#?]+)')
SECTION_RE = re.compile(r'<section id="lead-queue"([^>]*)>(.*?)</section>', re.S)
LEADS_RE = re.compile(r'<h4>Outside leads</h4>\s*<ul>(.*?)</ul>', re.S)
BRIDGES_RE = re.compile(r'<h4>Absurd bridges</h4>\s*<ul>(.*?)</ul>', re.S)
SUBIDEAS_RE = re.compile(r'<h4>Sub-ideas</h4>\s*<ul>(.*?)</ul>', re.S)
ORDER_RE = re.compile(r'<h4>Queue order</h4>\s*<ol>(.*?)</ol>', re.S)
TEST_PASSED = re.compile(r'<strong>Test\.</strong>\s*Passed\b')
OUTCOME_RE = re.compile(r'<strong>Follow-up\.</strong>\s*(Developed|Continuing|Closed|Reopened|Waiting|Unblocked)\b')
PICKED_RE = re.compile(r'<strong>Picked\.</strong>[^<]*?["\u201c][^"\u201d<]{3,}["\u201d]')


class Kind:
    """A kind of queue item: its name, as in data-NAME="ID" on the queue's items, developing entries and
    follow-up lists; the entry heading that lists its items (`listed`, a pattern whose group 1 is the list);
    whether that list is the shared Sub-ideas list (`sub`: items <li data-sub="NAME">, IDs ANCHOR:sN, no test);
    `rules`, per outcome (Developed, Closed, Continuing), rule(tag, text, where) giving the problems with an entry
    stating that outcome; `admit(body, head_body, item)`, for a kind whose items its own tool adds (listed=None),
    the problems with a new item; and `reopen`, whether a Reopened follow-up may reopen one."""

    def __init__(self, name, listed=None, sub=False, rules=None, admit=None, reopen=True):
        self.name, self.listed, self.sub = name, listed, sub
        self.rules, self.admit, self.reopen = rules or {}, admit, reopen


class Where:
    """What an entry's links resolve against: the notebook's text (anchors) and the repository root (claim
    registry, and relative paths, which notebooks write repository-relative, side notebooks too; `base` is None
    when the notebook's path is not known)."""

    def __init__(self, body, path=None, root=None):
        self.body, self.root = body, Path(root) if root else ROOT
        self.path = Path(path).resolve() if path else None
        self.base = self.root.resolve() if path else None
        self._claims = None

    def anchors(self):
        return set(re.findall(r'\bid="([^"]+)"', self.body))

    def claims(self):
        if self._claims is None:
            registry = self.root / 'research/claims/index.json'
            self._claims = ({c['id'] for c in json.loads(registry.read_text())['claims']}
                            if registry.exists() else set())
        return self._claims


def references(tag, text, where):
    """(unresolved links, resolved paths, resolved anchors, registered claim IDs) of an entry's text; a link to
    the entry's own anchor resolves but is no evidence, since what the entry says is cited by a claim or a file."""
    unresolved, paths, anchors = [], [], []
    known = where.anchors()
    own = re.search(r'\bid="([^"]+)"', tag)
    for href in HREF_RE.findall(text):
        repo_file = REPO_FILE_RE.fullmatch(href.split('#')[0])
        if repo_file:
            href = repo_file.group(1)
        elif href.startswith(('http:', 'https:', 'mailto:')):
            continue
        if href.startswith('#'):
            if href[1:] not in known:
                unresolved.append(href)
            elif not (own and href[1:] == own.group(1)):
                anchors.append(href)
            continue
        target = where.base / href.split('#')[0] if where.base else None
        if target is not None and where.path is not None and target.resolve() == where.path:
            fragment = href.partition('#')[2]       # the notebook itself: read as its anchor
            if fragment not in known:
                unresolved.append(href)
            elif fragment and not (own and fragment == own.group(1)):
                anchors.append(href)
            continue
        (paths if target is not None and target.exists() else unresolved).append(href)
    claims = [c for c in CLAIM_RE.findall(text) if c in where.claims()]
    return unresolved, paths, anchors, claims


def check_developed(tag, text, where):
    """A check is Developed when the entry answers it citing evidence that resolves."""
    unresolved, paths, anchors, claims = references(tag, text, where)
    problems = [f'links that do not resolve: {", ".join(unresolved)}'] if unresolved else []
    if not (paths or anchors or claims):
        problems.append('cite the evidence that answers it: a registered claim ID, an entry anchor or a '
                        'repository file')
    return problems


def build_developed(tag, text, where):
    """A build is Developed when its task opens (tasks/ID/) or the thing exists and its path is linked."""
    unresolved, paths, anchors, claims = references(tag, text, where)
    problems = [f'links that do not resolve: {", ".join(unresolved)}'] if unresolved else []
    if not paths:
        problems.append('link the opened task (tasks/ID/) or the built thing\'s path in the repository')
    return problems


KINDS = {'lead': Kind('lead', LEADS_RE), 'bridge': Kind('bridge', BRIDGES_RE),
         'check': Kind('check', SUBIDEAS_RE, sub=True, rules={'Developed': check_developed}),
         'build': Kind('build', SUBIDEAS_RE, sub=True, rules={'Developed': build_developed})}
BUILTIN = dict(KINDS)
SETTINGS = {'counted': {'research'}, 'backpressure': True, 'uncounted': [], 'guidance': []}
NAMES = '|'.join(KINDS)
FOLLOWUP_ITEM = re.compile(r'<li\b[^>]*data-(' + NAMES + r')="([^"]+)"[^>]*>(.*?)</li>', re.S)



class Live:
    """This module as kind modules see it: its names as they are when read, however it was loaded (tests load
    it by path, under no sys.modules entry), so a kind's rules see NAMES with the kinds the section added."""

    def __getattr__(self, name):
        try:
            return globals()[name]
        except KeyError:
            raise AttributeError(name) from None


LIVE = Live()


def configure(attrs):
    """Apply a queue section's attributes (a notebook without a section gets the defaults): the entry kinds
    that count, whether backpressure applies, and the kinds of the modules it names, loaded from beside this file,
    with each module's uncounted(tag, text), if it has one, naming entries of a counted kind that do not count, and
    its GUIDANCE, the cycle guidance for its kinds, which turn_guidance.py shows in place of the squeeze rule."""
    global NAMES, FOLLOWUP_ITEM
    counted = re.search(r'\bdata-counted="([^"]*)"', attrs)
    SETTINGS['counted'] = set(counted.group(1).split()) if counted else {'research'}
    SETTINGS['backpressure'] = 'data-backpressure="off"' not in attrs
    SETTINGS['uncounted'], SETTINGS['guidance'] = [], []
    KINDS.clear()
    KINDS.update(BUILTIN)
    modules = re.search(r'\bdata-kind-modules="([^"]*)"', attrs)
    if modules and modules.group(1).split():
        here = str(Path(__file__).resolve().parent)
        if here not in sys.path:
            sys.path.insert(0, here)
        for name in modules.group(1).split():
            module = importlib.import_module(name)
            for kind in module.kinds(LIVE):
                KINDS[kind.name] = kind
            if hasattr(module, 'uncounted'):
                SETTINGS['uncounted'].append(module.uncounted)
            if hasattr(module, 'GUIDANCE'):
                SETTINGS['guidance'].append(module.GUIDANCE)
    NAMES = '|'.join(KINDS)
    FOLLOWUP_ITEM = re.compile(r'<li\b[^>]*data-(' + NAMES + r')="([^"]+)"[^>]*>(.*?)</li>', re.S)


def counted(tag, text):
    """Whether an entry counts: it may develop items, its entries make spells, draining binds it.  Its kind is one
    the section counts, and no kind module calls it uncounted (business's reviews are business entries)."""
    kind = re.search(r'\bdata-kind="([^"]+)"', tag)
    return (bool(kind) and kind.group(1) in SETTINGS['counted']
            and not any(rule(tag, text) for rule in SETTINGS['uncounted']))


def picked(tag, text):
    """Whether the entry develops an item the user picked; ValueError if the tag says so without the quote."""
    if 'data-picked="user"' not in tag:
        return False
    if not PICKED_RE.search(text):
        raise ValueError('An entry tagged data-picked="user" quotes the user\'s words in a <strong>Picked.</strong> '
                         'paragraph')
    return True
ARTICLE_RE = re.compile(r'<article\b[^>]*>.*?</article>', re.S)


@functools.lru_cache(maxsize=8)
def record_articles(body):
    """(tag, text) of the Research-record articles, in order.  Cached: one check parses the same notebook
    several times (the spell and parent lookups)."""
    start = body.find('<section id="research-record">')
    if start < 0:
        return ()
    out = []
    for m in ARTICLE_RE.finditer(body, start):
        text = m.group(0)
        out.append((text[:text.index('>') + 1], text))
    return tuple(out)


def developed_by(tag, text):
    """((kind, id), outcome) for a research entry developing a queue item, or None.  The outcome is the entry's
    own: the last Follow-up outside listed items, so a quoted earlier Follow-up does not count."""
    if not counted(tag, text):
        return None
    found = re.findall(r'\bdata-(' + NAMES + r')="([^"]+)"', tag)
    if not found:
        return None
    if len(found) > 1:
        raise ValueError('A research entry develops at most one queue item: its tag names '
                         + ', '.join(i for _, i in found))
    outcomes = OUTCOME_RE.findall(FOLLOWUP_ITEM.sub('', text[len(tag):]))
    return found[0], outcomes[-1] if outcomes else None


class Node:
    """One queue item: its kind and ID, its <li> attributes and text as written, and its children (sub-ideas)."""

    def __init__(self, kind, ident, attrs, text, children=None):
        self.kind, self.ident, self.attrs, self.text = kind, ident, attrs, text
        self.children = children if children is not None else []

    @property
    def item(self):
        return self.kind, self.ident

    @property
    def waits(self):
        return 'data-waits="' in self.attrs

    def copy(self):
        return Node(self.kind, self.ident, self.attrs, self.text, [c.copy() for c in self.children])


TOKEN_RE = re.compile(r'<(/?)(li|ul|ol)\b([^>]*)>')


def parse_nodes(content):
    """The items of the queue's list, children nested one level, as Nodes; ValueError if malformed."""
    nodes, stack = [], []
    for m in TOKEN_RE.finditer(content):
        close, tag, attrs = m.groups()
        if tag != 'li':
            if tag == 'ul' and not close and stack and stack[-1].text is None:
                stack[-1].text = content[stack[-1].start:m.start()]
            continue
        if close:
            if not stack:
                raise ValueError('The queue section has an unmatched </li>')
            node = stack.pop()
            if node.text is None:
                node.text = content[node.start:m.start()]
            continue
        found = re.search(r'\bdata-(' + NAMES + r')="([^"]+)"', attrs)
        if found is None:
            raise ValueError(f'Every queue item is <li data-KIND="ID">, KIND one of {", ".join(KINDS)}: <li{attrs}>')
        node = Node(found.group(1), found.group(2), attrs, None)
        node.start = m.end()
        if len(stack) > 1:
            raise ValueError(f'Queue items nest one level only: {found.group(2)}')
        (stack[-1].children if stack else nodes).append(node)
        stack.append(node)
    if stack:
        raise ValueError(f'The queue section leaves <li> {stack[-1].ident} open')
    for node in nodes:
        for child in node.children:
            if not KINDS[child.kind].sub:
                raise ValueError(f'Only checks and builds are children: {child.ident} ({child.kind})')
    return nodes


def parse_tree(body, attrs=None):
    """(draining, [Node]) of the queue section, or None if the notebook has none; applies the section's settings,
    or those of the section attributes `attrs` when given (the draining flag stays the section's own)."""
    found = SECTION_RE.search(body)
    configure(attrs if attrs is not None else found.group(1) if found else '')
    if found is None:
        return None
    ol = re.search(r'<ol>(.*)</ol>', found.group(2), re.S)
    return 'data-draining="true"' in found.group(1), parse_nodes(ol.group(1) if ol else '')


def parse(body):
    """(draining, [(kind, id)]) of the queue's top-level items, or None if the notebook has none."""
    found = parse_tree(body)
    return None if found is None else (found[0], [n.item for n in found[1]])


def shape(nodes):
    return [(n.item, [c.item for c in n.children]) for n in nodes]


def marks(nodes):
    """The queued items marked as waiting on the user."""
    return {n.item for n in nodes if n.waits} | {c.item for n in nodes for c in n.children if c.waits}


def head_of(nodes):
    """The head: the first top-level item not waiting on the user, or None."""
    return next((n for n in nodes if not n.waits), None)


def every_item(nodes):
    return [n.item for n in nodes] + [c.item for n in nodes for c in n.children]


def locate(nodes, item):
    """(parent Node or None, Node) of a queued item, or (None, None)."""
    for node in nodes:
        if node.item == item:
            return None, node
        for child in node.children:
            if child.item == item:
                return node, child
    return None, None


def render_nodes(nodes):
    lines = []
    for node in nodes:
        children = ''
        if node.children:
            children = ('<ul>\n' + '\n'.join(f'<li{c.attrs}>{c.text}</li>' for c in node.children) + '\n</ul>')
        lines.append(f'<li{node.attrs}>{node.text}{children}</li>')
    return '\n'.join(lines)


def new_node(body, item):
    kind, ident = item
    return Node(kind, ident, f' data-{kind}="{ident}"',
                f'<a href="#{ident.rsplit(":", 1)[0]}">{ident}</a> ({kind}): {item_text(body, kind, ident)}')


def rewrite(body, nodes, draining):
    """The notebook with the queue section's list replaced by `nodes` and its draining flag set as given."""
    found = SECTION_RE.search(body)
    attrs = re.sub(r'\s*data-draining="[^"]*"', '', found.group(1)) + (' data-draining="true"' if draining else '')
    inner = re.sub(r'<ol>.*</ol>', lambda m: '<ol>\n' + render_nodes(nodes) + '\n</ol>', found.group(2), flags=re.S)
    return body[:found.start()] + f'<section id="lead-queue"{attrs}>{inner}</section>' + body[found.end():]


def draining_after(was, nodes):
    """Backpressure counts top-level items: on at CAP, off once down to FLOOR; never where the section turns it
    off."""
    if not SETTINGS['backpressure']:
        return False
    return len(nodes) > FLOOR if was else len(nodes) >= CAP


def wait_changes(text):
    """{item: reference or None} of an entry's Waiting (set the mark) and Unblocked (remove it) follow-ups."""
    out = {}
    for kind, item_id, item in FOLLOWUP_ITEM.findall(text):
        outcome = OUTCOME_RE.search(item)
        if outcome and outcome.group(1) == 'Waiting':
            rest = item[outcome.end():]
            link = re.search(r'href="([^"]*USER_REQUESTS\.md)"', rest)
            number = re.search(r'\bitem (\d+)', re.sub(r'<[^>]+>', ' ', rest))
            plain = re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', rest)).strip(' :.')
            out[(kind, item_id)] = (link.group(1) + (f' item {number.group(1)}' if number else '') if link
                                    else plain[:80])
        elif outcome and outcome.group(1) == 'Unblocked':
            out[(kind, item_id)] = None
    return out


def apply_marks(nodes, text):
    """Set or remove data-waits on queued items as the entry's Waiting and Unblocked follow-ups say."""
    for item, ref in wait_changes(text).items():
        node = locate(nodes, item)[1]
        if node is None:
            continue
        node.attrs = re.sub(r'\s*data-waits="[^"]*"', '', node.attrs)
        if ref is not None:
            node.attrs += f' data-waits="{html.escape(ref or "the user", quote=True)}"'


def check_waits(text, where):
    """Problems with an entry's Waiting follow-ups: each names its request; a task's request must exist."""
    problems = []
    for item, ref in wait_changes(text).items():
        if ref is None:
            continue
        if not ref:
            problems.append(f'{item[1]}: a Waiting follow-up names the request it waits on')
            continue
        task = re.match(r'(\S*USER_REQUESTS\.md)(?: item (\d+))?$', ref)
        if task:
            listing = (where.base or where.root) / task.group(1)
            record = listing.parent / 'task.json'
            if not listing.exists() or not record.exists():
                problems.append(f'{item[1]}: {task.group(1)} does not resolve to a task\'s requests')
            elif not task.group(2):
                problems.append(f'{item[1]}: name the request as "item N" after the link to {task.group(1)}')
            elif int(task.group(2)) not in {r['number'] for r in json.loads(record.read_text())['requests']}:
                problems.append(f'{item[1]}: {task.group(1)} has no open request {task.group(2)}')
    return problems


@functools.lru_cache(maxsize=4)
def reopenings(body):
    """{item: positions in the record of the entries reopening it}."""
    out = {}
    for position, (_, text) in enumerate(record_articles(body)):
        for item in reopened_by(text):
            out.setdefault(item, []).append(position)
    return out


def reopened_before(body, item, position):
    """Whether an entry before `position` in the record (anywhere, for None) reopens `item`."""
    return any(position is None or at < position for at in reopenings(body).get(item, []))


def record_parent(body, item, position=None):
    """The parent a sub-idea's own listing named: its data-parent, else the item its listing entry developed
    (or that item's own parent); None for a top-level kind, a listing with neither, or an item reopened before
    `position` (the whole record, for None), which returned at the top level then."""
    kind, ident = item
    if not KINDS[kind].sub or reopened_before(body, item, position):
        return None
    anchor = ident.rsplit(':', 1)[0]
    for tag, text in record_articles(body):
        if f'id="{anchor}"' not in tag:
            continue
        listed = listed_item(kind, text, ident)
        named = re.search(r'\bdata-parent="(' + NAMES + r'):([^"]+)"', listed[0]) if listed else None
        if named:
            parent = (named.group(1), named.group(2))
        else:
            work = developed_by(tag, text)
            parent = work[0] if work else None
        if parent and KINDS[parent[0]].sub:
            return record_parent(body, parent, position) or parent
        return parent
    return None


def group_of(body, nodes, item, position=None):
    """The top-level item whose spell an entry developing `item` counts toward; for the entry at `position` in
    the record, as the record stood then: before a reopen of the item, its listing's parent."""
    if position is not None and item in reopenings(body) and not reopened_before(body, item, position):
        return record_parent(body, item, position) or item
    parent, node = locate(nodes, item)
    if parent is not None:
        return parent.item
    if node is not None:
        return item
    return record_parent(body, item, position) or item


def spell(body, item, nodes=None, end=None):
    """Research entries, from the record's end, that developed `item` or one of its children since it became
    the head: entries that develop no queue item (reviews, other research) neither count nor break the run, which
    ends at an entry developing another item or settling a triage batch.  `nodes`, the queue the children are
    looked up in, defaults to `body`'s; the check passes the queue before the last entry, which still holds a
    child that entry closed.  `end` cuts the record before that many articles from its end."""
    if nodes is None:
        found = parse_tree(body)
        nodes = found[1] if found else []
    count = 0
    articles = record_articles(body)[:end]
    for position in range(len(articles) - 1, -1, -1):
        tag, text = articles[position]
        if not counted(tag, text) or 'data-picked="user"' in tag:
            continue
        work = developed_by(tag, text)
        if triaged(tag, text) or (work and group_of(body, nodes, work[0], position) != item):
            break
        if work:
            count += 1
    return count


def kept_children(text):
    """Items a follow-up list marks Continuing: children kept when their parent closes."""
    return {(kind, item_id) for kind, item_id, item in FOLLOWUP_ITEM.findall(text)
            if (OUTCOME_RE.search(item) or [None, None])[1] == 'Continuing'}


def close(nodes, item, kept, promoted):
    """Remove a queued item; a closed parent's children close with it unless kept, which go to `promoted`."""
    parent, node = locate(nodes, item)
    if node is None:
        return
    if parent is not None:
        parent.children.remove(node)
        return
    nodes.remove(node)
    promoted += [c for c in node.children if c.item in kept]


def placement(body, nodes, tag, text, item, audit):
    """The top-level Node a listed sub-idea joins as a child, or None for the top level; ValueError for a named
    parent that is not queued, except in an audit, which seeds like init."""
    kind, ident = item
    listed = listed_item(kind, text, ident)
    named = re.search(r'\bdata-parent="(' + NAMES + r'):([^"]+)"', listed[0]) if listed else None
    if named:
        target = (named.group(1), named.group(2))
    else:
        work = developed_by(tag, text)
        target = work[0] if work else None
    if target is None:
        return None
    # A developed sub-idea is already gone once done has run: its new sub-ideas join its parent.
    for candidate in (target, None if named else record_parent(body, target)):
        if candidate is None:
            continue
        parent, node = locate(nodes, candidate)
        if parent is not None:
            return parent
        if node is not None:
            return node
    if named and not audit:
        raise ValueError(f'{ident} names a parent that is not queued: {target[0]}:{target[1]}')
    return None


def place_arrivals(body, nodes, tag, text, listed, reopened):
    """Add new items: listed sub-ideas under their parent or at the tail, other listed items and reopened items
    (whose parent may be gone) at the tail."""
    audit = 'data-kind="audit"' in tag
    queued = set(every_item(nodes))
    for item in dict.fromkeys(listed + reopened):
        if item in queued:
            continue
        sub = KINDS[item[0]].sub and item in listed and item not in reopened
        parent = placement(body, nodes, tag, text, item, audit) if sub else None
        (parent.children if parent is not None else nodes).append(new_node(body, item))
        queued.add(item)


def arrivals_of(tag, text):
    """Items one article adds, as (kind, id): its passed Outside leads and Absurd bridges (reviews, research
    entries, which may carry their own, user, 3 October 2026, and audits, all of whose items are queued), then
    the Sub-ideas any entry lists (no test: when unsure, queue it)."""
    ident = re.search(r'\bid="([^"]+)"', tag)
    if not ident:
        return []
    audit = 'data-kind="audit"' in tag
    tested = re.search(r'data-kind="(?:review|research|audit)"', tag)
    out, walked = [], set()
    for kind in KINDS.values():
        section = kind.listed.search(text) if kind.listed else None
        if not section or (not kind.sub and not tested) or kind.listed in walked:
            continue
        walked.add(kind.listed)     # a list several kinds share (Sub-ideas) is walked once, in its order
        subs = {k.name for k in KINDS.values() if k.sub and k.listed is kind.listed}
        for n, item in enumerate(re.findall(r'<li\b(.*?)</li>', section.group(1), re.S), 1):
            if kind.sub:
                sub = re.match(r'[^>]*\bdata-sub="([^"]+)"', item)
                if sub and sub.group(1) in subs:
                    out.append((sub.group(1), f'{ident.group(1)}:s{n}'))
            elif audit or TEST_PASSED.search(item):
                out.append((kind.name, f'{ident.group(1)}:{n}'))
    return out


def listed_item(kind, text, ident):
    """The <li> attributes and content of a listed item ANCHOR:N or ANCHOR:sN in an article's text, or None."""
    if KINDS[kind].listed is None or ':' not in ident:
        return None
    n = ident.rsplit(':', 1)[1].lstrip('s')
    section = KINDS[kind].listed.search(text)
    items = re.findall(r'<li\b([^>]*)>(.*?)</li>', section.group(1), re.S) if section else []
    return items[int(n) - 1] if n.isdigit() and 0 < int(n) <= len(items) else None


def triaged(tag, text):
    """[((kind, id), outcome, words, has_evidence, text)] of a counted entry's Queue triage list, in order."""
    if not counted(tag, text):
        return []
    section = TRIAGE_RE.search(text)
    if not section:
        return []
    out = []
    for kind, item_id, item in FOLLOWUP_ITEM.findall(section.group(1)):
        outcome = OUTCOME_RE.search(item)
        words = len(re.sub(r'<[^>]+>', ' ', item).split())
        out.append(((kind, item_id), outcome.group(1) if outcome else None, words, bool(EVIDENCE_RE.search(item)),
                    item))
    return out


def listed_outcomes(text):
    """[((kind, id), outcome, text)] of a follow-up list's items outside a Queue triage batch."""
    section = TRIAGE_RE.search(text)
    rest = text.replace(section.group(0), '') if section else text
    return [((kind, item_id), (OUTCOME_RE.search(item) or [None, None])[1], item)
            for kind, item_id, item in FOLLOWUP_ITEM.findall(rest)]


def kind_rule_problems(tag, blocks, where):
    """Problems the item kinds' rules find with the outcomes stated in `blocks`, [((kind, id), outcome, text)]."""
    problems = []
    for (kind, ident), outcome, text in blocks:
        rule = KINDS[kind].rules.get(outcome) if kind in KINDS else None
        problems += [f'{ident} ({kind}), {outcome}: {p}' for p in (rule(tag, text, where) if rule else [])]
    return problems


def subidea_problems(text):
    """Problems with the form of an entry's Sub-ideas list: each item names a sub-idea kind, and a parent it
    names is KIND:ID with a known KIND."""
    section = SUBIDEAS_RE.search(text)
    problems = []
    subs = [k.name for k in KINDS.values() if k.sub]
    for n, attrs in enumerate(re.findall(r'<li\b([^>]*)>', section.group(1)) if section else [], 1):
        sub = re.search(r'\bdata-sub="([^"]*)"', attrs)
        if not sub or sub.group(1) not in subs:
            problems.append(f'Sub-ideas item {n} needs data-sub, one of {", ".join(subs)}')
        parent = re.search(r'\bdata-parent="([^"]*)"', attrs)
        if parent and not re.fullmatch(r'(?:' + NAMES + r'):\S+', parent.group(1)):
            problems.append(f'Sub-ideas item {n}: data-parent is KIND:ID, KIND one of {", ".join(KINDS)}')
    return problems


def listed_closures(tag, text):
    """Items a follow-up list (outside a Queue triage batch) marks Closed, and items it marks Developed."""
    section = TRIAGE_RE.search(text)
    rest = text.replace(section.group(0), '') if section else text
    closed, developed = [], []
    for kind, item_id, item in FOLLOWUP_ITEM.findall(rest):
        outcome = OUTCOME_RE.search(item)
        if outcome and outcome.group(1) == 'Closed':
            closed.append((kind, item_id))
        elif outcome and outcome.group(1) == 'Developed':
            developed.append((kind, item_id))
    return closed, developed


def ordered(tag, text, nodes):
    """`nodes` (top-level Nodes, as the entry's other changes leave them) in the order the entry's Queue order
    section gives, or unchanged without one; ValueError for an order the user did not give, or that is not exactly
    the remaining top-level items, each once and with no outcome."""
    section = ORDER_RE.search(text)
    if not section:
        return nodes
    if 'data-picked="user"' not in tag:
        raise ValueError('A Queue order is the user\'s: tag the entry data-picked="user" and quote their words in a '
                         '<strong>Picked.</strong> paragraph')
    if developed_by(tag, text) or triaged(tag, text):
        raise ValueError('An entry with a Queue order develops no item and settles no triage batch: the order '
                         'moves the head')
    listed = FOLLOWUP_ITEM.findall(section.group(1))
    if [i for _, i, item in listed if OUTCOME_RE.search(item)]:
        raise ValueError('Queue order items carry no outcome: close or develop an item in the follow-up list')
    order = [(kind, ident) for kind, ident, _ in listed]
    top = [n.item for n in nodes]
    if len(set(order)) != len(order):
        raise ValueError('A Queue order lists each item once')
    nested = [i for k, i in order if (k, i) not in top and (k, i) in every_item(nodes)]
    if nested:
        raise ValueError('A Queue order lists top-level items only; sub-ideas keep their place under their '
                         'parent: ' + ', '.join(nested))
    if set(order) != set(top):
        missing = [i for k, i in top if (k, i) not in order]
        unknown = [i for k, i in order if (k, i) not in top]
        raise ValueError('A Queue order lists every remaining top-level item: missing '
                         + (', '.join(missing) or 'none') + '; not queued ' + (', '.join(unknown) or 'none'))
    place = {item: n for n, item in enumerate(order)}
    return sorted(nodes, key=lambda node: place[node.item])


def reopened_by(text):
    """Items an entry reopens: follow-up list items whose outcome is Reopened."""
    return [(kind, item_id) for kind, item_id, item in FOLLOWUP_ITEM.findall(text)
            if (OUTCOME_RE.search(item) or [None, None])[1] == 'Reopened']


def audit_source(text, item):
    """The data-source anchor of an audit's listed item (kind, 'ANCHOR:N' or 'ANCHOR:sN'), or None."""
    listed = listed_item(item[0], text, item[1])
    found = re.search(r'data-source="([^"]+)"', listed[0]) if listed else None
    return found.group(1) if found else None


def item_text(body, kind, ident):
    """A short description of a listed item, for the queue line."""
    anchor = ident.rsplit(':', 1)[0]
    art = re.search(r'<article\b[^>]*\bid="' + re.escape(anchor) + r'"[^>]*>.*?</article>', body, re.S)
    listed = listed_item(kind, art.group(0), ident) if art else None
    if listed is None:
        return ''
    # the entry's text is HTML: unescape it before the queue line escapes it, so an entity is not escaped twice
    text = html.unescape(re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', '', listed[1])).strip())
    short = text[:220]
    while short.count('\\(') > short.count('\\)'):   # never cut inside inline math
        short = short[:short.rindex('\\(')].rstrip()
    return html.escape(short + ('…' if len(short) < len(text) else ''), quote=False)


def check_triage(batch, old):
    """The rigor rules of a Queue triage batch against the queue's top-level Nodes `old` before the entry."""
    if len(batch) > TRIAGE_MAX:
        raise ValueError(f'A Queue triage batch settles at most {TRIAGE_MAX} items, each with full care')
    items = [b[0] for b in batch]
    active = [n for n in old if not n.waits]
    if items != [n.item for n in active[:len(items)]]:
        raise ValueError('A Queue triage batch takes the first items of the queue not waiting on the user, in '
                         'order: expected ' + ', '.join(n.ident for n in active[:len(items)]))
    for ((kind, ident), outcome, words, evidence, _), node in zip(batch, active):
        if outcome not in ('Closed', 'Developed'):
            raise ValueError(f'Triage item {ident}: a batch only closes or develops ("<strong>Follow-up.</strong> '
                             'Closed: ..." or "Developed ..."); an item still bearing on an open statement gets its '
                             'own spell, so end the batch before it')
        if outcome == 'Developed' and node.children:
            raise ValueError(f'Triage item {ident} still has open sub-ideas, so it is not Developed')
        if words < TRIAGE_WORDS:
            raise ValueError(f'Triage item {ident}: {words} words; each batched item gets the care it would get '
                             f'alone, at least {TRIAGE_WORDS} words of what was checked and why (user, 3 October 2026)')
        if not evidence:
            raise ValueError(f'Triage item {ident}: cite the evidence for the outcome (a claim ID, an entry '
                             'anchor link or a repository file)')


def open_tree(body):
    """The queue's initial contents: listed items, in record order, that no follow-up list item has Closed (and
    not Reopened since), nor, for a sub-idea, an entry developing it Closed or Developed; a sub-idea goes under
    its parent when that is a queued top-level item, else to the top level (when unsure, queue it).  Once a queue
    exists, its changes are checked as transitions from HEAD (check), not recomputed from the history, whose older
    entries used Developed and Continuing for progress."""
    passed, closed, place = [], {}, {}
    articles = record_articles(body)
    for position, (tag, text) in enumerate(articles):
        ident = re.search(r'\bid="([^"]+)"', tag)
        place[ident.group(1) if ident else None] = position
        for item in arrivals_of(tag, text):
            source = audit_source(text, item) if 'data-kind="audit"' in tag else None
            passed.append((place.get(source, position), item))
        work = developed_by(tag, text)
        if work and KINDS[work[0][0]].sub and work[1] in ('Closed', 'Developed'):
            closed[work[0]] = True
        for kind, item_id, item in FOLLOWUP_ITEM.findall(text):
            outcome = OUTCOME_RE.search(item)
            if outcome and outcome.group(1) in ('Closed', 'Reopened'):
                closed[(kind, item_id)] = outcome.group(1) == 'Closed'
    nodes, top = [], {}
    # stable: an audit's items take their source's place in record order
    for _, item in sorted(passed, key=lambda pair: pair[0]):
        if closed.get(item) or item in top:
            continue
        parent = record_parent(body, item) if KINDS[item[0]].sub else None
        if parent in top:
            top[parent].children.append(new_node(body, item))
            continue
        top[item] = new_node(body, item)
        nodes.append(top[item])
    return nodes


def open_items(body):
    """The top-level items open_tree would queue, in order."""
    return [n.item for n in open_tree(body)]


def render(body, nodes, draining, attrs=''):
    flag = attrs + (' data-draining="true"' if draining else '')
    return (f'<section id="lead-queue"{flag}>\n<h2>Lead and bridge queue</h2>\n<p>Passed Outside leads and Absurd '
            'bridges and listed sub-ideas awaiting development, oldest first (FIFO), each sub-idea under the item '
            'it belongs to; rules in <code>tools/lead_queue.py</code>.</p>\n<ol>\n'
            + render_nodes(nodes) + '\n</ol>\n</section>\n')


def transition(body, old, tag, text):
    """The queue `old` (top-level Nodes before the entry) as the entry (tag, text) leaves it."""
    nodes = [n.copy() for n in old]
    work, batch = developed_by(tag, text), triaged(tag, text)
    chosen = 'data-picked="user"' in tag
    closed, _ = listed_closures(tag, text)
    kept, promoted = kept_children(text), []
    for item in closed + [b[0] for b in batch]:
        close(nodes, item, kept, promoted)
    parent, node = locate(nodes, work[0]) if work else (None, None)
    if work and work[1] in ('Closed', 'Developed'):
        close(nodes, work[0], kept, promoted)
        end_spell(body, nodes, parent, chosen, old)  # a developed or closed sub-idea's entry counts for its parent
    elif work and work[1] == 'Continuing':
        end_spell(body, nodes, parent if parent is not None else node, chosen, old)
    nodes += promoted
    place_arrivals(body, nodes, tag, text, arrivals_of(tag, text), reopened_by(text))
    apply_marks(nodes, text)
    return ordered(tag, text, nodes)


def check(head_body, body, path=None, root=None):
    """Raise ValueError if the queue in `body` breaks the rules relative to `head_body` (HEAD's notebook).
    The entry checked is the last Research-record article of `body`; `path` is the notebook's file, against whose
    directory its relative links resolve, and `root` the repository (default: this one)."""
    # both sections are read under the committed notebook's settings, so a commit changing them (business's move
    # from data-items="ideas" to its kind module) reads HEAD's items as the notebook now means them
    section = SECTION_RE.search(body)
    before = parse_tree(head_body, section.group(1) if section else None) if head_body else None
    now = parse_tree(body)
    if before is not None and now is None:
        raise ValueError('The lead and bridge queue section is gone: a notebook keeps its queue once it has one')
    if not re.search(r'data-route-item="', body) and now is None:
        return
    if now is None:
        raise ValueError('The notebook needs its lead and bridge queue: run python3 tools/lead_queue.py init '
                         'NOTEBOOK.html, with the --counted, --backpressure and --kind-modules options its branch '
                         'uses, review the section, and commit it with this entry (AGENTS.md)')
    draining, nodes = now
    items = every_item(nodes)
    if len(set(items)) != len(items):
        raise ValueError('The lead and bridge queue lists an item twice')
    articles = record_articles(body)
    fresh = head_body is None or len(articles) > len(record_articles(head_body))
    tag, text = articles[-1] if articles and fresh else ('', '')     # only a new entry's work is checked
    where = Where(body, path, root)
    work = developed_by(tag, text)
    batch = triaged(tag, text)
    chosen = picked(tag, text)
    if work and batch:
        raise ValueError('An entry either develops the head (data-lead or data-bridge) or settles a Queue triage '
                         'batch, not both')
    if work and work[1] not in ('Closed', 'Developed', 'Continuing'):
        raise ValueError('An entry developing a queue item states "<strong>Follow-up.</strong> Closed: <reason>", '
                         '"Developed ..." or "Continuing ..."')
    rule = KINDS[work[0][0]].rules.get(work[1]) if work else None
    problems = rule(tag, text, where) if rule else []
    if problems:
        raise ValueError(f'{work[0][1]} ({work[0][0]}), {work[1]}: ' + '; '.join(problems))
    problems = check_waits(text, where)
    if problems:
        raise ValueError('Waiting follow-ups: ' + '; '.join(problems))
    problems = subidea_problems(text)
    if problems:
        raise ValueError('; '.join(problems))
    problems = kind_rule_problems(tag, [(b[0], b[1], b[4]) for b in batch] + listed_outcomes(text), where)
    if problems:
        raise ValueError('; '.join(problems))
    if head_body is not None and len(articles) - len(record_articles(head_body)) > 1:
        raise ValueError('Commit one Research-record entry at a time: each entry\'s queue change is checked '
                         'against the commit before it')
    if not fresh and before is not None:
        if shape(nodes) != shape(before[1]) or marks(nodes) != marks(before[1]) or draining != before[0]:
            raise ValueError('A commit that adds no Research-record entry leaves the queue as it was')
        return
    if before is None:
        if work or batch:
            raise ValueError('The commit that creates the queue may not develop queue items: run lead_queue.py init, '
                             'commit the section, then develop its head')
        wanted = open_tree(body)
        admitted = [n for n in nodes if KINDS[n.kind].admit is not None]
        for node in admitted:
            problems = KINDS[node.kind].admit(body, head_body, node.item)
            if problems:
                raise ValueError(f'{node.ident} ({node.kind}) may not join the queue: ' + '; '.join(problems))
        seeded = [n for n in nodes if n not in admitted]
        items = every_item(seeded)
        if shape(seeded) != shape(wanted) or marks(nodes):
            have, want = set(items), set(every_item(wanted))
            raise ValueError('A new queue holds exactly the listed items not closed, sub-ideas under their parents: '
                             'missing ' + (', '.join(i for _, i in want - have) or 'none') + '; not open '
                             + (', '.join(i for _, i in have - want) or 'none') + '; otherwise the placement differs '
                             '(lead_queue.py init writes it)')
        if draining != draining_after(False, nodes):
            raise ValueError(f'The queue has {len(nodes)} top-level items: data-draining="true" must be '
                             + ('set' if not draining else 'absent') + f' (on at {CAP} items unless backpressure is '
                             'off)')
        return
    every = {item for t, x in articles for item in arrivals_of(t, x)}
    reopened = reopened_by(text)
    unknown = [i for k, i in reopened if (k, i) not in every and KINDS[k].admit is None]
    if unknown:
        raise ValueError('Reopened items must be passed review items or listed sub-ideas: ' + ', '.join(unknown))
    barred = [i for k, i in reopened if not KINDS[k].reopen]
    if barred:
        raise ValueError('These items are not reopened by a follow-up; their kind has its own way back: '
                         + ', '.join(barred))
    was_draining, old = before
    old = settle(head_body, [n.copy() for n in old])
    if batch:
        check_triage(batch, old)
    closed, developed = listed_closures(tag, text)
    listed_developed = [i for k, i in developed if (k, i) in every_item(old)]
    if listed_developed:
        raise ValueError('A follow-up list may mark a queued item Closed (it leaves the queue), Continuing or '
                         'Reopened; Developed is said by a research entry developing it: ' + ', '.join(listed_developed))
    head = head_of(old)
    first = next((c for c in head.children if not c.waits), None) if head else None
    if work:
        located = locate(old, work[0])[1]
        if located is None:
            raise ValueError(f'{work[0][1]} is not queued')
        if not chosen and work[0] not in [n.item for n in (head, first) if n is not None]:
            raise ValueError(f'Queue items are developed oldest first: this entry develops {work[0][1]}, but the '
                             f'head is {head.ident if head else "none (every item waits)"}' + (f' and its first '
                             f'sub-idea {first.ident}' if first else '') + '; the user may pick another (data-picked)')
        if work[1] == 'Developed' and [c for c in located.children if c.item not in closed]:
            raise ValueError(f'{work[0][1]} still has open sub-ideas, so it is not Developed; it is Continuing')
    draining_before = SETTINGS['backpressure'] and (was_draining or len(old) >= CAP)
    if draining_before and counted(tag, text) and not work and not batch and head is not None:
        raise ValueError(f'The queue is draining ({len(old)} items; backpressure from {CAP} until {FLOOR}): this '
                         f'entry must develop the head, {head.ident}, tagged data-{head.kind}="{head.ident}", '
                         'or its first sub-idea')
    expected = transition(body, old, tag, text)
    known = set(every_item(old)) | set(every_item(expected))
    for node in nodes:
        if node.item in known or KINDS[node.kind].admit is None:
            continue
        problems = KINDS[node.kind].admit(body, head_body, node.item)
        if problems:
            raise ValueError(f'{node.ident} ({node.kind}) may not join the queue: ' + '; '.join(problems))
        expected.append(node.copy())
    if shape(nodes) != shape(expected):
        raise ValueError('Queue update: keep the earlier items in order; remove a Closed or Developed item (a closed '
                         'parent\'s sub-ideas close with it unless a follow-up keeps one Continuing, which goes to the '
                         'tail); if Continuing, keep the head until its ' + str(SPELL) + 'th consecutive entry, then '
                         'move it, with its sub-ideas, to the tail; append this entry\'s newly listed items (sub-ideas '
                         'under their parent) and the items it reopens. Expected: '
                         + '; '.join(f'{i[1]}' + (' [' + ', '.join(c[1] for c in cs) + ']' if cs else '')
                                     for i, cs in shape(expected)))
    if marks(nodes) != marks(expected):
        raise ValueError('Waiting marks: data-waits is set by a Waiting follow-up and removed by an Unblocked one, '
                         'and changes no other way (lead_queue.py append applies them). Expected waiting: '
                         + (', '.join(i for _, i in marks(expected)) or 'none'))
    should_drain = draining_after(draining_before, nodes)
    if draining != should_drain:
        raise ValueError(f'The queue has {len(nodes)} top-level items: data-draining="true" must be '
                         + ('set' if should_drain else 'removed') + (f' (on at {CAP} items, off at {FLOOR})'
                                                                      if SETTINGS['backpressure'] else
                                                                      ' (backpressure is off here)'))


def waiting_note(node):
    """' [waiting: REFERENCE]' for an item waiting on the user, else ''."""
    found = re.search(r'data-waits="([^"]*)"', node.attrs)
    return f' [waiting: {html.unescape(found.group(1))}]' if found else ''


def head_lines(body, count=HEAD_READ):
    found = parse_tree(body)
    if found is None:
        return []
    draining, nodes = found
    settle(body, nodes)
    state = f'draining (backpressure from {CAP} until {FLOOR})' if draining or len(nodes) >= CAP else 'not draining'
    out = [f'{len(nodes)} items, {state}; restoration shows the first {min(count, len(nodes))}.']
    def plain(node):     # with its ID first, which a lead's text has and an idea's (business) has not
        text = html.unescape(re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', '', node.text)).strip())
        return text if text.startswith(node.ident) else f'{node.ident}: {text}'
    for n, node in enumerate(nodes[:count], 1):
        out.append(f'{n}. {plain(node)}{waiting_note(node)}')
        out += [f'   - {plain(c)}{waiting_note(c)}' for c in node.children]
    return out


def settle(body, nodes, end=None):
    """`nodes` with the head moved to the tail if the record (cut by `end`, as in `spell`) already owes it that
    move: its spell is complete though the queue still has it first, as a queue committed before a spell rule was
    enforced can.  On a queue the tools kept, the head's spell is under SPELL and nothing moves."""
    head = head_of(nodes)
    if head is not None and len(nodes) > 1 and spell(body, head.item, nodes, end) >= SPELL:
        nodes.remove(head)
        nodes.append(head)
    return nodes


def end_spell(body, nodes, top, picked, before=None):
    """Move `top` with its sub-ideas to the tail when it is the head and the entry ending `body` is the SPELLth of
    its spell, counted against the queue `before` that entry (default: `body`'s); a picked entry neither counts
    toward nor ends a spell."""
    if (top is not None and top in nodes and not picked and top is head_of(nodes)
            and spell(body, top.item, before) >= SPELL):
        nodes.remove(top)
        nodes.append(top)


def done(body, outcome):
    """The notebook with the item the last entry develops removed (Closed, Developed; a parent's sub-ideas close
    with it unless the entry keeps one Continuing, which goes to the tail), or kept (Continuing: a head keeps its
    place before its SPELLth consecutive entry, then moves with its sub-ideas to the tail), and the draining flag
    recomputed from the previous state.  Run it after appending the developing entry and before `append`."""
    found = parse_tree(body)
    if found is None:
        raise ValueError('No lead and bridge queue')
    draining, nodes = found
    if not nodes:
        raise ValueError('The queue is empty')
    settle(body, nodes, end=-1)
    if outcome not in ('Closed', 'Developed', 'Continuing'):
        raise ValueError('Outcome is Closed, Developed or Continuing')
    was = draining or len(nodes) >= CAP
    articles = record_articles(body)
    tag, text = articles[-1] if articles else ('', '')
    work = developed_by(tag, text)
    if not work:
        raise ValueError('Append the entry developing the item first: done acts on the last entry\'s item')
    if work[1] != outcome:
        raise ValueError(f'The last entry states {work[1]} for {work[0][1]}, not {outcome}')
    if locate(nodes, work[0])[1] is None:
        raise ValueError(f'{work[0][1]} is not queued (has done already run?)')
    item = work[0]
    parent, node = locate(nodes, item)
    picked = 'data-picked="user"' in tag
    if outcome == 'Continuing':
        end_spell(body, nodes, parent if parent is not None else node, picked)
    else:
        promoted = []
        close(nodes, item, kept_children(text) if work else set(), promoted)
        end_spell(body, nodes, parent, picked)       # a developed or closed sub-idea's entry counts for its parent
        nodes += promoted
    return rewrite(body, nodes, draining_after(was, nodes))


def settle_triage(body):
    """The notebook with the last entry's Queue triage items removed from the queue's head."""
    found = parse_tree(body)
    if found is None:
        raise ValueError('No lead and bridge queue')
    draining, nodes = found
    was = draining or len(nodes) >= CAP
    articles = record_articles(body)
    tag, text = articles[-1] if articles else ('', '')
    batch = triaged(tag, text)
    if not batch:
        raise ValueError('The last entry has no Queue triage list')
    check_triage(batch, nodes)
    promoted = []
    for item in [b[0] for b in batch]:
        close(nodes, item, kept_children(text), promoted)
    nodes += promoted
    return rewrite(body, nodes, draining_after(was, nodes)), len(batch)


def append_new(body):
    """The notebook with the items the last entry's follow-up list marks Closed removed (their sub-ideas with
    them, but for those it keeps Continuing, which go to the tail), its newly listed items added (sub-ideas under
    their parent, the rest and the items it reopens at the tail), and the draining flag recomputed; with the number
    of items added."""
    found = parse_tree(body)
    if found is None:
        raise ValueError('No lead and bridge queue')
    draining, nodes = found
    articles = record_articles(body)
    tag, text = articles[-1] if articles else ('', '')
    work = developed_by(tag, text)
    if work and work[1] in ('Closed', 'Developed') and locate(nodes, work[0])[1] is not None:
        raise ValueError(f'Run done first: the entry {work[1].lower()} {work[0][1]}, which is still queued, and '
                         'its new sub-ideas go where the queue is after that')
    problems = subidea_problems(text)
    if problems:
        raise ValueError('; '.join(problems))
    was = draining or len(nodes) >= CAP
    promoted = []
    for item in listed_closures(tag, text)[0]:
        close(nodes, item, kept_children(text), promoted)
    nodes += promoted
    before = len(every_item(nodes))
    place_arrivals(body, nodes, tag, text, arrivals_of(tag, text), reopened_by(text))
    apply_marks(nodes, text)
    nodes = ordered(tag, text, nodes)
    return rewrite(body, nodes, draining_after(was, nodes)), len(every_item(nodes)) - before


def staged_check(notebook, base='HEAD'):
    """Check the staged copy of `notebook` against its copy at `base`: (exit status, message): 0 when it passes,
    1 when the queue breaks a rule, 3 when the check cannot run (no repository, nothing staged, no such base);
    2 stays the usage error's, which a caller reads as a tool without this command."""
    path = Path(notebook).resolve()
    # a pre-commit hook inherits GIT_DIR, under which --show-toplevel answers the current directory: find the
    # repository from the notebook's own place (GIT_INDEX_FILE stays, so the hook's index is the one read)
    env = {k: v for k, v in os.environ.items() if k not in ('GIT_DIR', 'GIT_WORK_TREE')}
    git = functools.partial(subprocess.run, capture_output=True, text=True, env=env)
    top = git(['git', 'rev-parse', '--show-toplevel'], cwd=path.parent)
    if top.returncode != 0:
        return 3, f'{notebook} is not in a git repository'
    root = Path(top.stdout.strip())
    relative = path.relative_to(root).as_posix()
    staged = git(['git', 'show', f':{relative}'], cwd=root)
    if staged.returncode != 0:
        return 3, f'{relative} is not staged'
    known = git(['git', 'rev-parse', '--verify', '--quiet', f'{base}^{{commit}}'], cwd=root)
    if known.returncode != 0:
        return 3, f'{base} is no commit in this repository'
    head = git(['git', 'show', f'{base}:{relative}'], cwd=root)
    try:
        check(head.stdout if head.returncode == 0 else None, staged.stdout, path, root)
    except ValueError as error:
        return 1, f'{relative}: {error}'
    return 0, None


def main(argv):
    if len(argv) in (3, 5) and argv[1] == 'check' and (len(argv) == 3 or argv[3] == '--base'):
        status, error = staged_check(argv[2], argv[4] if len(argv) == 5 else 'HEAD')
        if error:
            print(error, file=sys.stderr)
        return status
    if len(argv) == 3 and argv[1] == 'append':
        path = Path(argv[2])
        body, count = append_new(path.read_text())
        path.write_text(body)
        print(f'Appended {count} items; ' + head_lines(body, 0)[0])
        return 0
    if len(argv) == 3 and argv[1] == 'triage':
        path = Path(argv[2])
        body, count = settle_triage(path.read_text())
        path.write_text(body)
        print(f'Settled {count} items; ' + '\n'.join(head_lines(body, 1)))
        return 0
    if len(argv) == 4 and argv[1] == 'done':
        path = Path(argv[2])
        path.write_text(done(path.read_text(), argv[3]))
        print('\n'.join(head_lines(path.read_text(), 1)))
        return 0
    options = dict(zip(argv[3::2], argv[4::2]))
    allowed = {'--counted': 'data-counted', '--backpressure': 'data-backpressure', '--kind-modules': 'data-kind-modules'}
    if (len(argv) < 3 or argv[1] not in ('init', 'head') or len(argv) % 2 == 0 or not set(options) <= set(allowed)
            or (argv[1] == 'head' and options) or options.get('--backpressure', 'off') != 'off'):
        print(__doc__, file=sys.stderr)
        return 2
    path = Path(argv[2])
    body = path.read_text()
    if argv[1] == 'head':
        print('\n'.join(head_lines(body)))
        return 0
    if parse(body) is not None:
        print('The notebook already has a lead and bridge queue', file=sys.stderr)
        return 1
    attrs = ''.join(f' {allowed[k]}="{html.escape(v, quote=True)}"' for k, v in options.items())
    configure(attrs)
    nodes = open_tree(body)
    record = body.find('<section id="research-record">')
    if record < 0:
        print('The notebook has no Research record', file=sys.stderr)
        return 1
    path.write_text(body[:record] + render(body, nodes, draining_after(False, nodes), attrs) + body[record:])
    print(f'Added the queue with {len(nodes)} items and {len(every_item(nodes)) - len(nodes)} sub-ideas under them')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
