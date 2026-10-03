#!/usr/bin/env python3
"""The lead and bridge queue (user, 3 October 2026: "I don't want promising leads/bridges to be dropped").

Every Outside lead and Absurd bridge that passed its cheap test in a route review waits in one FIFO queue,
the living section <section id="lead-queue">, the last section before the Research record.  It has no word
budget (notebook_context.py skips it) and restoration reads only its head (resume.py).  Rules, checked by
finish-turn.py against HEAD:

- The queue holds exactly the passed items not yet closed, once each.  A review appends its newly passed
  items at the end.
- A research entry develops at most one item, always the head, tagged data-lead or data-bridge="ANCHOR:N",
  and states <strong>Follow-up.</strong> Closed (the attempt's reason), Developed (taken into a result or
  route) or Continuing.  Closed and Developed remove the item; Continuing moves it to the tail.
- Backpressure: at CAP items the section carries data-draining="true"; then every research entry develops
  the head until the queue is down to FLOOR items, when the flag is removed.

Usage: lead_queue.py init NOTEBOOK.html  (adds the section, oldest items first, if it is absent)
       lead_queue.py head NOTEBOOK.html  (the first HEAD_READ items, as restoration prints them)
       lead_queue.py done NOTEBOOK.html Closed|Developed|Continuing  (after developing the head)"""
import html
import re
import sys
from pathlib import Path

CAP, FLOOR, HEAD_READ = 50, 20, 5
SECTION_RE = re.compile(r'<section id="lead-queue"([^>]*)>(.*?)</section>', re.S)
ITEM_RE = re.compile(r'<li data-(lead|bridge)="([^"]+)"[^>]*>(.*?)</li>', re.S)
LEADS_RE = re.compile(r'<h4>Outside leads</h4>\s*<ul>(.*?)</ul>', re.S)
BRIDGES_RE = re.compile(r'<h4>Absurd bridges</h4>\s*<ul>(.*?)</ul>', re.S)
TEST_PASSED = re.compile(r'<strong>Test\.</strong>\s*Passed\b')
OUTCOME_RE = re.compile(r'<strong>Follow-up\.</strong>\s*(Developed|Continuing|Closed)\b')
FOLLOWUP_ITEM = re.compile(r'<li\b[^>]*data-(lead|bridge)="([^"]+)"[^>]*>(.*?)</li>', re.S)
ARTICLE_RE = re.compile(r'<article\b[^>]*>.*?</article>', re.S)


def record_articles(body):
    """(tag, text) of the Research-record articles, in order."""
    start = body.find('<section id="research-record">')
    if start < 0:
        return []
    out = []
    for m in ARTICLE_RE.finditer(body, start):
        text = m.group(0)
        out.append((text[:text.index('>') + 1], text))
    return out


def developed_by(tag, text):
    """((kind, id), outcome) for a research entry developing a queue item, or None."""
    if 'data-kind="research"' not in tag:
        return None
    found = re.search(r'\bdata-(lead|bridge)="([^"]+)"', tag)
    if not found:
        return None
    outcome = OUTCOME_RE.search(text)
    return (found.group(1), found.group(2)), outcome.group(1) if outcome else None


def open_items(body):
    """Passed, unclosed items as (kind, id), in record order: per review, leads then bridges."""
    passed, closed = [], set()
    for tag, text in record_articles(body):
        ident = re.search(r'\bid="([^"]+)"', tag)
        if 'data-kind="review"' in tag and ident:
            for kind, pattern in (('lead', LEADS_RE), ('bridge', BRIDGES_RE)):
                section = pattern.search(text)
                if section:
                    for n, item in enumerate(re.findall(r'<li\b(.*?)</li>', section.group(1), re.S), 1):
                        if TEST_PASSED.search(item):
                            passed.append((kind, f'{ident.group(1)}:{n}'))
            # follow-up lists of reviews (the earlier form) may close items
            for kind, item_id, item in FOLLOWUP_ITEM.findall(text):
                outcome = OUTCOME_RE.search(item)
                if outcome and outcome.group(1) == 'Closed':
                    closed.add((kind, item_id))
        work = developed_by(tag, text)
        if work and work[1] in ('Closed', 'Developed'):
            closed.add(work[0])
    return [p for p in passed if p not in closed]


def parse(body):
    """(draining, [(kind, id)]) of the queue section, or None if the notebook has none."""
    found = SECTION_RE.search(body)
    if found is None:
        return None
    return 'data-draining="true"' in found.group(1), [(k, i) for k, i, _ in ITEM_RE.findall(found.group(2))]


def item_text(body, kind, ident):
    """A short description of a review item, for the queue line."""
    anchor, n = ident.rsplit(':', 1)
    art = re.search(r'<article\b[^>]*\bid="' + re.escape(anchor) + r'"[^>]*>.*?</article>', body, re.S)
    if art is None:
        return ''
    section = (LEADS_RE if kind == 'lead' else BRIDGES_RE).search(art.group(0))
    items = re.findall(r'<li\b[^>]*>(.*?)</li>', section.group(1), re.S) if section else []
    if int(n) > len(items):
        return ''
    text = re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', '', items[int(n) - 1])).strip()
    short = text[:220]
    while short.count('\\(') > short.count('\\)'):   # never cut inside inline math
        short = short[:short.rindex('\\(')].rstrip()
    return html.escape(short + ('…' if len(short) < len(text) else ''), quote=False)


def render(body, items, draining):
    lines = [f'<li data-{kind}="{ident}"><a href="#{ident.rsplit(":", 1)[0]}">{ident}</a> ({kind}): '
             f'{item_text(body, kind, ident)}</li>' for kind, ident in items]
    flag = ' data-draining="true"' if draining else ''
    return (f'<section id="lead-queue"{flag}>\n<h2>Lead and bridge queue</h2>\n<p>Passed Outside leads and Absurd '
            'bridges awaiting development, oldest first (FIFO); rules in <code>tools/lead_queue.py</code>.</p>\n<ol>\n'
            + '\n'.join(lines) + '\n</ol>\n</section>\n')


def check(head_body, body):
    """Raise ValueError if the queue in `body` breaks the rules relative to `head_body` (HEAD's notebook).
    The entry checked is the last Research-record article of `body`."""
    if not re.search(r'data-route-item="', body):
        return
    now = parse(body)
    if now is None:
        raise ValueError('The notebook needs its lead and bridge queue: run python3 tools/lead_queue.py init '
                         'NOTEBOOK.html, review the section, and commit it with this entry (AGENTS.md)')
    draining, queue = now
    if len(set(queue)) != len(queue):
        raise ValueError('The lead and bridge queue lists an item twice')
    wanted = open_items(body)
    missing = [i for k, i in wanted if (k, i) not in queue]
    stale = [i for k, i in queue if (k, i) not in wanted]
    if missing:
        raise ValueError('Passed leads or bridges missing from the queue (append new ones at its end): '
                         + ', '.join(missing))
    if stale:
        raise ValueError('Queue items that are closed or are not passed review items: ' + ', '.join(stale)
                         + '. Remove a Closed or Developed item; a Continuing one moves to the tail')
    articles = record_articles(body)
    tag, text = articles[-1] if articles else ('', '')
    work = developed_by(tag, text)
    if work and work[1] is None:
        raise ValueError('An entry developing a queue item states "<strong>Follow-up.</strong> Closed: <reason>", '
                         '"Developed ..." or "Continuing ..."')
    before = parse(head_body) if head_body else None
    if before is None:
        if len(queue) >= CAP and not draining:
            raise ValueError(f'The queue has {len(queue)} items, at least {CAP}: mark the section '
                             'data-draining="true"')
        return
    was_draining, old = before
    head = old[0] if old else None
    if work and work[0] != head:
        raise ValueError(f'Queue items are developed oldest first: this entry develops {work[0][1]}, but the head '
                         f'is {head[1] if head else "empty"}')
    draining_before = was_draining or len(old) >= CAP
    if draining_before and 'data-kind="research"' in tag and not work:
        raise ValueError(f'The queue is draining ({len(old)} items; backpressure from {CAP} until {FLOOR}): this '
                         f'research entry must develop the head, {head[1]}, tagged data-{head[0]}="{head[1]}"')
    expected = [i for i in old if i in queue and (not work or i != work[0])]
    if work and work[1] == 'Continuing':
        expected.append(work[0])
    expected += [i for i in queue if i not in old]
    if queue != expected:
        raise ValueError('Queue order: keep the earlier order, move a Continuing item to the tail, and append '
                         'new items at the end')
    should_drain = len(queue) > FLOOR if draining_before else len(queue) >= CAP
    if draining != should_drain:
        raise ValueError(f'The queue has {len(queue)} items: data-draining="true" must be '
                         + ('set' if should_drain else 'removed') + f' (on at {CAP} items, off at {FLOOR})')


def head_lines(body, count=HEAD_READ):
    found = parse(body)
    if found is None:
        return []
    draining, queue = found
    section = SECTION_RE.search(body).group(2)
    texts = {(k, i): re.sub(r'<[^>]+>', '', t).strip() for k, i, t in ITEM_RE.findall(section)}
    state = f'draining (backpressure from {CAP} until {FLOOR})' if draining or len(queue) >= CAP else 'not draining'
    out = [f'{len(queue)} items, {state}; restoration shows the first {min(count, len(queue))}.']
    out += [f'{n}. {texts[item]}' for n, item in enumerate(queue[:count], 1)]
    return out


def done(body, outcome):
    """The notebook with the head item removed (Closed, Developed) or moved to the tail (Continuing), and the
    draining flag recomputed from the previous state."""
    found = SECTION_RE.search(body)
    if found is None:
        raise ValueError('No lead and bridge queue')
    draining, queue = parse(body)
    if not queue:
        raise ValueError('The queue is empty')
    lines = re.findall(r'<li data-(?:lead|bridge)="[^"]+"[^>]*>.*?</li>', found.group(2), re.S)
    head = lines.pop(0)
    if outcome == 'Continuing':
        lines.append(head)
    elif outcome not in ('Closed', 'Developed'):
        raise ValueError('Outcome is Closed, Developed or Continuing')
    was = draining or len(queue) >= CAP
    flag = (len(lines) > FLOOR) if was else (len(lines) >= CAP)
    inner = re.sub(r'<ol>.*</ol>', lambda m: '<ol>\n' + '\n'.join(lines) + '\n</ol>', found.group(2), flags=re.S)
    section = '<section id="lead-queue"' + (' data-draining="true"' if flag else '') + '>' + inner + '</section>'
    return body[:found.start()] + section + body[found.end():]


def main(argv):
    if len(argv) == 4 and argv[1] == 'done':
        path = Path(argv[2])
        path.write_text(done(path.read_text(), argv[3]))
        print('\n'.join(head_lines(path.read_text(), 1)))
        return 0
    if len(argv) != 3 or argv[1] not in ('init', 'head'):
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
    items = open_items(body)
    record = body.find('<section id="research-record">')
    if record < 0:
        print('The notebook has no Research record', file=sys.stderr)
        return 1
    path.write_text(body[:record] + render(body, items, len(items) >= CAP) + body[record:])
    print(f'Added the queue with {len(items)} items')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
