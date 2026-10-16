#!/usr/bin/env python3
"""The lead and bridge queue (user, 3 October 2026: "I don't want promising leads/bridges to be dropped").

Every Outside lead and Absurd bridge that passed its cheap test in a route review waits in one FIFO queue,
the living section <section id="lead-queue">, the last section before the Research record.  It has no word
budget (notebook_context.py skips it) and restoration reads only its head (resume.py).  Rules, checked by
finish-turn.py against HEAD:

- The queue holds passed review items once each.  A review appends its newly passed items at the end; a review
  outside draining marks picks (<li data-pick>: its three most promising passed leads and two bridges,
  or all passed items when fewer pass; user, 5 October 2026) and appends only those.
- A research entry develops at most one item, by default the head, or any other queued item with a
  <strong>Chosen.</strong> paragraph, also while the queue drains (user, 9 and 11 October 2026; AGENTS.md),
  tagged data-lead or data-bridge="ANCHOR:N",
  and states <strong>Follow-up.</strong> Closed (a reason the attempt found), Developed (no remaining
  application to an open statement) or Continuing (it still bears on one; user, 3 October 2026: squeeze
  items, do not close them at their first usable result).  Closed and Developed remove the item; a
  Continuing item keeps the head for SPELL entries by default. At a boundary, data-spell-extend="2" on the
  article earns two more cycles when <p class="spell-extension" data-statement="NAME"> states
  <strong>Progress.</strong> (a registered proof, reduction or refutation from this spell/extension period,
  and how it materially advances that open statement) and <strong>Next.</strong> (the concrete next necessary
  implication using the same mechanism). Reassess every two extra cycles, with no lifetime cap; finite checks,
  promise alone or reused old progress do not qualify. Without fresh qualifying progress, rotate.
  A developed sub-idea counts for its continuing parent. A quoted user audit restoring a head can extend at
  its boundary with the same evidence, naming data-spell-item="lead:ID" or "bridge:ID".
  A quoted user override may set data-spell-limit="none" and data-spell-item="KIND:ID"
  on its article. It disables rotation only for that top-level item; close it with
  a recorded reason when further useful development is exhausted.
- Queue triage batches are retired (user, 9 October 2026: "Revert it back to the state where each item was done
  one at a time"): items are developed one at a time, each item's work finished before the next one's starts
  (AGENTS.md), and every item is recorded in its own entry.  Sub-ideas of the one item an entry
  develops may be batched in that entry (user, 9 October 2026: "An entry may develop at most one top level item.
  Sub ideas attached to a single parent can be batched."): each in a follow-up list item
  <li data-check="ID"> or <li data-build="ID"> ending <strong>Follow-up.</strong> Developed (with the evidence
  its kind asks for), Closed (with a reason) or Continuing.  Older entries' <h4>Queue triage</h4> lists are still
  read as history; a new entry with one is refused.  Older research entries' own Outside leads and Absurd bridges
  joined the tail like a review's; new research entries carry none (user, 9 October 2026).
- A queue audit (data-kind="audit") lists, under the same two headings, ideas that earlier reviews named outside
  the standard sections, each <li data-source="REVIEW-ANCHOR">; all its items are queued, at their source's
  place in record order when the queue is created.
- Sub-ideas sit under the item they belong to (user, 3 October 2026: "I want it to look like a nested list of
  entries"), one level deep: a sub-idea listed by an entry developing X joins X (or X's parent), one naming
  data-parent="KIND:ID" joins that item, others go to the tail.  The head or its first sub-idea may be developed;
  developing a sub-idea counts toward its parent's spell, and the parent moves to the tail with its sub-ideas.  A
  parent is not Developed while it has sub-ideas; a Closed parent closes them, except those the entry's follow-up
  list would keep Continuing: sub-ideas belong to their item, so a parent with a sub-idea it does not close is
  not Closed either, it is Continuing (user, 10 October 2026).  Backpressure counts top-level items.
- Sub-ideas (user, 3 October 2026): any Research-record entry may list, under <h4>Sub-ideas</h4>, questions to
  research and checks to run (<li data-sub="check">) and things to build (<li data-sub="build">) that it names and
  leaves undone; they join the tail with no test, as ANCHOR:sN, N counted over the whole list.  A check is Developed
  when the developing entry answers it citing evidence that resolves (a registered claim ID, an anchor, a repository
  file); a build when its task opens (a link to it) or the thing exists and its path is linked.
  Every relative link of an entry developing either must resolve.
- `add` (user, 7 October 2026: "You should be able to queue items by just running the tool") appends a check, a
  build or an idea at the tail, <li data-KIND="ID" data-source="WHERE">TEXT</li>, a top-level item of its own, from
  wherever it came up (an entry, a conversation, a task file); a commit that adds no entry may change the queue only
  by such appends.  A check or build added so is Developed as a listed one is; an idea (user, 7 October 2026: "in
  the future I might ask to queue actual ideas") as a check is, with the evidence that settles it.  A build whose
  text claims a cost or a saving (slow, saves, took 27 s) says in the text whether that is measured: "measured"
  with what was, or "not measured"; `add` and `edit` refuse one that does not (build_evidence).  A notebook's
  kind module may define its own idea kind.
- An entry reopens an item closed too early with a follow-up list item <li data-lead="ANCHOR:N"> ending
  <strong>Follow-up.</strong> Reopened: <reason>; `append` puts it at the tail.
- Backpressure: at CAP items the section carries data-draining="true"; then every research entry develops
  the head until the queue is down to FLOOR items, when the flag is removed.
- Per notebook, the section's attributes say which entry kinds count (data-counted, default research: they
  develop items, count toward spells and are held to the head while draining), whether backpressure applies
  (data-backpressure="off" turns it off) and which modules beside this file add kinds (data-kind-modules, each
  with a kinds(lead_queue) function).  A notebook without route items is checked once it has a queue section.
- The agent selects the order (user, 9 October 2026: "You can select the order. Make this a general framework
  rule."): an entry may develop any queued item instead of the head when its text has a paragraph
  <strong>Chosen.</strong> saying which open statement the item bears on and why it comes before the head.
  Nothing is skipped: every top-level item is still developed in its own entry, the head remains the default, and a
  chosen item's spell runs as for a head; at its boundary it waits until another item has had an entry.
- The user may pick any item out of order (user, 3 October 2026): the developing entry's tag carries
  data-picked="user" and its text a paragraph <strong>Picked.</strong> with the user's words in quotation marks.
  A picked entry satisfies draining and neither counts toward nor ends any spell.
- The user may also reorder the queue (user, 3 October 2026): an entry tagged data-picked="user", quoting them in
  its Picked. paragraph, lists under <h4>Queue order</h4> one <ol> of <li data-KIND="ID"></li>, every top-level
  item it leaves once, in the new order; sub-ideas stay under their parent.  It develops no item and settles no
  triage batch, and while the queue drains it is an uncounted kind (an audit).  `append` applies the order after
  the entry's other changes. An <ol data-move="head"> naming one parent promotes just it, preserving all others.
- An item that waits on the user's answer stays queued, marked data-waits: a follow-up list item for it ending
  <strong>Follow-up.</strong> Waiting: <the request> sets the mark, one ending Unblocked: <the answer> removes it.
  The head is the first item not waiting, and its first sub-idea not waiting; draining asks nothing when every
  item waits.

Usage: lead_queue.py init NOTEBOOK.html  (adds the section, oldest items first, if it is absent)
       lead_queue.py head NOTEBOOK.html  (the first HEAD_READ items, as restoration prints them)
       lead_queue.py history NOTEBOOK.html ID [--status]  (group history; --status gives the latest
                                            development and computed current spell before planning; ID is
                                            KIND:ID, as lead:REVIEW:1, where two kinds share an identifier)
       lead_queue.py done NOTEBOOK.html Closed|Developed|Continuing  (after appending the entry developing an
                                            item, and before append)
       lead_queue.py add NOTEBOOK.html --check|--build|--idea ID SOURCE TEXT  (appends the item at the tail;
                                            SOURCE says where it came up)
       lead_queue.py edit NOTEBOOK.html ID TEXT  (replaces the text of an item add wrote; its source stays)
       lead_queue.py close-built NOTEBOOK.html ID --record REVIEW.txt --path PATH [--path PATH] --note TEXT
                                            (removes a built top-level build without an entry and records it in
                                            research/queue-closures.jsonl; a commit without an entry may carry it)
       lead_queue.py append NOTEBOOK.html  (after the last entry, and done: items its follow-up list closes leave,
                                            its newly listed items join the queue, the items it reopens go to
                                            the tail, its Waiting and Unblocked marks apply)
       lead_queue.py init NOTEBOOK.html [--counted KINDS] [--backpressure off] [--kind-modules MODULES]
       lead_queue.py check NOTEBOOK.html [--base REV]  (the staged notebook against REV's, default HEAD;
                                            exit 0 when it passes, 1 when refused, 3 when it cannot run)"""
import functools
import html
import importlib
import importlib.util
import json
import os
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import branch_extension
from notebook_math import strip_tags, strip_tags_tight

ROOT = Path(__file__).resolve().parents[1]

CAP, FLOOR, HEAD_READ = 30, 10, 5     # user, 9 October 2026: earlier draining leaves fewer stale items
SPELL = 4   # default spell; evidence-backed extensions add two (user, 5 October 2026)
SPELL_EXTENSION = 2
DRAINING_REVIEW_RULE = ('While the queue is draining, reviews produce no Outside leads or Absurd bridges; '
                       'omit both sections and assess the existing work.')
# Queue triage batches (3 October 2026) are retired (user, 9 October 2026): batched items were closed by record
# matches without the attempt a single-item entry makes.  TRIAGE_RE still reads the batches of older entries.
TRIAGE_RETIRED = ('Queue triage batches are retired (user, 9 October 2026: "Revert it back to the state where each '
                  'item was done one at a time"): develop the head in its own entry (data-lead or data-bridge)')
TRIAGE_RE = re.compile(r'<h4>Queue triage</h4>\s*<ul>(.*?)</ul>', re.S)
CLAIM_RE = re.compile(r'\b(?:lem|thm|prop|cor|conj|check|ex|def|obs|local):[A-Za-z0-9.-]+')
EVIDENCE_RE = re.compile(CLAIM_RE.pattern + r'|href="(?!https?:|mailto:)[^"]+"')
HREF_RE = re.compile(r'href="([^"]+)"')
# A file URL of this repository (build_pages.SOURCE_URL), the form notebooks link files in: its repository path.
REPO_FILE_RE = re.compile(r'https://github\.com/kbr-/math-research/(?:blob|tree)/[^/]+/([^#?]+)')
SECTION_RE = re.compile(r'<section id="lead-queue"([^>]*)>(.*?)</section>', re.S)
def section_list(heading):
    # Keep the list body in group 1 for existing callers; either presentation is valid.
    return re.compile(r'<h4>' + re.escape(heading) + r'</h4>\s*<(?:ul|ol)>(.*?)</(?:ul|ol)>', re.S)


LEADS_RE = section_list('Outside leads')
BRIDGES_RE = section_list('Absurd bridges')
SUBIDEAS_RE = section_list('Sub-ideas')
ORDER_RE = re.compile(r'<h4>Queue order</h4>\s*<ol(?: data-move="head")?>(.*?)</ol>', re.S)
TEST_PASSED = re.compile(r'<strong>Test\.</strong>\s*Passed\b')
OUTCOME_RE = re.compile(r'<strong>Follow-up\.</strong>\s*(Developed|Continuing|Closed|Reopened|Promoted|Waiting|Unblocked)\b')
PICKED_RE = re.compile(r'<strong>Picked\.</strong>[^<]*?["\u201c][^"\u201d<]{3,}["\u201d]')
CHOSEN_RE = re.compile(r'<strong>Chosen\.</strong>\s*[^<\s][^<]{39,}')


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
        self._claim_records = None

    def anchors(self):
        return set(re.findall(r'\bid="([^"]+)"', self.body))

    def claim_records(self):
        if self._claim_records is None:
            registry = self.root / 'research/claims/index.json'
            self._claim_records = ({c['id']: c for c in json.loads(registry.read_text())['claims']}
                                   if registry.exists() else {})
        return self._claim_records

    def claims(self):
        if self._claims is None:
            self._claims = set(self.claim_records())
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
    """A build is Developed when its task opens (a link to it) or the thing exists and its path is linked."""
    unresolved, paths, anchors, claims = references(tag, text, where)
    problems = [f'links that do not resolve: {", ".join(unresolved)}'] if unresolved else []
    if not paths:
        problems.append('link the opened task or the built thing\'s path in the repository')
    return problems


ADDED_ID = re.compile(r'[a-z0-9]+(?:-[a-z0-9]+)*$')


def added_admit(body, head_body, item):
    """The problems with the queue line of an item `add` wrote: a lower-case hyphenated ID, where it came up and a
    line of text."""
    kind, ident = item
    line = re.search(r'<li data-' + kind + '="' + re.escape(ident) + r'"([^>]*)>(.*?)</li>', body, re.S)
    source = re.search(r'\bdata-source="([^"]*)"', line.group(1)) if line else None
    problems = [] if ADDED_ID.match(ident) else [f'{kind} ID {ident!r}: lower-case words joined by hyphens']
    if not source or not source.group(1).strip() or not strip_tags_tight(line.group(2)).strip():
        problems.append(f'an added {kind} is <li data-{kind}="ID" data-source="WHERE">TEXT</li>, with where it came '
                        'up and a line of text (lead_queue.py add writes it)')
    return problems


def admitter(node):
    """The rule admitting a node no entry lists: its kind's own, or for a check or build `add` wrote, which carries
    data-source as no listed sub-idea does, added_admit; None for a node only an entry may bring."""
    kind = KINDS[node.kind]
    if kind.admit is not None:
        return kind.admit
    return added_admit if kind.sub and 'data-source="' in node.attrs else None


KINDS = {'lead': Kind('lead', LEADS_RE), 'bridge': Kind('bridge', BRIDGES_RE),
         'idea': Kind('idea', rules={'Developed': check_developed}, admit=added_admit),
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
    window = re.search(r'\bdata-spell-window="(\d+)"', attrs)
    SETTINGS['spell_window'] = int(window.group(1)) if window else None     # off unless the section sets it
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
    the section counts, and no kind module calls it uncounted (a notebook whose reviews are entries of its own kind)."""
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


def named(item, ident):
    """Whether the (kind, identifier) item is what `ident` names: its identifier, or KIND:IDENTIFIER, the form
    for an identifier that two kinds share (a lead and a bridge of one review are both REVIEW:1)."""
    kind, _, rest = ident.partition(':')
    return item[1] == ident or (kind in KINDS and item == (kind, rest))


def qualified(node):
    """KIND:IDENTIFIER of a queued node, the form no two queued items share."""
    return f'{node.kind}:{node.ident}'


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



def is_draining(body, attrs=None):
    """The active backpressure state, including the threshold before its flag is written."""
    found = parse_tree(body, attrs) if body else None
    return bool(found and SETTINGS['backpressure'] and (found[0] or len(found[1]) >= CAP))


def validate_review_generation(tag, text, draining):
    """Reject new review lead/bridge sections during backpressure; historical entries stay readable."""
    if not draining or not re.search(r'\bdata-kind="review"', tag):
        return
    headings = re.findall(r'<h[1-6]\b[^>]*>(.*?)</h[1-6]>', text, re.S | re.I)
    names = {strip_tags_tight(heading).strip().casefold() for heading in headings}
    if names & {'outside leads', 'absurd bridges'}:
        raise ValueError(DRAINING_REVIEW_RULE)


def wait_changes(text):
    """{item: reference or None} of an entry's Waiting (set the mark) and Unblocked (remove it) follow-ups."""
    out = {}
    for kind, item_id, item in FOLLOWUP_ITEM.findall(text):
        outcome = OUTCOME_RE.search(item)
        if outcome and outcome.group(1) == 'Waiting':
            rest = item[outcome.end():]
            # A branch's own module may read the reference its own way (a link to a record of requests).
            reference = branch_extension.ask('wait_reference')
            given = reference(rest) if reference else None
            plain = re.sub(r'\s+', ' ', strip_tags(rest)).strip(' :.')
            out[(kind, item_id)] = plain[:80] if given is None else given
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
    """Problems with an entry's Waiting follow-ups: each names its request, and passes what the branch's own
    module asks of the reference, where it asks anything."""
    problems = []
    for item, ref in wait_changes(text).items():
        if ref is None:
            continue
        if not ref:
            problems.append(f'{item[1]}: a Waiting follow-up names the request it waits on')
            continue
        further = branch_extension.ask('wait_problems')
        problems += [f'{item[1]}: {problem}' for problem in (further(ref, where.base or where.root) if further else ())]
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


LINK_EARLIER_FROM = '2026-10-11'   # entries dated from here on; older records are not retrofitted


def unlinked_earlier_entry(body, nodes, articles, item):
    """The anchor of the most recent earlier entry that developed `item` itself, or else the one that developed
    the top-level item of its group, when the last entry does not link it; None otherwise.  Entries on sibling
    sub-ideas are not required.  An entry of 11 October 2026 re-derived a lemma and a failed attempt recorded
    the day before under the same item's parent, found by no registry search."""
    tag, text = articles[-1]
    dated = re.search(r'\bid="entry-(\d{4}-\d{2}-\d{2})-', tag)
    if dated is None or dated.group(1) < LINK_EARLIER_FROM:
        return None
    last = len(articles) - 1
    for target in dict.fromkeys((item, group_of(body, nodes, item, last))):
        for position in range(last - 1, -1, -1):
            old_tag, old_text = articles[position]
            work = developed_by(old_tag, old_text)
            if work and work[0] == target:
                anchor = re.search(r'\bid="([^"]+)"', old_tag)
                if anchor is not None and f'href="#{anchor.group(1)}"' not in text:
                    return anchor.group(1)
                break
    return None


READ_ALL_LIMIT = 6      # an item with more earlier entries than this is held to its latest only, as before
READ_ALL_FROM = '2026-10-12'    # entries dated from here on; earlier ones could not have known the rule
QUOTED_WORDS = 8
UNREAD_RE = re.compile(r'<strong>Unread\.</strong>((?:(?!</p>).)*)', re.S)


def descendant_entries(articles, anchors, end=None):
    """Anchors, in record order, of the entries before position `end` that developed a sub-idea listed by one of
    the entries `anchors` (an item ANCHOR:sN), and are not among them; one generation.  On 10 October 2026 an
    audit answering part of a queued check was filed under a sub-idea of an entry on that check, and appeared in
    no list for the check; an entry of 12 October on it was drafted without it."""
    wanted = set(anchors)
    found = []
    for tag, text in articles[:end]:
        work = developed_or_none(tag, text)
        anchor = re.search(r'\bid="([^"]+)"', tag)
        if (work and anchor and anchor.group(1) not in wanted and ':s' in work[0][1]
                and work[0][1].rsplit(':s', 1)[0] in wanted):
            found.append(anchor.group(1))
    return found


def item_entries(articles, item, end=None):
    """(own, below): anchors of the entries before position `end` that developed `item` itself, and of those that
    developed a sub-idea listed by one of them."""
    own = []
    for tag, text in articles[:end]:
        work = developed_or_none(tag, text)
        anchor = re.search(r'\bid="([^"]+)"', tag)
        if work and work[0] == item and anchor:
            own.append(anchor.group(1))
    return own, descendant_entries(articles, own, end)


def developed_or_none(tag, text):
    """developed_by, with None for an older entry whose tag names two items: the largest notebook's record has
    one, of September 2026, and a check on a new entry is not the place to refuse it."""
    try:
        return developed_by(tag, text)
    except ValueError:
        return None


def _words(text):
    plain = html.unescape(strip_tags(text))
    return [w for w in (re.sub(r'^\W+|\W+$', '', token).lower() for token in plain.split()) if w]


def quotable(text):
    """The words of an entry that a later entry on its item quotes: those of its own Follow-up paragraph, where
    it says what it left; of its title when the Follow-up has fewer than QUOTED_WORDS words; and none when the
    title is as short, in which case a link is all that can be asked."""
    follow = re.findall(r'<strong>Follow-up\.</strong>((?:(?!</p>).)*)', FOLLOWUP_ITEM.sub('', text), re.S)
    title = re.search(r'<h3>(.*?)</h3>', text, re.S)
    for part in (follow[-1] if follow else '', title.group(1) if title else ''):
        if len(_words(part)) >= QUOTED_WORDS:
            return _words(part)
    return []


def unread_item_entries(articles, item, limit=READ_ALL_LIMIT):
    """[(anchor, what is missing), ...] for the earlier entries that developed `item` itself, or a sub-idea listed
    by one of those, when there are at most `limit` of them: 'link' where the last entry does not link the entry,
    'quotation' where it links it without QUOTED_WORDS consecutive words of what `quotable` gives for it.  An
    entry named in the last entry's <strong>Unread.</strong> paragraph, by its anchor, is waived: the paragraph
    says which were not read and why.  On 12 October 2026 an entry on an item with two earlier entries, and two
    more on sub-ideas they listed, repeated a statement that one of the four had withdrawn; it linked one of them
    without having read it, which is why a link alone is not accepted.  A quotation shows that a sentence was
    seen, not that an entry was read."""
    tag, text = articles[-1]
    dated = re.search(r'\bid="entry-(\d{4}-\d{2}-\d{2})-', tag)
    if dated is None or dated.group(1) < READ_ALL_FROM:
        return []
    own, below = item_entries(articles, item, len(articles) - 1)
    wanted = own + below
    if not wanted or len(wanted) > limit:
        return []
    said = UNREAD_RE.search(text)
    waived = said.group(1) if said else ''
    have = _words(text)
    runs = {tuple(have[i:i + QUOTED_WORDS]) for i in range(len(have) - QUOTED_WORDS + 1)}
    by_anchor = {(re.search(r'\bid="([^"]+)"', old_tag) or [None, ''])[1]: old_text
                 for old_tag, old_text in articles[:-1]}
    missing = []
    for anchor in wanted:
        if re.search(re.escape(anchor) + r'(?![\w-])', waived):      # the whole anchor: anchors share prefixes
            continue
        if f'href="#{anchor}"' not in text:
            missing.append((anchor, 'link'))
            continue
        given = quotable(by_anchor[anchor])
        if given and not any(tuple(given[i:i + QUOTED_WORDS]) in runs
                             for i in range(len(given) - QUOTED_WORDS + 1)):
            missing.append((anchor, 'quotation'))
    return missing


OWED_RE = re.compile(r'<strong>Owed attempt\.</strong>((?:(?!</p>)(?!</li>).)*)', re.S)


def unaccounted_attempt(articles, item):
    """The anchor of the latest earlier entry that developed `item` and whose Follow-up names a next attempt,
    when the last entry has no <strong>Owed attempt.</strong> paragraph of at least 40 characters; None otherwise.

    On 11 October 2026 a reading named as an item's next attempt was displaced by constructions in three
    entries on the item, each naming it again.  The finisher already holds a closure to the attempt named;
    this holds every entry on the item to saying what became of it: made, with its outcome, or not made and
    why another attempt came first."""
    tag, text = articles[-1]
    dated = re.search(r'\bid="entry-(\d{4}-\d{2}-\d{2})-', tag)
    if dated is None or dated.group(1) < LINK_EARLIER_FROM:
        return None
    for position in range(len(articles) - 2, -1, -1):
        old_tag, old_text = articles[position]
        work = developed_by(old_tag, old_text)
        if work and work[0] == item:
            follow = re.findall(r'<p><strong>Follow-up\.</strong>(.*?)</p>', old_text, re.S)
            if not follow or not re.search(r'\bnext attempt\b', follow[-1], re.I):
                return None
            said = OWED_RE.search(text)
            plain = html.unescape(strip_tags(said.group(1))).strip() if said else ''
            anchor = re.search(r'\bid="([^"]+)"', old_tag)
            return anchor.group(1) if len(plain) < 40 and anchor else None
    return None


LEFT_ITEMS_RE = re.compile(r'\bdata-left-items="([^"]*)"')
RETURNS_RE = re.compile(r'<strong>Returns\.</strong>((?:(?!</p>)(?!</li>).)*)', re.S)


def left_by_last_review(body, nodes, articles, item):
    """The anchor of the last review before the last entry, when that review's data-left-items names `item` or the
    top-level item of its group and the entry has no <strong>Returns.</strong> paragraph of at least 40
    characters saying why it returns; None otherwise.

    On 11 October 2026 two reviews in a row decided to leave an item, and the next block returned to it, once
    for eighteen entries in all; nothing compared an entry's item with the review's decision.  The review now
    declares the items it leaves, and an entry on one of them says why it returns.  The check reads the item,
    not the subject: the same question developed under another item is the reviewer's to catch."""
    tag, text = articles[-1]
    last = len(articles) - 1
    route = re.findall(r'\bdata-route="([^"]*)"', tag)
    for position in range(last - 1, -1, -1):
        old_tag = articles[position][0]
        if 'data-kind="review"' not in old_tag or re.findall(r'\bdata-route="([^"]*)"', old_tag) != route:
            continue                                  # a review of another route decides nothing for this one
        left = LEFT_ITEMS_RE.search(old_tag)
        names = set(left.group(1).split()) if left else set()
        if not names & {item[1], group_of(body, nodes, item, last)[1]}:
            return None
        said = RETURNS_RE.search(text)
        plain = html.unescape(strip_tags(said.group(1))).strip() if said else ''
        anchor = re.search(r'\bid="([^"]+)"', old_tag)
        return anchor.group(1) if len(plain) < 40 and anchor else None
    return None


def unknown_left_items(tag, nodes):
    """The identifiers a review's data-left-items names that are not queued: a mistyped one would leave nothing."""
    left = LEFT_ITEMS_RE.search(tag) if 'data-kind="review"' in tag else None
    queued = {item[1] for item in every_item(nodes)}
    return [name for name in left.group(1).split() if name not in queued] if left else []


QUEUE_ITEMS_RE = re.compile(r'\bdata-queue-items="(\d+)"')


def review_counts(body):
    """[(anchor, count)] for the reviews that declare the queue's top-level count, in record order."""
    out = []
    for tag, _ in record_articles(body):
        declared = QUEUE_ITEMS_RE.search(tag)
        anchor = re.search(r'\bid="([^"]+)"', tag)
        if declared and anchor and 'data-kind="review"' in tag:
            out.append((anchor.group(1), int(declared.group(1))))
    return out


def undeclared_review_count(tag, draining, nodes):
    """What a review of a draining queue must declare and does not: data-queue-items with the top-level count.

    A queue was called draining through a block of six entries that left its count where it was (52 and 52,
    11 October 2026).  A review of a draining queue therefore records the count, and the start guidance prints
    the last two recorded counts beside the present one."""
    dated = re.search(r'\bid="entry-(\d{4}-\d{2}-\d{2})-', tag)
    if not draining or 'data-kind="review"' not in tag or dated is None or dated.group(1) < LINK_EARLIER_FROM:
        return None
    declared = QUEUE_ITEMS_RE.search(tag)
    if declared is None or int(declared.group(1)) != len(nodes):
        return len(nodes)
    return None


def unstated_subideas(tag, text, item, before_nodes):
    """The open sub-ideas of the top-level item an entry develops for which the entry lists no outcome.

    `before_nodes` is the queue as it stood before the entry.  The entry developing a sub-idea states that one's
    outcome as its own follow-up; every other open sub-idea of the same parent needs a follow-up list item with
    Closed, Developed or Continuing.  On 11 October 2026 a sub-idea answered by the next entry on its item stayed
    queued for a day, because that entry spoke only of the sub-idea it had posed itself."""
    dated = re.search(r'\bid="entry-(\d{4}-\d{2}-\d{2})-', tag)
    if dated is None or dated.group(1) < LINK_EARLIER_FROM:
        return []
    parent, node = locate(before_nodes, item)
    top = parent if parent is not None else node
    if top is None:
        return []
    stated = {listed for listed, outcome, _ in listed_outcomes(text) if outcome in ('Closed', 'Developed', 'Continuing')}
    return [child.ident for child in top.children if child.item != item and child.item not in stated]


def history(body, ident):
    """(anchor, item id, outcome) of every entry that developed the item `ident`, the top-level item of its
    group, or another member of that group, oldest first: what to read before an entry on the item is begun
    (the link check above asks for the latest only)."""
    found = parse_tree(body)
    nodes = found[1] if found else []
    articles = record_articles(body)
    shared = [i for i in every_item(nodes) if named(i, ident)]
    if len(shared) > 1:     # never the first match unsaid: a caller that looks up bare fails here, not quietly
        raise ValueError(f'{len(shared)} queued items share the identifier {ident}; name one by its kind: '
                         + ', '.join(f'{kind}:{name}' for kind, name in shared))
    item = shared[0] if shared else None
    if item is None:
        item = next((w[0] for w in (developed_by(t, x) for t, x in articles) if w and named(w[0], ident)), None)
    if item is None:
        return []
    group = group_of(body, nodes, item, len(articles))
    rows = []
    for position, (tag, text) in enumerate(articles):
        work = developed_by(tag, text)
        if work and group_of(body, nodes, work[0], position) == group:
            anchor = re.search(r'\bid="([^"]+)"', tag)
            rows.append((anchor.group(1) if anchor else '?', work[0][1], work[1] or ''))
    return rows


def spell_entries(body, item, nodes=None, end=None):
    """Positions in the current spell, oldest first; reviews and user picks do not count."""
    if nodes is None:
        found = parse_tree(body)
        nodes = found[1] if found else []
    positions = []
    articles = record_articles(body)[:end]
    for position in range(len(articles) - 1, -1, -1):
        tag, text = articles[position]
        if not counted(tag, text) or 'data-picked="user"' in tag:
            continue
        work = developed_by(tag, text)
        if triaged(tag, text) or (work and group_of(body, nodes, work[0], position) != item):
            break
        if work:
            positions.append(position)
    return positions[::-1]


def spell(body, item, nodes=None, end=None):
    """Number of consecutive developments of a parent or its children (reviews do not reset it)."""
    return len(spell_entries(body, item, nodes, end))


SPELL_WINDOW = 8    # the window the status of an item reports; a refusal needs data-spell-window on the section


def window_count(body, item, nodes=None, window=SPELL_WINDOW, end=None):
    """Number of entries developing `item` or its sub-ideas among the last `window` counted entries that develop
    an item (reviews and user picks do not count).  A spell counts entries in a row, so one entry on another
    item restarts it: on 12 October 2026 an item with 23 entries had never had more than two in a row."""
    if nodes is None:
        found = parse_tree(body)
        nodes = found[1] if found else []
    articles = record_articles(body)[:end]
    count = seen = 0
    for position in range(len(articles) - 1, -1, -1):
        if seen == window:
            break
        tag, text = articles[position]
        if not counted(tag, text) or 'data-picked="user"' in tag:
            continue
        work = developed_by(tag, text)
        if not work:
            continue
        seen += 1
        count += group_of(body, nodes, work[0], position) == item
    return count


ATTEMPT_SENTENCE_RE = re.compile(r'\b(?:next attempt|still owed|owed (?:from|since)|stays? owed)\b', re.I)


def named_attempts(body, ident):
    """(anchor, sentences of its Follow-up that name an attempt, whether a later entry of the group has an
    Owed attempt paragraph) for every entry of the item's group whose Follow-up names one, oldest first.

    On 11 October 2026 an attempt named on 9 October was deferred in two entries of its item, each of whose
    Owed attempt paragraphs answered only the latest follow-up; a review found that the statement to be read
    had been on record for a day.  The paragraph is written against this list, not against the last entry."""
    articles = dict()
    for tag, text in record_articles(body):
        anchor = re.search(r'\bid="([^"]+)"', tag)
        if anchor:
            articles[anchor.group(1)] = text
    rows = []
    anchors = [anchor for anchor, _item, _outcome in history(body, ident)]
    for position, anchor in enumerate(anchors):
        text = articles.get(anchor, '')
        follow = re.findall(r'<p><strong>Follow-up\.</strong>(.*?)</p>', text, re.S)
        if not follow:
            continue
        plain = ' '.join(html.unescape(strip_tags(follow[-1])).split())
        said = [s for s in re.split(r'(?<=[.;:])\s+(?=[A-Z])', plain) if ATTEMPT_SENTENCE_RE.search(s)]
        if said:       # answered, as far as a pattern can tell: some later entry of the group has the paragraph
            later = any(OWED_RE.search(articles.get(a, '')) for a in anchors[position + 1:])
            rows.append((anchor, said, later))
    return rows


def survey(body):
    """One row for each top-level queued item: (kind, identifier, entries of its group, open sub-ideas, outcome
    of its latest entry, whether that entry's Follow-up names an attempt, entries naming an attempt that no
    later entry of the group reports).  For judging whether a queue can drain by closures: an item with no
    entry, no sub-idea and no attempt named is untouched, not dead."""
    found = parse_tree(body)
    rows = []
    for node in (found[1] if found else []):
        entries = history(body, qualified(node))
        attempts = named_attempts(body, qualified(node))
        latest_names = bool(entries) and bool(attempts) and attempts[-1][0] == entries[-1][0]
        rows.append((node.kind, node.ident, len(entries), len(node.children),
                     entries[-1][2] if entries else 'none', latest_names,
                     sum(1 for _anchor, _said, later in attempts if not later)))
    return rows


ELSEWHERE = 6       # measured 11 October 2026 on four items known to be answered in part under another item, each
                    # on the notebook as it stood before the item's first entry: the answering claim stood
                    # second, third and second for three and was not among the six for the fourth.  The limit
                    # was chosen on these same cases.  A share of the item's words in the claim's summary found
                    # none of the four at 0.4 and one at 0.3


def registered_claims(path=None):
    """The claims of the registry, or [] where there is none."""
    try:
        return json.loads((path or ROOT / 'research' / 'claims' / 'index.json').read_text())['claims']
    except (OSError, ValueError, KeyError):
        return []


def claims_elsewhere(body, claims, ident, limit=ELSEWHERE, earlier=False):
    """[(score, claim id, entry anchor), ...], best first: the claims nearest to the queued item's text, by the
    registry search's ranking and with its score, among those declared by entries that did not develop the item
    `ident` or its group and came after the entry that queued it (for an item added by the tool, after the
    record's last entry at that time) and after the group's last entry.  In one block of 11 October 2026 four
    items taken as never developed had each been partly answered by an entry filed under another item, and
    nothing showed it before the cycle was spent.  A hint to read the entry, not a verdict.

    With `earlier` true, the claims of the other entries up to the entry that queued the item instead, and none
    where that entry is not in the record; with None, both sides in one ranking, the search's scores depending
    on the set ranked.  On 12 October 2026 a queued check was taken and a cycle spent before two registered
    statements that bore on it, both older than the item, were read."""
    found = parse_tree(body)
    node = next((n for top in (found[1] if found else []) for n in [top] + top.children if named(n.item, ident)), None)
    if node is None:
        return []
    articles = record_articles(body)
    anchors = [(re.search(r'\bid="([^"]+)"', tag) or [None, ''])[1] for tag, _ in articles]
    own = {anchor for anchor, _, _ in history(body, ident)}
    added = re.search(r'\bdata-after="([^"]+)"', node.attrs)    # an item added by the tool: the record's last entry then
    source = added.group(1) if added else node.ident.rsplit(':', 1)[0]
    after = max([position for position, anchor in enumerate(anchors) if anchor == source or anchor in own] or [-1])
    queued = max([position for position, anchor in enumerate(anchors) if anchor == source] or [-1])
    where = {}                # earlier: up to the queuing entry, none where it is unknown; None: of either side
    for position, (tag, _) in enumerate(articles):
        declared = re.search(r'\bdata-claims="([^"]*)"', tag)
        wanted = (position > after or position <= queued) if earlier is None else (
            position <= queued if earlier else position > after)
        if wanted and declared and anchors[position] not in own:
            where.update({claim: anchors[position] for claim in declared.group(1).split()})
    later = [claim for claim in claims if claim['id'] in where]
    if not later:
        return []
    spec = importlib.util.spec_from_file_location('search_claims', Path(__file__).parent / 'search-claims.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    text = html.unescape(re.sub(r'\\\(.*?\\\)', ' ', strip_tags(node.text.split('):', 1)[-1])))
    if not module.stems(text):                  # nothing to rank by: the search would return every claim at zero
        return []
    return [(round(score, 1), claim['id'], where[claim['id']])
            for score, claim in module.search({'claims': later}, [text])[:limit] if score > 0]


def registered(path=None):
    """(claims, typed edges) of the registry from one reading of it, or ([], []) where there is none."""
    try:
        registry = json.loads((path or ROOT / 'research' / 'claims' / 'index.json').read_text())
        return registry['claims'], registry.get('relationships', [])
    except (OSError, ValueError, KeyError):
        return [], []


def citing_entries(body, relationships, ident):
    """[(entry anchor, its claim, edge type, cited claim, of the queuing entry, after the latest development), ...]
    in record order: the articles of any kind that did not develop the item `ident` or its group, and are not
    the entry that queued it, one of whose declared claims has a registry edge of any type to a claim declared
    by the queuing entry (fifth field true) or by an entry that developed the item or its group.
    On 12 October 2026 a queued check was developed in five entries while an entry on another item, two after the
    one that queued it, had tested its general claim and cited its proposition: the ranking by nearness of text
    printed none, and the citation was in the registry.  An item added by the tool names no queuing entry, and
    only the claims of its own entries are looked for.  A reading list, not a verdict."""
    found = parse_tree(body)
    node = next((n for top in (found[1] if found else []) for n in [top] + top.children if named(n.item, ident)), None)
    if node is None:
        return []
    own = {anchor for anchor, _, _ in history(body, ident)}
    source = None if re.search(r'\bdata-after="', node.attrs) else node.ident.rsplit(':', 1)[0]
    declared = []
    for tag, _ in record_articles(body):
        anchor = (re.search(r'\bid="([^"]+)"', tag) or [None, ''])[1]
        claims = re.search(r'\bdata-claims="([^"]*)"', tag)
        declared.append((anchor, set(claims.group(1).split()) - {'none'} if claims else set()))
    queuing = set().union(*[claims for anchor, claims in declared if anchor == source] or [set()])
    cited = queuing.union(*[claims for anchor, claims in declared if anchor in own] or [set()])
    edges = {}
    for edge in relationships:           # edges between current claims only: a historical label may share an id
        ends = [edge.get(end, {}) for end in ('source', 'target')]
        if ends[1].get('id') in cited and all(end.get('namespace', 'current') == 'current' for end in ends):
            edges.setdefault(ends[0].get('id'), []).append((edge.get('type'), ends[1].get('id')))
    latest = max([position for position, (anchor, _) in enumerate(declared) if anchor in own] or [-1])
    return [(anchor, claim, kind, target, target in queuing, position > latest)
            for position, (anchor, claims) in enumerate(declared) if anchor not in own and anchor != source
            for claim in sorted(claims) for kind, target in edges.get(claim, [])]


def linking_entries(body, ident):
    """Anchors of the later entries, of any kind, that did not develop the item `ident` and link the entry which
    queued it, in order; None for an item that is not queued or that no entry queued (one added by the tool).
    A signal for an item answered elsewhere that a queued build asked for.  Measured on 11 October 2026 on four
    items known to be answered in part under another item, it held the answering entry for none of them, so it
    is offered as a command and printed nowhere by default."""
    found = parse_tree(body)
    node = next((n for top in (found[1] if found else []) for n in [top] + top.children if named(n.item, ident)), None)
    articles = record_articles(body)
    anchors = [(re.search(r'\bid="([^"]+)"', tag) or [None, ''])[1] for tag, _ in articles]
    source = (node.ident if node else ident).rsplit(':', 1)[0]
    if node is None or source not in anchors:
        return None
    own = {anchor for anchor, _, _ in history(body, ident)}
    return [anchors[position] for position in range(anchors.index(source) + 1, len(articles))
            if anchors[position] not in own and f'href="#{source}"' in articles[position][1]]


EXTENSION_RE = re.compile(r'\bAdded\b')


def extended_again(head_body, body):
    """Identifiers of the queued build items whose text gained a dated addition ("Added ...") in `body` while
    HEAD's text of the same item already carried one.  In one review period of 12 October 2026 the text of one
    queued build was extended five times, each time as the prevention of a mistake, and nothing was built:
    a second extension is refused, and what is new is built or queued as an item of its own."""
    def builds(text):
        found = parse_tree(text) if text else None
        return {qualified(node): len(EXTENSION_RE.findall(node.text))
                for top in (found[1] if found else []) for node in [top] + top.children if node.kind == 'build'}
    before = builds(head_body)
    return sorted(ident for ident, count in builds(body).items()
                  if before.get(ident, 0) >= 1 and count > before[ident])


def answered_report(body, claims):
    """[(item id, [(score, claim, anchor), ...]), ...] for the top-level queued items no entry has developed that
    have such claims; build items are left out, a claim being no answer to a build."""
    found = parse_tree(body)
    rows = []
    for node in (found[1] if found else []):
        if node.kind != 'build' and not history(body, qualified(node)):
            matches = claims_elsewhere(body, claims, qualified(node))
            if matches:
                rows.append((node.ident, matches))
    return rows


def result_files(body, ident):
    """The result files (scripts, outputs, data) that the entries on the item's group link under research/results,
    in order, without timing tables and reviewers' records.  On 11 October 2026 an entry reported a numerical
    control of an identity that an earlier entry on the same item had already controlled, uncited: the status
    listed the earlier entries, by title, and not their computations."""
    anchors = {anchor for anchor, _, _ in history(body, ident)}
    out = []
    for tag, text in record_articles(body):
        found = re.search(r'\bid="([^"]+)"', tag)
        if found and found.group(1) in anchors:
            for path in re.findall(r'href="(research/results/[^"#]+)"', text):
                if not path.endswith(('timing.html', 'review.txt', 'stage1.txt')) and path not in out:
                    out.append(path)
    return out


def item_status(body, ident, claims=None, relationships=None):
    """Bounded orientation for a queued item, using the same grouping and spell rules as the gate."""
    found = parse_tree(body)
    nodes = found[1] if found else []
    matches = [item for item in every_item(nodes) if named(item, ident)]
    if len(matches) > 1:
        history(body, ident)        # raises, naming the forms to choose from
    if len(matches) != 1:
        raise ValueError(f'Expected one queued item {ident}; found {len(matches)}')
    ident = f'{matches[0][0]}:{matches[0][1]}'      # the unambiguous form, for the lookups below
    parent, node = locate(nodes, matches[0])
    top = parent or node
    rows = history(body, ident)
    count = spell(body, top.item, nodes)
    limit = spell_limit(body, top.item, nodes)
    boundary = 'unlimited' if limit == float('inf') else str(limit)
    lifetime = len(history(body, f'{top.kind}:{top.ident}'))
    # A spell counts consecutive entries, so entries on another item between restart it: on 11 October 2026 an
    # item with fifteen entries stood at "spell 0".  The lifetime count is printed so that this is seen.
    reset = (f' Entries on it in all: {lifetime}, more than a spell: the spell restarted after entries on other '
             'items, and the boundary has not limited the item.' if lifetime > count and lifetime >= 3
             else f' Entries on it in all: {lifetime}.')
    # The queued text holds what a merge carried over from another item, which no entry's follow-up names: on
    # 11 October 2026 two starting points of a merged check survived there alone and the status did not show them.
    queued = re.sub(r'\s+', ' ', html.unescape(strip_tags(node.text))).strip()
    return [f'Item: {node.kind}:{node.ident}; group: {top.kind}:{top.ident}',
            f'Queued text: {queued}',
            'Latest development: ' + (f'#{rows[-1][0]} ({rows[-1][2]})' if rows else 'none'),
            f'Current spell: {count}; boundary: {boundary}.' + reset,
            f'Entries on it among the last {SPELL_WINDOW} on queued items: '
            f'{window_count(body, top.item, nodes)}.',
            (f'Next development would be entry {count + 1}.' if count < limit else
             'Boundary reached: develop a different item first, unless an extension is earned.'),
            'Open sub-ideas: ' + (', '.join(c.ident for c in top.children) or 'none'),
            'Entries on the item itself, then on sub-ideas they listed (when at most '
            f'{READ_ALL_LIMIT} in all, a new entry links and quotes each): '
            + ' | '.join(', '.join('#' + anchor for anchor in part) or 'none'
                         for part in item_entries(record_articles(body), node.item)),
            'Result files its entries link (read what was computed before computing again): '
            + (', '.join(result_files(body, ident)) or 'none'),
            'Attempts named by the follow-ups of its entries (write the Owed attempt paragraph against all):'
            ] + ([f'  #{anchor}{"" if owed else " [no later entry has an Owed attempt paragraph]"}: '
                  + ' '.join(said)
                  for anchor, said, owed in named_attempts(body, ident)] or ['  none']) + (
            ['Claims of later entries on other items nearest to its text (read each entry before planning):']
            + ([f'  {score} {claim} in #{anchor}' for score, claim, anchor in claims_elsewhere(body, claims, ident)]
               or ['  none'])
            + ['Claims of entries up to the one that queued it, nearest to its text (read each statement too):']
            + ([f'  {score} {claim} in #{anchor} [earlier]'
                for score, claim, anchor in claims_elsewhere(body, claims, ident, earlier=True)] or ['  none'])
            if claims is not None else []) + (
            citing_status(citing_entries(body, relationships, ident)) if relationships is not None else [])


def citing_status(rows):
    """The status lines for citing_entries' rows: the queuing entry's list, then that of the item's own entries."""
    return (['Other entries whose claims cite, by a registry edge, a claim of the entry that queued it (read each '
             'before planning; [later]: after the item\'s latest development, or it has none):']
            + (citing_lines(rows, True) or ['  none'])
            + ['Other entries whose claims cite a claim of its own entries or its group\'s ([later]: after the '
               'latest development):']
            + (citing_lines(rows, False) or ['  none']))


def citing_lines(rows, queuing):
    """One line for each entry among citing_entries' rows that cite a claim of the queuing entry (`queuing` true)
    or of the item's own entries, in their order, with those edges; [later] marks an entry after the item's
    latest development."""
    by_entry = {}
    for anchor, claim, kind, target, of_queuing, later in rows:
        if of_queuing == queuing:
            by_entry.setdefault((anchor, later), []).append(f'{claim} {kind} {target}')
    return [f'  #{anchor}{" [later]" if later else ""}: ' + '; '.join(edges)
            for (anchor, later), edges in by_entry.items()]


def older_nearest(body, claims):
    """(older, some, unknown) over the top-level queued items, builds left out: items whose nearest claim, in one
    ranking of the claims of entries on other items from before the item's queuing and from after its last own
    entry, is of an entry before the queuing; items with any such claim and a known queuing entry; and items
    whose queuing entry is not in the record, which have no earlier side and are counted apart."""
    found = parse_tree(body)
    order = [(re.search(r'\bid="([^"]+)"', tag) or [None, ''])[1] for tag, _ in record_articles(body)]
    anchors = set(order)
    older = some = unknown = 0
    for node in (found[1] if found else []):
        if node.kind == 'build':
            continue
        added = re.search(r'\bdata-after="([^"]+)"', node.attrs)
        source = added.group(1) if added else node.ident.rsplit(':', 1)[0]
        if source not in anchors:
            unknown += 1
            continue
        both = claims_elsewhere(body, claims, qualified(node), 1, earlier=None)
        some += bool(both)               # the side is that of the entry the ranking names for the top claim
        older += bool(both and order.index(both[0][2]) <= max(i for i, a in enumerate(order) if a == source))
    return older, some, unknown


def claim_places(body, claims, ident, wanted):
    """['CLAIM: place N of M among the claims of earlier|later entries, score S' or 'CLAIM: not among them', ...]:
    where named claims stand in the two rankings for an item, to measure what a listing cut at ELSEWHERE shows."""
    lines = []
    for label, earlier in (('earlier', True), ('later', False)):
        ranked = claims_elsewhere(body, claims, ident, len(claims) or 1, earlier=earlier)
        places = {claim: (place, score) for place, (score, claim, _) in enumerate(ranked, 1)}
        lines += [f'{claim}: place {places[claim][0]} of {len(ranked)} among the claims of {label} entries, score '
                  f'{places[claim][1]}; the listing shows {ELSEWHERE}'
                  for claim in wanted if claim in places]
    return lines + [f'{claim}: not among them' for claim in wanted if not any(line.startswith(claim + ':')
                                                                              for line in lines)]


def extension_item(body, nodes, tag, text, position=None):
    """An extension belongs to a continuing lead/bridge, including one just promoted by the user."""
    if 'data-spell-extend=' not in tag:
        return None
    if 'data-spell-extend="2"' not in tag:
        raise ValueError('A spell extension adds exactly two cycles: data-spell-extend="2"')
    work = developed_by(tag, text)
    if work and 'data-picked="user"' not in tag:
        item = group_of(body, nodes, work[0], position)
        if item == work[0] and work[1] != 'Continuing':
            raise ValueError('A closed or developed parent cannot extend its spell')
    else:
        named = re.search(r'data-spell-item="(lead|bridge):([^"]+)"', tag)
        if not (named and 'data-kind="audit"' in tag and picked(tag, text) and ORDER_RE.search(text)):
            raise ValueError('An extension needs a development, or a quoted user audit restoring its head')
        item = named.groups()
    return item      # any item the agent develops may earn one (user, 10 October 2026)


def unlimited_item(tag, text):
    """An explicit, quoted user override, scoped to one queue item."""
    if 'data-spell-limit=' not in tag:
        return None
    named = re.search(r'data-spell-item="(' + NAMES + r'):([^\"]+)"', tag)
    if 'data-spell-limit="none"' not in tag or not named or not picked(tag, text):
        raise ValueError('An unlimited spell needs data-spell-limit="none", a named item, and a quoted user pick')
    return named.groups()


def spell_limit(body, item, nodes=None, end=None):
    """Four by default; each declaration at the current boundary adds two, without a lifetime cap."""
    if 'data-spell-limit=' in body:
        for tag, text in reversed(record_articles(body)[:end]):
            if unlimited_item(tag, text) == item:
                return float('inf')
    if 'data-spell-extend=' not in body:
        return SPELL
    if nodes is None:
        found = parse_tree(body)
        nodes = found[1] if found else []
    positions = spell_entries(body, item, nodes, end)
    if not positions:
        return SPELL
    articles = record_articles(body)[:end]
    count, limit = 0, SPELL
    positions = set(positions)
    for pos in range(min(positions), len(articles)):
        count += pos in positions
        tag, text = articles[pos]
        if extension_item(body, nodes, tag, text, pos) == item:
            if count != limit:
                raise ValueError(f'A spell extension is assessed at cycle {limit}, not cycle {count}')
            limit += SPELL_EXTENSION
    return limit


def validate_spell_extension(body, tag, text, nodes, where):
    """Require fresh proved/refuted progress and a named remaining implication, not a case list."""
    unlimited = unlimited_item(tag, text)
    if unlimited is not None:
        parent, node = locate(nodes, unlimited)
        if node is None or parent is not None:
            raise ValueError('An unlimited spell names one queued top-level item')
    item = extension_item(body, nodes, tag, text, len(record_articles(body)) - 1)
    paragraph = re.search(r'<p\b[^>]*class="spell-extension"[^>]*>(.*?)</p>', text, re.S)
    if item is None:
        if paragraph:
            raise ValueError('A spell-extension paragraph needs data-spell-extend="2" on its article')
        return
    if 'data-kind="audit"' in tag:
        head = head_of(ordered(tag, text, nodes))
        if head is None or head.item != item:
            raise ValueError('A restored spell extension must name the new nonwaiting head')
    spell_limit(body, item, nodes)  # Includes the current declaration; rejects early/duplicate extensions.
    if not paragraph or not re.search(r'data-statement="[^"\s][^"]*"', paragraph.group(0)):
        raise ValueError('A spell extension names its open statement in a spell-extension paragraph')
    progress = re.search(r'<strong>Progress\.</strong>(.*?)<strong>Next\.</strong>(.+)',
                         paragraph.group(1), re.S)
    if not progress or any(not strip_tags_tight(part).strip() for part in progress.groups()):
        raise ValueError('A spell extension states Progress and a concrete Next necessary implication')
    articles = record_articles(body)
    positions = spell_entries(body, item, nodes)
    if not positions:
        raise ValueError('A spell extension needs a completed default spell before it can extend')
    previous = max((p for p in range(positions[0], len(articles) - 1)
                    if extension_item(body, nodes, *articles[p], p) == item), default=-1)
    sources = {}
    for pos in positions:
        if pos <= previous:
            continue
        source_tag, _ = articles[pos]
        anchor = re.search(r'\bid="([^"]+)"', source_tag)
        declared = re.search(r'\bdata-claims="([^"]+)"', source_tag)
        if anchor and declared:
            for claim in declared.group(1).split():
                sources.setdefault(claim, set()).add(anchor.group(1))
    registry = where.claim_records()
    for cid in CLAIM_RE.findall(progress.group(1)):
        claim = registry.get(cid, {})
        status = claim.get('mathematical_status')
        eligible = status == 'refutation' or (status == 'working_proof' and not cid.startswith(('ex:', 'check:')))
        if eligible and any(re.search(r'#' + re.escape(anchor) + r'(?:[)\"\s]|$)', claim.get('record', ''))
                            for anchor in sources.get(cid, ())):
            return
    raise ValueError('A spell extension needs a registered proof, reduction or refutation from this '
                     'extension period; finite checks, conjectures and reused old progress do not qualify')


def kept_children(text):
    """Items a follow-up list marks Continuing: children kept when their parent closes."""
    return {(kind, item_id) for kind, item_id, item in FOLLOWUP_ITEM.findall(text)
            if (OUTCOME_RE.search(item) or [None, None])[1] == 'Continuing'}


def close(nodes, item, kept, promoted):
    """Remove a queued item; a closed parent's children close with it unless kept, which go to `promoted` (the
    finisher refuses an entry that closes a parent while keeping a sub-idea, so this arises only in old records)."""
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
    """Items one article adds, as (kind, id): its passed Outside leads and Absurd bridges (reviews, older research
    entries, which carried their own, user, 3 October 2026, and audits, all of whose items are queued), then the
    Sub-ideas any entry lists (no test: when unsure, queue it).  A section that marks picks (<li data-pick>)
    adds only its picks; the other items are dropped (user, 9 October 2026)."""
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
        picking = not kind.sub and re.search(r'<li\b[^>]*\bdata-pick\b', section.group(1))
        for n, item in enumerate(re.findall(r'<li\b(.*?)</li>', section.group(1), re.S), 1):
            if picking and not re.match(r'[^>]*\bdata-pick\b', item):
                continue
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
        words = len(strip_tags(item).split())
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
    if '<ol data-move="head">' in section.group(0):
        if len(order) != 1 or order[0] not in top:
            raise ValueError('A head promotion names exactly one queued top-level item')
        return [n for n in nodes if n.item == order[0]] + [n for n in nodes if n.item != order[0]]
    if set(order) != set(top):
        missing = [i for k, i in top if (k, i) not in order]
        unknown = [i for k, i in order if (k, i) not in top]
        raise ValueError('A Queue order lists every remaining top-level item: missing '
                         + (', '.join(missing) or 'none') + '; not queued ' + (', '.join(unknown) or 'none'))
    place = {item: n for n, item in enumerate(order)}
    return sorted(nodes, key=lambda node: place[node.item])


def reopened_by(text):
    """Items an entry reopens: follow-up list items whose outcome is Reopened, or Promoted (a sub-idea that
    waited outside the queue, see queued_arrivals)."""
    return [(kind, item_id) for kind, item_id, item in FOLLOWUP_ITEM.findall(text)
            if (OUTCOME_RE.search(item) or [None, None])[1] in ('Reopened', 'Promoted')]


MERGE_RE = re.compile(r'<strong>Follow-up\.</strong>\s*Closed: merged into ([\w:.-]*\w)')


def apply_merges(body, nodes, text, tag=None):
    """A follow-up list item closed as "merged into ID" hands its wording to that queued item, so a near
    duplicate that adds something is kept as part of the item it repeats (user, 9 October 2026).  With `tag`,
    the entry's own item does the same when the entry's own Follow-up closes it so: on 11 October 2026 an entry
    closed its item as merged, its reviewer accepted the closure on that condition, and the wording was not
    carried, the merge being read in listed items only."""
    listed = list(FOLLOWUP_ITEM.findall(text))
    work = developed_by(tag, text) if tag else None
    if work and work[1] == 'Closed':
        listed.append((work[0][0], work[0][1], FOLLOWUP_ITEM.sub('', text[len(tag):])))
    for kind, ident, item in listed:
        merged = MERGE_RE.search(item)
        target = next((n for top in nodes for n in [top] + top.children if merged and n.ident == merged.group(1)),
                      None)
        if merged and target is None:
            raise ValueError(f'{ident} is merged into {merged.group(1)}, which is not queued')
        note = f' Merged from {ident}: {item_text(body, kind, ident)}'
        if target is not None and note not in target.text:
            target.text += note


def waits_for_review(tag, text):
    """Whether an article's Sub-ideas wait outside the queue: those of a research entry that develops no queue
    item have no parent to nest under, and a review promotes the ones worth queueing (user, 9 October 2026:
    "it would read them and promote any number based on its judgement")."""
    return 'data-kind="research"' in tag and developed_by(tag, text) is None


def queued_arrivals(tag, text):
    """Arrivals without waiting Sub-ideas or items resolved in their introducing entry."""
    waiting = waits_for_review(tag, text)
    resolved = {item for group in listed_closures(tag, text) for item in group}

    def parentless(item):       # a sub-idea that names its parent (data-parent) nests there and does not wait
        listed = listed_item(item[0], text, item[1])
        return KINDS[item[0]].sub and not (listed and 'data-parent=' in listed[0])
    return [item for item in arrivals_of(tag, text)
            if item not in resolved and not (waiting and parentless(item))]


def pending_subideas(body):
    """(kind, id) of Sub-ideas that wait for a review: listed by research entries developing no queue item
    since the last review, not queued, and not already developed or closed by an entry of their own (one seeded
    into a new queue and then developed has left the queue without waiting for anything)."""
    found = parse_tree(body)
    queued = set(every_item(found[1])) if found else set()
    articles = list(record_articles(body))
    last = max((i for i, (tag, _) in enumerate(articles) if 'data-kind="review"' in tag), default=-1)
    finished = {work[0] for work in (developed_by(tag, text) for tag, text in articles)
                if work and work[1] in ('Developed', 'Closed')}
    return [item for tag, text in articles[last + 1:]
            for item in arrivals_of(tag, text)
            if item not in queued and item not in finished and item not in queued_arrivals(tag, text)]


STOP = set('with that this from have were which their there than then into also each such only when whether '
           'what does prove test check read find decide show whose where about against between every'.split())


def content_words(text):
    """Lower-case words of four or more letters in a queue line, without its ID link, markup and formulas."""
    text = re.sub(r'\\\(.*?\\\)', ' ', strip_tags(text.split('):', 1)[-1]))
    return {w for w in re.findall(r'[a-z]{4,}', text.lower())} - STOP


BUILT_AT = 0.4


def built_items(nodes, text, threshold=BUILT_AT):
    """[(share, id), ...], most alike first: queued top-level build items of whose content words a commit's
    message and file names have the share `threshold` or more.  On 11 October 2026 three build items stayed
    queued after the commits that built most of them; measured on that day's 88 commits to the framework, nine
    got ten lines at 0.4, seven naming the item the commit worked on and three false.  A hint to read the item."""
    words = content_words('): ' + text.replace('/', ' ').replace('_', ' '))
    out = []
    for node in nodes:
        item = content_words(node.text)
        if node.kind == 'build' and len(item) >= 5 and len(words & item) / len(item) >= threshold:
            out.append((round(len(words & item) / len(item), 2), node.ident))
    return sorted(out, reverse=True)


def built(root, rev='HEAD'):
    """The lines for a commit: the build items, queued in any notebook as the commit `rev` left it and already
    queued before it, that its message and file names resemble.  Everything is read from the commit, not from
    the working tree."""
    def git(*args):
        result = subprocess.run(['git', '-C', str(root), *args], capture_output=True, text=True)
        return result.stdout if result.returncode == 0 else ''
    files = git('show', '--name-only', '--format=', rev)
    if not any(name.startswith(('tools/', 'compute.sh', 'AGENTS.md', '.claude/')) for name in files.split()):
        return []
    text = git('show', '-s', '--format=%B', rev) + ' ' + files
    lines = []
    for path in ['notebook.html', *sorted(git('ls-tree', '--name-only', rev, 'research/branches/').split())]:
        path = path if path.endswith('.html') else f'{path}/notebook.html'
        tree = parse_tree(git('show', f'{rev}:{path}'))
        hits = built_items(tree[1], text) if tree else []
        if hits:        # an item the commit itself queued shares its words with the commit and is not built by it
            before = parse_tree(git('show', f'{rev}~1:{path}'))
            hits = [hit for hit in hits if before and hit[1] in {node.ident for node in before[1]}]
        for share, ident in hits:
            lines.append(f'This commit resembles the queued build item {ident} of {path} '
                         f'({share} of its words): read the item, and if the commit builds it or part of it, say '
                         'so in the next entry on it, which closes it or names what is left.')
    return lines


def similar_items(nodes, threshold=0.5):
    """Pairs of queued items with much wording in common, [(share, id, id)], most alike first: the share is
    the common content words over those of the shorter item.  A hint to merge, not a verdict."""
    flat = [(n.ident, content_words(n.text)) for top in nodes for n in [top] + top.children]
    out = []
    for i, (a, wa) in enumerate(flat):
        for b, wb in flat[i + 1:]:
            if min(len(wa), len(wb)) >= 5:
                share = len(wa & wb) / min(len(wa), len(wb))
                if share >= threshold:
                    out.append((round(share, 2), a, b))
    return sorted(out, reverse=True)


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
    text = html.unescape(re.sub(r'\s+', ' ', strip_tags_tight(listed[1])).strip())
    short = text[:220]
    while short.count('\\(') > short.count('\\)'):   # never cut inside inline math
        short = short[:short.rindex('\\(')].rstrip()
    return html.escape(short + ('…' if len(short) < len(text) else ''), quote=False)



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
    closed = sum(listed_closures(tag, text), [])     # listed Developed sub-ideas leave the queue too
    apply_merges(body, nodes, text, tag)
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
    place_arrivals(body, nodes, tag, text, queued_arrivals(tag, text), reopened_by(text))
    apply_marks(nodes, text)
    return ordered(tag, text, nodes)


def review_build_completion(tag, items, nodes):
    """A review records one completed standalone build, not a batch or open children."""
    if 'data-kind="review"' not in tag or len(items) != 1:
        return False
    item = items[0]
    parent, node = locate(nodes, item)
    return item[0] == 'build' and parent is None and node is not None and not node.children


def item_history_problems(body, nodes, articles, tag, text, work, before):
    """The refusals, in the order check() raises them, of an entry developing queue item work[0] against the item's
    earlier record: an unlinked last development, unread earlier entries, a return to an item the last review left,
    an unaccounted named attempt and unmentioned open sub-ideas.  None of them depends on the queue section, so
    notebook-append.py runs them on a draft before it is appended (16 October 2026: four refusals of one entry
    came only from the finisher, each after the claims had been registered, which a fix of the entry made stale)."""
    found = []
    earlier = unlinked_earlier_entry(body, nodes, articles, work[0])
    if earlier:
        found.append(f'This entry develops an item that, or whose parent, was last developed in #{earlier}: link that '
                     'entry, after reading it, so that work already recorded on the item is not repeated '
                     '(AGENTS.md, restoration and research discipline)')
    unread = unread_item_entries(articles, work[0])
    if unread:
        found.append(f'This entry develops an item that has at most {READ_ALL_LIMIT} earlier entries, counting '
                     'those on the item itself and those on sub-ideas they listed, and for some of them it '
                     'lacks: ' + ', '.join(f'#{anchor} ({what})' for anchor, what in unread) + f'. Link each '
                     f'after reading it and quote {QUOTED_WORDS} consecutive words of its Follow-up (of its '
                     'title when that is shorter), or name it by its anchor after <strong>Unread.</strong> with the reason it '
                     'was not read (tools/lead_queue.py, unread_item_entries)')
    left = left_by_last_review(body, nodes, articles, work[0])
    if left:
        found.append(f'The last review, #{left}, names this entry\'s item, or its parent, among the items it '
                     'leaves (data-left-items): develop another item, or say after <strong>Returns.</strong>, '
                     'in at least 40 characters, why this entry returns to it (AGENTS.md)')
    owed = unaccounted_attempt(articles, work[0])
    if owed:
        found.append(f'The item\'s last entry, #{owed}, named a next attempt: say after <strong>Owed '
                     'attempt.</strong>, in at least 40 characters, that it was made, with its outcome, or '
                     'why another attempt came first (AGENTS.md; a named reading was displaced three times)')
    silent = unstated_subideas(tag, text, work[0], before[1] if before else nodes)
    if silent:
        found.append('This entry develops an item with open sub-ideas it does not mention: give each a '
                     'follow-up list item with its outcome (Closed, Developed or Continuing): '
                     + ', '.join(silent) + ' (AGENTS.md; a sub-idea answered by a later entry stayed queued)')
    return found


def draft_item_problems(body):
    """item_history_problems for the last article of `body`, a notebook with a drafted entry appended but its
    queue section not yet updated; [] when the entry develops no queue item or the notebook has no queue."""
    section = SECTION_RE.search(body)
    now = parse_tree(body)
    if now is None or not section:
        return []
    articles = record_articles(body)
    if not articles:
        return []
    tag, text = articles[-1]
    work = developed_by(tag, text)
    if not work:
        return []
    nodes = now[1]
    return item_history_problems(body, nodes, articles, tag, text, work, now)


def check(head_body, body, path=None, root=None):
    """Raise ValueError if the queue in `body` breaks the rules relative to `head_body` (HEAD's notebook).
    The entry checked is the last Research-record article of `body`; `path` is the notebook's file, against whose
    directory its relative links resolve, and `root` the repository (default: this one)."""
    # both sections are read under the committed notebook's settings, so a commit changing them (a move
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
    count = undeclared_review_count(tag, draining, nodes)
    if count is not None:
        raise ValueError(f'A review of a draining queue declares data-queue-items="{count}", the number of top-level '
                         'items now queued, so that the next cycles see whether the queue shrinks (AGENTS.md)')
    unknown = unknown_left_items(tag, nodes)
    if unknown:
        raise ValueError('The review\'s data-left-items names items that are not queued: ' + ', '.join(unknown)
                         + ': give the queue\'s own identifiers, since a mistyped one leaves nothing')
    if work:
        problems = item_history_problems(body, nodes, articles, tag, text, work, before)
        if problems:
            raise ValueError(problems[0])
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
    validate_spell_extension(body, tag, text, nodes, where)
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
        # builds closed by close-built, each recorded in the ledger with its evidence, leave without an entry
        present = {n.ident for n in nodes}
        removed = [n for n in before[1] if n.ident not in present]
        if removed:
            top = Path(root or ROOT)
            relative = Path(path).resolve().relative_to(top.resolve()).as_posix() if path else None
            ledger = closure_ledger(top)
            for node in removed:
                row = ledger.get((relative, node.ident))
                if node.kind != 'build' or node.children or row is None:
                    raise ValueError(f'{node.ident} left the queue in a commit without an entry: only a build with '
                                     'no sub-ideas leaves so, through lead_queue.py close-built, which records it '
                                     f'in {CLOSURES}')
                problems = closure_problems(row, top)
                if problems:
                    raise ValueError(f'{node.ident}: the closure in {CLOSURES} is incomplete: ' + '; '.join(problems))
        remaining = [n for n in before[1] if n.ident in present]
        kept, added = nodes[:len(remaining)], nodes[len(remaining):]
        if (shape(kept) != shape(remaining) or marks(nodes) != marks(remaining)
                or any(n.children or admitter(n) is None for n in added)
                or draining != draining_after(before[0], nodes)):
            raise ValueError('A commit that adds no Research-record entry changes the queue only by appending, at the '
                             'tail, the checks, builds and ideas lead_queue.py add writes')
        for node in added:
            problems = admitter(node)(body, head_body, node.item)
            if problems:
                raise ValueError(f'{node.ident} ({node.kind}) may not join the queue: ' + '; '.join(problems))
        return
    if before is None:
        if work or batch:
            raise ValueError('The commit that creates the queue may not develop queue items: run lead_queue.py init, '
                             'commit the section, then develop its head')
        wanted = open_tree(body)
        admitted = [n for n in nodes if admitter(n) is not None]
        for node in admitted:
            problems = admitter(node)(body, head_body, node.item)
            if problems:
                raise ValueError(f'{node.ident} ({node.kind}) may not join the queue: ' + '; '.join(problems))
        seeded = [n for n in nodes if n not in admitted]
        items = every_item(seeded)
        if shape(seeded) != shape(wanted) or marks(nodes):
            have, want = set(items), set(every_item(wanted))
            raise ValueError('A new queue holds exactly the listed items not closed, sub-ideas under their parents: '
                             'missing ' + (', '.join(i for _, i in want - have) or 'none') + '; not open '
                             + (', '.join(i for _, i in have - want) or 'none') + '; otherwise the placement differs '
                             '(lead_queue.py init writes it; a queue created before the entries it must seed '
                             'is rebuilt by removing the section and running init again)')
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
        raise ValueError(TRIAGE_RETIRED)
    closed, developed = listed_closures(tag, text)
    listed_developed = [item for item in developed if item in every_item(old)]
    if listed_developed:
        # A scheduled review may record one completed standalone build. It is not a
        # research spell and must not restore multi-item triage or close open children.
        review_build = review_build_completion(tag, closed + listed_developed, old)
        # sub-ideas of the one top-level item the entry develops may be batched (user, 9 October 2026)
        own = locate(old, work[0]) if work else (None, None)
        group = own[0] or own[1]
        outside = [i for k, i in listed_developed
                   if group is None or locate(old, (k, i))[0] is not group]
        if outside and not review_build:
            raise ValueError('A follow-up list marks Developed only sub-ideas of the top-level item the entry '
                             'develops (one top-level item per entry; its sub-ideas may be batched): '
                             + ', '.join(outside))
        closed = closed + listed_developed
    head = head_of(old)
    first = next((c for c in head.children if not c.waits), None) if head else None
    if work:
        located = locate(old, work[0])[1]
        if located is None:
            raise ValueError(f'{work[0][1]} is not queued')
        if not chosen and work[0] not in [n.item for n in (head, first) if n is not None]:
            if not CHOSEN_RE.search(text):
                raise ValueError(f'The head is the default: this entry develops {work[0][1]}, but the head is '
                                 f'{head.ident if head else "none (every item waits)"}' + (f' and its first '
                                 f'sub-idea {first.ident}' if first else '') + '. To develop another item, say in '
                                 'a <strong>Chosen.</strong> paragraph which open statement it bears on and why '
                                 'it comes first; the user may also pick one (data-picked)')
            top = locate(old, work[0])[0] or located
            if spell(body, top.item, old) > spell_limit(body, top.item, old):
                raise ValueError(f'{top.ident} has reached the boundary of its spell: develop another item first, '
                                 'or earn an extension (data-spell-extend)')
        window = SETTINGS.get('spell_window')       # the head too: its rotation does not see interleaved entries
        top = locate(old, work[0])[0] or located
        # not for a queue with no other item to take, nor for the entry that removes the item
        if (window and not chosen and len(old) > 1 and work[1] not in ('Closed', 'Developed')
                and window_count(body, top.item, old, window) > spell_limit(body, top.item, old)):
            raise ValueError(f'{top.ident} has had more entries among the last {window} on queued items than '
                             'its spell allows (data-spell-window): develop another item first')
        if work[1] == 'Developed' and [c for c in located.children if c.item not in closed]:
            raise ValueError(f'{work[0][1]} still has open sub-ideas, so it is not Developed; it is Continuing')
        staying = [c.ident for c in located.children if c.item in kept_children(text)]
        if work[1] == 'Closed' and staying:
            raise ValueError(f'{work[0][1]} keeps sub-ideas open ({", ".join(staying)}), so it is not Closed; it '
                             'is Continuing: sub-ideas belong to their item and do not become items of their own '
                             'when it closes (user, 10 October 2026)')
    draining_before = SETTINGS['backpressure'] and (was_draining or len(old) >= CAP)
    validate_review_generation(tag, text, draining_before)
    if draining_before and counted(tag, text) and not work and not batch and head is not None:
        raise ValueError(f'The queue is draining ({len(old)} items; backpressure from {CAP} until {FLOOR}): this '
                         f'entry must develop the head, {head.ident}, tagged data-{head.kind}="{head.ident}", '
                         'or its first sub-idea')
    expected = transition(body, old, tag, text)
    known = set(every_item(old)) | set(every_item(expected))
    for node in nodes:
        if node.item in known or admitter(node) is None:
            continue
        problems = admitter(node)(body, head_body, node.item)
        if problems:
            raise ValueError(f'{node.ident} ({node.kind}) may not join the queue: ' + '; '.join(problems))
        expected.append(node.copy())
    if shape(nodes) != shape(expected):
        raise ValueError('Queue update: keep the earlier items in order; remove a Closed or Developed item (a closed '
                         'parent\'s sub-ideas close with it unless a follow-up keeps one Continuing, which goes to the '
                         'tail); if Continuing, keep the head until its current spell boundary '
                         '(four, plus earned two-cycle extensions), then '
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
    def plain(node):     # with its ID first, which a lead's text has and a kind module's idea has not
        text = html.unescape(re.sub(r'\s+', ' ', strip_tags_tight(node.text)).strip())
        return text if text.startswith(node.ident) else f'{node.ident}: {text}'
    for n, node in enumerate(nodes[:count], 1):
        out.append(f'{n}. {plain(node)}{waiting_note(node)}')
        out += [f'   - {plain(c)}{waiting_note(c)}' for c in node.children]
    return out


def settle(body, nodes, end=None):
    """`nodes` with the head moved to the tail if the record (cut by `end`, as in `spell`) already owes it that
    move: its spell is complete though the queue still has it first, as a queue committed before a spell rule was
    enforced can.  On a queue the tools kept, the head is below its current spell limit and nothing moves."""
    head = head_of(nodes)
    if head is not None and len(nodes) > 1 and spell(body, head.item, nodes, end) >= spell_limit(body, head.item, nodes, end):
        nodes.remove(head)
        nodes.append(head)
    return nodes


def end_spell(body, nodes, top, picked, before=None):
    """Move `top` with its sub-ideas to the tail when it is the head and the entry ending `body` reaches the current boundary of
    its spell, counted against the queue `before` that entry (default: `body`'s); a picked entry neither counts
    toward nor ends a spell."""
    if (top is not None and top in nodes and not picked and top is head_of(nodes)
            and spell(body, top.item, before) >= spell_limit(body, top.item, before)):
        nodes.remove(top)
        nodes.append(top)


def done(body, outcome):
    """The notebook with the item the last entry develops removed (Closed, Developed; a parent's sub-ideas close
    with it unless the entry keeps one Continuing, which goes to the tail), or kept (Continuing: a head keeps its
    place before its current boundary, including earned extensions, then moves with its sub-ideas to the tail), and the draining flag
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
    apply_merges(body, nodes, text, tag)
    for item in sum(listed_closures(tag, text), []):
        close(nodes, item, kept_children(text), promoted)
    nodes += promoted
    before = len(every_item(nodes))
    place_arrivals(body, nodes, tag, text, queued_arrivals(tag, text), reopened_by(text))
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


ADDABLE = ('check', 'build', 'idea')


def add(body, kind, ident, source, text):
    """The notebook with item `ident` of `kind` (one of ADDABLE) appended at the tail; ValueError if an item of
    that ID is queued already or the line is malformed."""
    found = parse_tree(body)
    if found is None:
        raise ValueError('The notebook has no lead and bridge queue: run init first')
    draining, nodes = found
    if any(i == ident for _, i in every_item(nodes)):
        raise ValueError(f'{ident} is already queued')
    if kind == 'build' and build_evidence(text):
        raise ValueError(f'{ident}: {build_evidence(text)}')
    # The last entry of the record when the item is added: a source given in words (a review, a conversation)
    # names no entry, and the finisher's check of a review's period could not tell when such an item was queued.
    articles = record_articles(body)
    last = re.search(r'\bid="([^"]+)"', articles[-1][0]) if articles else None
    after = f' data-after="{last.group(1)}"' if last else ''
    node = Node(kind, ident, f' data-{kind}="{ident}" data-source="{html.escape(source)}"{after}',
                added_text(source, text))
    nodes.append(node)
    updated = rewrite(body, nodes, draining_after(draining, nodes))
    problems = admitter(node)(updated, None, node.item)
    if problems:
        raise ValueError('; '.join(problems))
    return updated


CLOSURES = 'research/queue-closures.jsonl'     # tracked: one line per build closed without an entry
CLOSURE_NOTE = 40                               # characters a closure note needs at least


def closure_ledger(root=None):
    """{(notebook path relative to the repository, item identifier): ledger row} of builds closed by close-built."""
    path = Path(root or ROOT) / CLOSURES
    rows = {}
    for line in path.read_text().splitlines() if path.exists() else []:
        try:
            row = json.loads(line)
        except ValueError:
            continue
        rows[(row.get('notebook'), row.get('ident'))] = row
    return rows


def closure_problems(row, root=None):
    """What a ledger row lacks: the implementation paths it names exist, its reviewer record is a *review*.txt
    file that exists, and its note says what was built in at least CLOSURE_NOTE characters."""
    root = Path(root or ROOT)
    problems = []
    if len(row.get('note', '').strip()) < CLOSURE_NOTE:
        problems.append(f'its note says in fewer than {CLOSURE_NOTE} characters what was built (or measured)')
    record = row.get('record', '')
    if not re.search(r'review[^/]*\.txt$', record) or not (root / record).is_file():
        problems.append(f'its reviewer record {record or "(none)"} is not an existing *review*.txt file')
    paths = row.get('paths') or []
    if not paths:
        problems.append('it names no implementation path')
    problems += [f'its implementation path {p} does not exist' for p in paths if not (root / p).exists()]
    return problems


def close_built(body, notebook, ident, record, paths, note, root=None, today=None, falsified=False):
    """(the notebook without build `ident`, the ledger row recording why): a top-level build with no sub-ideas,
    built in a framework commit, leaves the queue without an entry, as `add` let it join without one.

    With `falsified`, the build leaves without being built, because a measurement showed that its mechanism
    does not do what it was queued for: the row says so ("outcome": "falsified"), its note says what was
    measured, and its paths are the measurement and whatever replaced the mechanism (16 October 2026: a
    registry search queued to find a test's missed claims ranked them hundreds deep, and the only way out
    of the queue recorded it as built).

    Until 16 October 2026 a build left the queue only through an entry developing it or, one per review, a
    route review; six builds finished in one framework turn would have waited six reviews, swelling a draining
    queue (user: "Isn't that a gap in the framework? Why can't you close items")."""
    found = parse_tree(body)
    if found is None:
        raise ValueError('The notebook has no lead and bridge queue')
    draining, nodes = found
    node = next((n for n in nodes if n.ident == ident), None)
    if node is None:
        raise ValueError(f'{ident} is not a top-level queued item')
    if node.kind != 'build':
        raise ValueError(f'{ident} is a {node.kind}: only builds close this way; other items close in an entry')
    if node.children:
        raise ValueError(f'{ident} has sub-ideas: they close in an entry with it')
    import datetime
    row = {'notebook': notebook, 'ident': ident, 'text': ' '.join(html.unescape(strip_tags(node.text)).split()),
           'note': note, 'record': record, 'paths': list(paths),
           'date': (today or datetime.date.today()).isoformat()}
    if falsified:
        row['outcome'] = 'falsified'
    problems = closure_problems(row, root)
    if falsified and not re.search(r'\bmeasur(?:ed|ement)\b', note, re.I):
        problems.append('its note does not say what was measured, which a falsified build rests on')
    if problems:
        raise ValueError(f'{ident} cannot close: ' + '; '.join(problems))
    nodes = [n for n in nodes if n is not node]
    return rewrite(body, nodes, draining_after(draining, nodes)), row


COST_CLAIM = re.compile(
    r'\b(?:sav(?:e|es|ing|ings)|faster|slow(?:er|ly|s|ed)?|speeds? up|costs?|wastes?|halves?|shorten(?:s|ed)?|cheaper|'
    r'most of (?:it|its|the|that)|(?:takes?|took|spen[dt]s?)\b[^.;:]{0,60}?\b(?:\d[\d.,]*\s*(?:s|ms|min|h)|seconds?|minutes?|hours?))\b',
    re.I)


def build_evidence(text):
    """What a build's text lacks, or None: a text that claims a cost or a saving (slow, saves, took 27 s)
    says whether the claim is measured, with the word: 'measured' and what was, or 'not measured'.  A figure
    alone does not say it: the build that prompted this rule gave figures of a census and guessed their cause,
    and promised a saving for several cycles that one measurement refuted (10 October 2026)."""
    claim = COST_CLAIM.search(text)
    if claim and not re.search(r'\bmeasur(?:ed|ement|ements)\b', text, re.I):
        return (f'the text claims a cost or a saving ("{claim.group(0)}") and does not say what it rests on: name '
                'the measurement ("measured: ...", with where it is saved), or write "not measured"')
    return None


def added_text(source, text):
    """An added item's line: its text, then a link to the entry it came up in when SOURCE is one."""
    link = f' (<a href="#{html.escape(source)}">source</a>)' if source.startswith('entry-') else ''
    return html.escape(text, quote=False) + link


def edit(body, ident, text):
    """The notebook with the text of queued item `ident`, one `add` wrote, replaced and its source kept; ValueError
    if no such item is queued, or an entry listed it, since such an item's text is that entry's."""
    found = parse_tree(body)
    if found is None:
        raise ValueError('The notebook has no lead and bridge queue: run init first')
    draining, nodes = found
    node = next((n for n in nodes + [c for n in nodes for c in n.children] if n.ident == ident), None)
    if node is None:
        raise ValueError(f'{ident} is not queued')
    source = re.search(r'\bdata-source="([^"]*)"', node.attrs)
    if source is None:
        raise ValueError(f'{ident} was listed by an entry, so its text is that entry\'s: only an item add wrote is '
                         'edited here')
    if node.kind == 'build' and build_evidence(text):
        raise ValueError(f'{ident}: {build_evidence(text)}')
    node.text = added_text(html.unescape(source.group(1)), text)
    return rewrite(body, nodes, draining)


def main(argv):
    if len(argv) in (2, 3) and argv[1] == 'built':
        print('\n'.join(built(Path.cwd(), argv[2] if len(argv) == 3 else 'HEAD')), end='')
        return 0
    if len(argv) == 7 and argv[1] == 'add' and argv[3] in [f'--{k}' for k in ADDABLE]:
        path = Path(argv[2])
        try:
            path.write_text(add(path.read_text(), argv[3][2:], argv[4], argv[5], argv[6]))
        except ValueError as error:
            print(error, file=sys.stderr)
            return 1
        kind = argv[3][2:]
        article = 'an' if kind[0] in 'aeiou' else 'a'
        print(f'Appended {argv[4]}, {article} {kind}; {len(parse_tree(path.read_text())[1])} items in the queue.')
        return 0
    if len(argv) >= 3 and argv[1] == 'close-built':
        import argparse
        parser = argparse.ArgumentParser(prog='lead_queue.py close-built')
        parser.add_argument('notebook')
        parser.add_argument('ident')
        parser.add_argument('--record', required=True, help='the reviewer record, a *review*.txt file')
        parser.add_argument('--path', action='append', required=True, help='an implementation path (repeatable)')
        parser.add_argument('--note', required=True, help='what was built, with its measured checks')
        parser.add_argument('--falsified', action='store_true',
                            help='not built: a measurement showed its mechanism fails its purpose (the note says '
                                 'what was measured; the paths name the measurement and any replacement)')
        args = parser.parse_args(argv[2:])
        import notebooks
        path = Path(notebooks.notebook_file(args.notebook))
        relative = path.resolve().relative_to(ROOT.resolve()).as_posix()
        try:
            body, row = close_built(path.read_text(), relative, args.ident, args.record, args.path, args.note,
                                    falsified=args.falsified)
        except ValueError as error:
            print(error, file=sys.stderr)
            return 1
        with (ROOT / CLOSURES).open('a') as ledger:
            ledger.write(json.dumps(row, ensure_ascii=False) + '\n')
        path.write_text(body)
        print(f'Closed {args.ident} as {"falsified by measurement" if args.falsified else "built"}, recorded in {CLOSURES}; '
              f'{len(parse_tree(body)[1])} items in the queue. Stage the ledger with the notebook.')
        return 0
    if len(argv) == 5 and argv[1] == 'edit':
        path = Path(argv[2])
        try:
            path.write_text(edit(path.read_text(), argv[3], argv[4]))
        except ValueError as error:
            print(error, file=sys.stderr)
            return 1
        print(f'Edited {argv[3]}.')
        return 0
    if len(argv) in (3, 5) and argv[1] == 'check' and (len(argv) == 3 or argv[3] == '--base'):
        status, error = staged_check(argv[2], argv[4] if len(argv) == 5 else 'HEAD')
        if error:
            print(error, file=sys.stderr)
        return status
    if len(argv) == 3 and argv[1] == 'append':
        path = Path(argv[2])
        old = path.read_text()
        was = set(every_item(parse_tree(old)[1])) if parse_tree(old) else set()
        body, count = append_new(old)
        path.write_text(body)
        print(f'Appended {count} items; ' + head_lines(body, 0)[0])
        nodes = parse_tree(body)[1]
        new = {ident for _, ident in set(every_item(nodes)) - was}
        for share, a, b in similar_items(nodes):
            if a in new or b in new:
                print(f'Similar wording ({share}): {a} and {b}. If they ask the same thing, keep one: in a '
                      'follow-up list close the other with "Closed: merged into ID", which adds its wording to ID')
        waiting = pending_subideas(body)
        if waiting:
            print(f'{len(waiting)} sub-ideas wait for the next review to promote them (Follow-up. Promoted: '
                  'reason): ' + ', '.join(i for _, i in waiting))
        return 0
    if len(argv) == 3 and argv[1] in ('similar', 'pending'):
        body = Path(argv[2]).read_text()
        if argv[1] == 'pending':
            print('\n'.join(i for _, i in pending_subideas(body)) or 'No sub-ideas wait for a review')
        else:
            print('\n'.join(f'{share}  {a}  {b}' for share, a, b in similar_items(parse_tree(body)[1]))
                  or 'No similar queued items')
        return 0
    if len(argv) == 4 and argv[1] == 'linkers':
        try:
            rows = linking_entries(Path(argv[2]).read_text(), argv[3])
        except ValueError as error:     # an identifier two kinds share: the forms to choose from
            print(error, file=sys.stderr)
            return 1
        if rows is None:
            print(f'{argv[3]} is not queued, or no entry of the record queued it: nothing to look for.')
            return 1
        print('\n'.join(rows))
        print(f'{len(rows)} later entries that did not develop it link the entry that queued {argv[3]}.')
        return 0
    if len(argv) == 3 and argv[1] == 'nearby':
        body = Path(argv[2]).read_text()
        claims = registered_claims()
        rows = answered_report(body, claims)
        for ident, matches in rows:
            print(ident)
            print('\n'.join(f'  {score} {claim} in #{anchor}' for score, claim, anchor in matches))
        print(f'{len(rows)} queued items without an entry, builds left out, each with at most {ELSEWHERE} claims of '
              f'later entries on other items nearest to its text, with the search\'s score; {len(claims)} '
              f'registered claims and {len(record_articles(body))} entries read. A reading list, not a verdict: '
              'every item gets one, answered or not.')
        older, some, unknown = older_nearest(body, claims)
        print(f'{older} of the {some} queued items with a known queuing entry and a nearest claim, builds left out, '
              'have that claim, in one ranking of both sides, in an entry up to the queuing; the status of an item '
              f'lists those too, marked [earlier]. {unknown} more items name no queuing entry of the record and '
              'have no earlier side.')
        return 0
    if len(argv) >= 5 and argv[1] == 'places':            # places NOTEBOOK ID CLAIM...
        print('\n'.join(claim_places(Path(argv[2]).read_text(), registered_claims(), argv[3], argv[4:])))
        return 0
    if len(argv) == 3 and argv[1] == 'survey':
        rows = survey(Path(argv[2]).read_text())
        print('kind\titem\tentries\topen sub-ideas\tlatest outcome\tlatest names an attempt\tattempts unreported')
        print('\n'.join('\t'.join(str(value) for value in row) for row in rows))
        untouched = sum(1 for row in rows if row[2] == 0)
        print(f'{len(rows)} items: {untouched} with no entry; '
              f'{sum(1 for row in rows if row[2] and not row[3] and not row[5])} with entries, no open sub-idea '
              'and no attempt named by the latest follow-up')
        return 0
    if len(argv) in (4, 5) and argv[1] == 'history' and (len(argv) == 4 or argv[4] == '--status'):
        body = Path(argv[2]).read_text()
        if len(argv) == 5:
            try:
                print('\n'.join(item_status(body, argv[3], *registered())))
            except ValueError as error:
                print(error, file=sys.stderr)
                return 1
            return 0
        try:
            rows = history(body, argv[3])
        except ValueError as error:
            print(error, file=sys.stderr)
            return 1
        print('\n'.join(f'{anchor}\t{ident}\t{outcome}' for anchor, ident, outcome in rows)
              or f'No entry has developed {argv[3]}, its group or a member of it')
        return 0
    if len(argv) == 3 and argv[1] == 'triage':
        print(TRIAGE_RETIRED, file=sys.stderr)
        return 1
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
