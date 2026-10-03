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
- An entry reopens an item closed too early with a follow-up list item <li data-lead="ANCHOR:N"> ending
  <strong>Follow-up.</strong> Reopened: <reason>; `append` puts it at the tail.
- Backpressure: at CAP items the section carries data-draining="true"; then every research entry develops
  the head until the queue is down to FLOOR items, when the flag is removed.

Usage: lead_queue.py init NOTEBOOK.html  (adds the section, oldest items first, if it is absent)
       lead_queue.py head NOTEBOOK.html  (the first HEAD_READ items, as restoration prints them)
       lead_queue.py done NOTEBOOK.html Closed|Developed|Continuing  (after developing the head)
       lead_queue.py triage NOTEBOOK.html  (after appending an entry with a Queue triage batch)
       lead_queue.py append NOTEBOOK.html  (after the last entry: its newly passed review items and the items
                                            it marks Reopened go to the tail)"""
import html
import re
import sys
from pathlib import Path

CAP, FLOOR, HEAD_READ = 50, 20, 5
SPELL = 4   # consecutive research entries a Continuing head keeps the head (user, 3 October 2026)
# A research entry may settle the first TRIAGE_MAX queue items at once (user, 3 October 2026), each with the care
# it would get alone: its own block of at least TRIAGE_WORDS words citing its evidence, outcome Closed or Developed
# only; an item still bearing on an open statement is not batched but gets its own spell.
TRIAGE_MAX, TRIAGE_WORDS = 4, 80
TRIAGE_RE = re.compile(r'<h4>Queue triage</h4>\s*<ul>(.*?)</ul>', re.S)
EVIDENCE_RE = re.compile(r'\b(?:lem|thm|prop|cor|conj|check|ex|def|obs):[A-Za-z0-9.-]+|href="#[^"]+"')
SECTION_RE = re.compile(r'<section id="lead-queue"([^>]*)>(.*?)</section>', re.S)
LEADS_RE = re.compile(r'<h4>Outside leads</h4>\s*<ul>(.*?)</ul>', re.S)
BRIDGES_RE = re.compile(r'<h4>Absurd bridges</h4>\s*<ul>(.*?)</ul>', re.S)
TEST_PASSED = re.compile(r'<strong>Test\.</strong>\s*Passed\b')
OUTCOME_RE = re.compile(r'<strong>Follow-up\.</strong>\s*(Developed|Continuing|Closed|Reopened)\b')


class Kind:
    """A kind of queue item: its name, as in data-NAME="ID" on the queue's items, developing entries and
    follow-up lists, and the entry heading that lists its items (`listed`, a pattern whose group 1 is the list)."""

    def __init__(self, name, listed):
        self.name, self.listed = name, listed


KINDS = {'lead': Kind('lead', LEADS_RE), 'bridge': Kind('bridge', BRIDGES_RE)}
NAMES = '|'.join(KINDS)
ITEM_RE = re.compile(r'<li data-(' + NAMES + r')="([^"]+)"[^>]*>(.*?)</li>', re.S)
LINE_RE = re.compile(r'<li data-(?:' + NAMES + r')="[^"]+"[^>]*>.*?</li>', re.S)
FOLLOWUP_ITEM = re.compile(r'<li\b[^>]*data-(' + NAMES + r')="([^"]+)"[^>]*>(.*?)</li>', re.S)
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
    """((kind, id), outcome) for a research entry developing a queue item, or None.  The outcome is the entry's
    own: the last Follow-up outside listed items, so a quoted earlier Follow-up does not count."""
    if 'data-kind="research"' not in tag:
        return None
    found = re.findall(r'\bdata-(' + NAMES + r')="([^"]+)"', tag)
    if not found:
        return None
    if len(found) > 1:
        raise ValueError('A research entry develops at most one queue item: its tag names '
                         + ', '.join(i for _, i in found))
    outcomes = OUTCOME_RE.findall(FOLLOWUP_ITEM.sub('', text[len(tag):]))
    return found[0], outcomes[-1] if outcomes else None


def spell(body, item, pending=False):
    """Research entries, from the record's end, that developed `item` since it became the head: entries that
    develop no queue item (reviews, other research) neither count nor break the run, which ends at an entry
    developing another item or settling a triage batch.  With pending=True the entry about to be appended counts
    too, unless it is already the last article (its <!-- TIMING TURN --> marker is still unfilled)."""
    count, last = 0, True
    for tag, text in reversed(record_articles(body)):
        if 'data-kind="research"' not in tag:
            continue
        if pending and last and '<!-- TIMING ' in text:
            pending = False
        last = False
        work = developed_by(tag, text)
        if triaged(tag, text) or (work and work[0] != item):
            break
        if work:
            count += 1
    return count + (1 if pending else 0)


def review_passed(tag, text):
    """Passed items of one review or research article, as (kind, id): leads then bridges.  Research entries may
    carry their own Outside leads and Absurd bridges (user, 3 October 2026: work on a lead can generate new ones)."""
    ident = re.search(r'\bid="([^"]+)"', tag)
    if not re.search(r'data-kind="(?:review|research|audit)"', tag) or not ident:
        return []
    audit = 'data-kind="audit"' in tag   # every item an audit lists is queued: "when unsure, queue it"
    out = []
    for kind in KINDS.values():
        section = kind.listed.search(text)
        if section:
            for n, item in enumerate(re.findall(r'<li\b(.*?)</li>', section.group(1), re.S), 1):
                if audit or TEST_PASSED.search(item):
                    out.append((kind.name, f'{ident.group(1)}:{n}'))
    return out


def triaged(tag, text):
    """[((kind, id), outcome, words, has_evidence)] of a research entry's Queue triage list, in order."""
    if 'data-kind="research"' not in tag:
        return []
    section = TRIAGE_RE.search(text)
    if not section:
        return []
    out = []
    for kind, item_id, item in FOLLOWUP_ITEM.findall(section.group(1)):
        outcome = OUTCOME_RE.search(item)
        words = len(re.sub(r'<[^>]+>', ' ', item).split())
        out.append(((kind, item_id), outcome.group(1) if outcome else None, words, bool(EVIDENCE_RE.search(item))))
    return out


def check_triage(batch, old):
    """The rigor rules of a Queue triage batch against the queue `old` before the entry."""
    if len(batch) > TRIAGE_MAX:
        raise ValueError(f'A Queue triage batch settles at most {TRIAGE_MAX} items, each with full care')
    items = [b[0] for b in batch]
    if items != old[:len(items)]:
        raise ValueError('A Queue triage batch takes the first items of the queue, in order: expected '
                         + ', '.join(i for _, i in old[:len(items)]))
    for (kind, ident), outcome, words, evidence in batch:
        if outcome not in ('Closed', 'Developed'):
            raise ValueError(f'Triage item {ident}: a batch only closes or develops ("<strong>Follow-up.</strong> '
                             'Closed: ..." or "Developed ..."); an item still bearing on an open statement gets its '
                             'own spell, so end the batch before it')
        if words < TRIAGE_WORDS:
            raise ValueError(f'Triage item {ident}: {words} words; each batched item gets the care it would get '
                             f'alone, at least {TRIAGE_WORDS} words of what was checked and why (user, 3 October 2026)')
        if not evidence:
            raise ValueError(f'Triage item {ident}: cite the evidence for the outcome (a claim ID or an entry '
                             'anchor link)')


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


def reopened_by(text):
    """Items an entry reopens: follow-up list items whose outcome is Reopened."""
    return [(kind, item_id) for kind, item_id, item in FOLLOWUP_ITEM.findall(text)
            if (OUTCOME_RE.search(item) or [None, None])[1] == 'Reopened']


def open_items(body):
    """The queue's initial contents: passed items, in record order, that no follow-up list item has Closed
    (and not Reopened since).  Once a queue exists, its changes are checked as transitions from HEAD (check),
    not recomputed from the history, whose older entries used Developed and Continuing for progress."""
    passed, closed, place = [], {}, {}
    articles = record_articles(body)
    for position, (tag, text) in enumerate(articles):
        ident = re.search(r'\bid="([^"]+)"', tag)
        place[ident.group(1) if ident else None] = position
        for item in review_passed(tag, text):
            source = audit_source(text, item) if 'data-kind="audit"' in tag else None
            passed.append((place.get(source, position), item))
        for kind, item_id, item in FOLLOWUP_ITEM.findall(text):
            outcome = OUTCOME_RE.search(item)
            if outcome and outcome.group(1) in ('Closed', 'Reopened'):
                closed[(kind, item_id)] = outcome.group(1) == 'Closed'
    # stable: an audit's items take their source review's place in record order
    return [p for _, p in sorted(passed, key=lambda pair: pair[0]) if not closed.get(p)]


def audit_source(text, item):
    """The data-source anchor of an audit's listed item (kind, 'ANCHOR:N'), or None."""
    section = KINDS[item[0]].listed.search(text)
    tags = re.findall(r'<li\b([^>]*)>', section.group(1)) if section else []
    n = int(item[1].rsplit(':', 1)[1])
    found = re.search(r'data-source="([^"]+)"', tags[n - 1]) if n <= len(tags) else None
    return found.group(1) if found else None


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
    section = KINDS[kind].listed.search(art.group(0))
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
    articles = record_articles(body)
    tag, text = articles[-1] if articles else ('', '')
    work = developed_by(tag, text)
    batch = triaged(tag, text)
    if work and batch:
        raise ValueError('An entry either develops the head (data-lead or data-bridge) or settles a Queue triage '
                         'batch, not both')
    if work and work[1] not in ('Closed', 'Developed', 'Continuing'):
        raise ValueError('An entry developing a queue item states "<strong>Follow-up.</strong> Closed: <reason>", '
                         '"Developed ..." or "Continuing ..."')
    before = parse(head_body) if head_body else None
    if head_body is not None and len(articles) - len(record_articles(head_body)) > 1:
        raise ValueError('Commit one Research-record entry at a time: each entry\'s queue change is checked '
                         'against the commit before it')
    if before is None:
        if work or batch:
            raise ValueError('The commit that creates the queue may not develop queue items: run lead_queue.py init, '
                             'commit the section, then develop its head')
        wanted = open_items(body)
        missing = [i for k, i in wanted if (k, i) not in queue]
        stale = [i for k, i in queue if (k, i) not in wanted]
        if missing or stale:
            raise ValueError('A new queue holds exactly the passed items not closed: missing '
                             + (', '.join(missing) or 'none') + '; not open ' + (', '.join(stale) or 'none'))
        if len(queue) >= CAP and not draining:
            raise ValueError(f'The queue has {len(queue)} items, at least {CAP}: mark the section '
                             'data-draining="true"')
        return
    every = {item for t, x in articles for item in review_passed(t, x)}
    arrivals = review_passed(tag, text) + reopened_by(text)
    unknown = [i for k, i in arrivals if (k, i) not in every]
    if unknown:
        raise ValueError('Reopened items must be passed review items: ' + ', '.join(unknown))
    was_draining, old = before
    if batch:
        check_triage(batch, old)
    closed, developed = listed_closures(tag, text)
    listed_developed = [i for k, i in developed if (k, i) in old]
    if listed_developed:
        raise ValueError('A follow-up list may mark a queued item Closed (it leaves the queue), Continuing or '
                         'Reopened; Developed is said by a research entry developing it: ' + ', '.join(listed_developed))
    head = old[0] if old else None
    if work and work[0] != head:
        raise ValueError(f'Queue items are developed oldest first: this entry develops {work[0][1]}, but the head '
                         f'is {head[1] if head else "empty"}')
    draining_before = was_draining or len(old) >= CAP
    if draining_before and 'data-kind="research"' in tag and not work and not batch:
        raise ValueError(f'The queue is draining ({len(old)} items; backpressure from {CAP} until {FLOOR}): this '
                         f'research entry must develop the head, {head[1]}, tagged data-{head[0]}="{head[1]}"')
    expected = [i for i in old if (not work or i != work[0]) and i not in closed][len(batch):]
    if work and work[1] == 'Continuing':
        if spell(body, work[0]) < SPELL:
            expected.insert(0, work[0])      # keeps the head for up to SPELL consecutive entries
        else:
            expected.append(work[0])
    new = list(dict.fromkeys(i for i in arrivals if i not in expected))
    if queue[:len(expected)] != expected or sorted(queue[len(expected):]) != sorted(set(new)):
        raise ValueError('Queue update: keep the earlier items in order; remove the developed head if Closed or '
                         'Developed; if Continuing, keep it at the head until its ' + str(SPELL) + 'th consecutive entry, '
                         'then move it to the tail; append at the end exactly this entry\'s '
                         'newly passed review items and the items it marks Reopened ('
                         + (', '.join(i for _, i in new) or 'none') + ')')
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
    """The notebook with the head item removed (Closed, Developed), kept at the head (Continuing, before its
    SPELLth consecutive entry) or moved to the tail (Continuing, at it), and the draining flag recomputed from
    the previous state.  Run it before or after appending the developing entry; spell() tells which."""
    found = SECTION_RE.search(body)
    if found is None:
        raise ValueError('No lead and bridge queue')
    draining, queue = parse(body)
    if not queue:
        raise ValueError('The queue is empty')
    lines = LINE_RE.findall(found.group(2))
    head = lines.pop(0)
    if outcome == 'Continuing':
        if spell(body, queue[0], pending=True) < SPELL:
            lines.insert(0, head)
        else:
            lines.append(head)
    elif outcome not in ('Closed', 'Developed'):
        raise ValueError('Outcome is Closed, Developed or Continuing')
    was = draining or len(queue) >= CAP
    flag = (len(lines) > FLOOR) if was else (len(lines) >= CAP)
    inner = re.sub(r'<ol>.*</ol>', lambda m: '<ol>\n' + '\n'.join(lines) + '\n</ol>', found.group(2), flags=re.S)
    section = '<section id="lead-queue"' + (' data-draining="true"' if flag else '') + '>' + inner + '</section>'
    return body[:found.start()] + section + body[found.end():]


def settle_triage(body):
    """The notebook with the last entry's Queue triage items removed from the queue's head."""
    found = SECTION_RE.search(body)
    if found is None:
        raise ValueError('No lead and bridge queue')
    draining, queue = parse(body)
    articles = record_articles(body)
    tag, text = articles[-1] if articles else ('', '')
    batch = triaged(tag, text)
    if not batch:
        raise ValueError('The last entry has no Queue triage list')
    check_triage(batch, queue)
    lines = LINE_RE.findall(found.group(2))[len(batch):]
    was = draining or len(queue) >= CAP
    flag = (len(lines) > FLOOR) if was else (len(lines) >= CAP)
    inner = re.sub(r'<ol>.*</ol>', lambda m: '<ol>\n' + '\n'.join(lines) + '\n</ol>', found.group(2), flags=re.S)
    section = '<section id="lead-queue"' + (' data-draining="true"' if flag else '') + '>' + inner + '</section>'
    return body[:found.start()] + section + body[found.end():], len(batch)


def append_new(body):
    """The notebook with the last entry's newly passed review items and its Reopened items appended at the
    queue's tail, and the draining flag set if the queue reaches CAP."""
    found = SECTION_RE.search(body)
    if found is None:
        raise ValueError('No lead and bridge queue')
    draining, queue = parse(body)
    articles = record_articles(body)
    tag, text = articles[-1] if articles else ('', '')
    new = list(dict.fromkeys(i for i in review_passed(tag, text) + reopened_by(text) if i not in queue))
    lines = LINE_RE.findall(found.group(2))
    lines += [f'<li data-{kind}="{ident}"><a href="#{ident.rsplit(":", 1)[0]}">{ident}</a> ({kind}): '
              f'{item_text(body, kind, ident)}</li>' for kind, ident in new]
    flag = draining or len(lines) >= CAP
    inner = re.sub(r'<ol>.*</ol>', lambda m: '<ol>\n' + '\n'.join(lines) + '\n</ol>', found.group(2), flags=re.S)
    section = '<section id="lead-queue"' + (' data-draining="true"' if flag else '') + '>' + inner + '</section>'
    return body[:found.start()] + section + body[found.end():], len(new)


def main(argv):
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
