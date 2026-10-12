#!/usr/bin/env python3
"""Append a drafted research-record entry and optionally replace the Proposed next step.

The entry file holds one <article> element. It is inserted after the last article of the
selected notebook's research record. With --next FILE, the body of the proposed-next-step
section is replaced by the file's HTML (the section heading is kept). Fails closed if the entry's
anchor already exists, the record or section is missing, or the entry fails the existing
route/review reporting checks. Claim evidence remains a finalization check after registration.

It also refuses, before anything is written:
- an entry or a next step with a dollar sign, which MathJax reads as a math delimiter, or with an HTML
  character reference that lost its ampersand (tools/char_refs.py);
- a next step that parks the goal (a wait for a date, a feed or the user) while the notebook's Open
  statements section still lists a statement; an entry of a kind the branch's own module names
  (tools/branch_extension.py) is not checked;
- an entry while the notebook's Where we stand is the same as in the last commit, since every cycle
  reviews that section. --stand-unchanged REASON lets it through, and the entry then holds the reason
  in a paragraph labelled Where we stand, which tools/stand_reasons.py counts;
- a next step that names no queued item, by identifier or by a link to an entry that developed one, while
  the notebook's queue is draining. For each item a next step names it prints the item's queued text and
  its latest follow-up, to write the description against;
- a next step that names a queued item by its identifier, when the item has a latest follow-up, without
  quoting eight consecutive words of that follow-up or of the item's queued text.
After these, a branch's own tools/append_checks.py, where it has one, is asked: its
check(source, entry, next_html) raises ValueError to refuse.
"""
# Copyright (c) 2026 Kamil Braun. SPDX-License-Identifier: MIT

import argparse
import functools
import html
import importlib.util
from pathlib import Path
import re
import subprocess
import sys
import branch_extension
from char_refs import broken_entities
from notebooks import selected, ROOT

HEADING = '<h2>Proposed next step</h2>'
# While the goal is open the next step is always research (AGENTS.md): wording that parks it on a
# date, a feed or the user's approval is refused. A step may name other work that waits, as long as
# it is not itself a wait.
PARKING = re.compile(r'\b(cycles?|the spin|the goal|research|work)\s+(waits?|pauses?|stops?)\b'
                     r'|\bwaits?\s+(on|for)\s+your\s+(approvals?|answers?|decisions?)\b'
                     r'|\b(pause|park)(s|d|ed|ing)?\s+(the\s+)?(goal|spin|loop|research|cycles?)\b', re.I)
STAND_LABEL = '<p><strong>Where we stand.</strong> Unchanged: '


def section(source, name):
    """The section `name` of the notebook, or None when it has none."""
    start = source.find(f'<section id="{name}"')
    return None if start < 0 else source[start:source.index('</section>', start)]


def goal_open(source):
    """Whether the notebook still lists a statement needed for its goal: an Open statements section
    with a list item. A notebook without the section, such as one that records tasks, has no goal
    this tool can read as open."""
    return '<li' in (section(source, 'open-statements') or '')


def refuse_broken_text(what, text):
    if '$' in text:
        # The finisher refuses this too, but only after the entry is in the notebook.
        raise ValueError(f'{what} contains a dollar sign, which MathJax reads as a math delimiter; write '
                         'mathematics with \\( \\) and currency as "USD 5"')
    broken = broken_entities(text)
    if broken:
        raise ValueError(f'{what} has character references without their & ({", ".join(sorted(set(broken)))}), '
                         'the mark of a sed replacement; edit notebook text with an exact replacement')


def with_stand_reason(source, entry, committed, reason):
    """`entry`, checked against the rule that every cycle reviews Where we stand: refused while the
    section is as `committed` has it and no reason is given; with a reason, the entry gains the
    paragraph that records it. A changed section, a notebook without one or one not yet committed
    leaves the entry as it is."""
    stand = section(source, 'where-we-stand')
    if committed is None or stand is None or stand != section(committed, 'where-we-stand'):
        return entry
    if not reason or not reason.strip():
        raise ValueError('Where we stand is unchanged since the last commit. Update it for this cycle '
                         '(AGENTS.md: after every research turn), or pass --stand-unchanged REASON '
                         'saying why nothing in it changed')
    paragraph = f'{STAND_LABEL}{html.escape(reason.strip(), quote=False)}</p>'
    meta = re.search(r'<p class="entry-meta">.*?</p>', entry, re.S)
    at = meta.end() if meta else entry.rindex('</article>')
    return entry[:at] + '\n' + paragraph + ('\n' if not meta else '') + entry[at:]


def named_items(source, next_html):
    """The queued items a next step names, by identifier or by a link to an entry that developed one, each as
    (identifier, queued text, anchor of its latest development, that entry's Follow-up); None when the notebook
    has no queue.

    A next step of 11 October 2026 described a queued check as asking another question than its text asks, and
    the cycle went to a form the item's own closure had judged not to bear: the item's words and its latest
    follow-up are shown beside the next step, and a next step that takes a queue item says which."""
    import lead_queue
    found = lead_queue.parse_tree(source)
    if found is None:
        return None
    nodes = found[1] + [child for node in found[1] for child in node.children]
    # Keyed by kind and identifier: a lead and a bridge of one review share REVIEW:1, and keyed by identifier
    # alone the bridge's text was printed with the lead's entries (11 October 2026).
    queued = {(node.kind, node.ident): node for node in nodes}
    linked = set(re.findall(r'href="#([^"]+)"', next_html))
    named = []
    for kind, ident in queued:
        if not mentioned(ident, next_html):
            continue
        shared = [k for k, i in queued if i == ident]
        # among items sharing the identifier, the one whose kind is the word before it; all when none is said
        said = [k for k in shared if re.search(r'\b' + k + r'[\s:]+' + re.escape(ident) + r'(?![\w:-])', next_html)]
        if len(shared) == 1 or not said or kind in said:
            named.append((kind, ident))
    developments = {}
    for tag, text in lead_queue.record_articles(source):
        anchor = re.search(r'\bid="([^"]+)"', tag)
        item = re.search(r'\bdata-(' + lead_queue.NAMES + r')="([^"]+)"', tag)
        if anchor and item and item.groups() in queued:
            follow = re.findall(r'<p><strong>Follow-up\.</strong>(.*?)</p>', text, re.S)
            developments[item.groups()] = (anchor.group(1), plain(follow[-1]) if follow else '')
            if anchor.group(1) in linked and item.groups() not in named:
                named.append(item.groups())
    return [(Named(i, k, sum(1 for _, other in queued if other == i) > 1), plain(queued[k, i].text),
             *developments.get((k, i), ('', ''))) for k, i in named]


def mentioned(ident, text):
    """Whether `text` names the queue identifier, bare or as KIND:IDENTIFIER, and not as part of a longer one."""
    import lead_queue
    return re.search(r'(?<![\w:#-])(?:(?:' + lead_queue.NAMES + r'):)?' + re.escape(ident) + r'(?![\w:-])', text)


class Named(str):
    """A queued item's identifier that remembers its kind, for identifiers two kinds share."""

    def __new__(cls, ident, kind=None, shared=False):
        named = super().__new__(cls, ident)
        named.kind = kind
        named.full = f'{kind}:{ident}' if kind else str(ident)     # what the queue tool's lookups take
        named.label = named.full if shared else str(ident)         # what a message prints: the kind where needed
        return named


def item_history(source, ident):
    """Every record entry that developed the queued item `ident`, oldest first, as (anchor, title).

    A review of 11 October 2026 gave its decisive test to a queued item after reading that item's latest
    entry only; an earlier entry on the same item already answered the test.  The whole list is printed
    beside the next step, so that the entries to read are named."""
    import lead_queue
    history = []
    kinds = getattr(ident, 'kind', None) or lead_queue.NAMES      # one kind when the identifier carries it
    for tag, text in lead_queue.record_articles(source):
        anchor = re.search(r'\bid="([^"]+)"', tag)
        item = re.search(r'\bdata-(?:' + kinds + r')="([^"]+)"', tag)
        # also entries filed under another item that give this one an outcome in a follow-up list item: an item
        # of 11 October had been closed and reopened so, as a sub-idea of its former parent, and the list of
        # entries filed under its own identifier showed neither
        listed = re.search(r'<li data-(?:' + kinds + r')="' + re.escape(ident) + r'"', text)
        if anchor and ((item and item.group(1) == ident) or listed):
            title = re.search(r'<h3>(.*?)</h3>', text, re.S)
            history.append((anchor.group(1), plain(title.group(1)) if title else ''))
    return history


QUOTED_WORDS = 8    # consecutive words of an item's follow-up or text that a next step naming it must quote


def words(text):
    return [w for w in (re.sub(r'^\W+|\W+$', '', token).lower() for token in plain(text).split()) if w]


def quotes(step, source, length=QUOTED_WORDS):
    """Whether `step` contains `length` consecutive words of `source`."""
    have, given = words(step), words(source)
    runs = {tuple(given[i:i + length]) for i in range(len(given) - length + 1)}
    return any(tuple(have[i:i + length]) in runs for i in range(len(have) - length + 1))


def require_quoted_items(source, next_html):
    """A next step that names a queued item by its identifier, when the item has a latest follow-up, quotes
    it or the item's text.

    Printing the item's words (above) showed, on 11 October 2026, a next step whose reason did not match its
    item, and the step was committed with the mismatch.  A quotation of eight consecutive words is a mechanical
    proxy: the description is then written from the item's words.  An item named only through a link to an
    entry is not held to this, a link often pointing at the item being left."""
    for ident, text, anchor, follow in named_items(source, next_html) or []:
        by_name = mentioned(ident, next_html)
        if by_name and follow and not (quotes(next_html, follow) or quotes(next_html, text)):
            raise ValueError(f'the next step names queue item {ident.label} and quotes neither its latest follow-up '
                             f'(#{anchor}) nor its queued text: quote at least {QUOTED_WORDS} consecutive words '
                             'of one of them, so that what the item asks is written from its own words '
                             f'(tools/lead_queue.py history NOTEBOOK {ident.label} --status)')


REVIEW_AFTER = 6    # research entries on a route, then its review (AGENTS.md)


def review_due(articles):
    """Whether the last entry's route has had its six research entries since its last review."""
    route = re.search(r'\bdata-route="([^"]+)"', articles[-1][0]) if articles else None
    if not route:
        return False
    run = 0
    for tag, _ in reversed(articles):
        if f'data-route="{route.group(1)}"' not in tag:
            continue
        if 'data-kind="research"' not in tag:
            break
        run += 1
    return run >= REVIEW_AFTER


def plain(fragment):
    return ' '.join(html.unescape(re.sub(r'<[^>]+>', ' ', fragment)).split())


def require_named_item(source, next_html):
    """While the queue drains every research entry develops a queued item, so its next step names one."""
    import lead_queue
    items = named_items(source, next_html)
    if items is None or items or not lead_queue.is_draining(source) or not goal_open(source):
        return
    if review_due(lead_queue.record_articles(source)):
        return      # the next entry is the route review, which develops no item
    raise ValueError('the queue is draining, so the next entry develops a queued item, and this next step names '
                     'none: give the item\'s identifier, or link an entry that developed it, and describe what '
                     'it asks from its queued text (tools/lead_queue.py history NOTEBOOK ID --status)')


def registry_matches(text, limit=3, data=None, home=None):
    """The registered claims nearest to a queued item's text, as (identifier, start of summary), best first;
    an empty list where the registry cannot be read.

    On 11 October 2026 a reading named on a queue item was deferred in two entries while its statement had
    been registered for a day: the item's words were never put to the registry.  The matches are printed
    beside the item when a next step names it; they are not logged as a search of the author's.

    With `home`, a part of a record address that marks the notebook's own claims, those come first, each
    group in its order of score: across two blocks of entries the three matches printed were mostly claims
    of other notebooks, which share common words and say nothing of the item."""
    spec = importlib.util.spec_from_file_location('search_claims', Path(__file__).parent / 'search-claims.py')
    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
        if data is None:
            data = module.read_json(module.REGISTRY)
        found = module.search(data, [plain(text)])
    except (OSError, ValueError, KeyError):
        return []
    if home:
        found = sorted(found, key=lambda pair: home not in str(pair[1].get('record', '')))   # stable
    return [(claim['id'], ' '.join(claim['summary'].split())[:140]) for _score, claim in found[:limit]]


def older_claim_lines(source, ident, claims=None):
    """Lines for the claims of entries older than a queued item that are nearest to its text, marked as earlier;
    the registry matches above them are of any date and do not say which."""
    import lead_queue
    found = lead_queue.claims_elsewhere(source, lead_queue.registered_claims() if claims is None else claims,
                                        getattr(ident, 'full', ident), 3, earlier=True)
    return [f'  Claim of an entry up to the one that queued it, nearest to its text [earlier]: {claim} in #{anchor}'
            for _score, claim, anchor in found]


def home_of(source):
    """The part of a record address that marks a side notebook's claims, or None for the main notebook."""
    found = re.search(r'branches/[^/]+/', str(source))
    return found.group(0) if found else None


def refuse_excluded_item(source, next_html):
    """A next step may not take only the item that the finisher will refuse for the next entry.

    After two research entries in a row on one queue item that declare no bearing, the finisher sends the next
    entry to a different item.  On 11 October 2026 two next steps named such an item; the first was noticed
    on opening the cycle and the second only when the finished entry was refused."""
    items = named_items(source, next_html)
    if not items:
        return
    tags = [t for t in re.findall(r'<article\b[^>]*>', source) if 'data-kind="research"' in t]
    if not tags:
        return
    route = re.search(r'data-route="([^"]+)"', tags[-1])
    last = [t for t in tags if route and f'data-route="{route.group(1)}"' in t][-2:]
    taken = [re.search(r'data-(check|lead|bridge|idea|build)="([^"]+)"', t) for t in last]
    if len(last) < 2 or not all(taken) or taken[0].groups() != taken[1].groups():
        return
    if not all('data-bearing="none"' in t for t in last):
        return
    # by kind and identifier: a bridge sharing the excluded lead's identifier is a different item
    excluded, named = taken[0].group(2), {ident.full for ident, *_ in items}
    if named == {':'.join(taken[0].groups())}:
        raise ValueError(f'the next step takes {excluded}, whose last two entries declared no bearing: the '
                         'finisher will refuse a third in a row, so name the different item the next entry '
                         'develops (AGENTS.md, goal progress)')
    if ':'.join(taken[0].groups()) in named:
        print(f'Note: {excluded} had two entries in a row without bearing; the next entry must develop '
              'another of the items this step names.', file=sys.stderr)


# What the plan must say of the entry it plans; "does not close" and "the other check is closed" do not match.
PLAN_CLOSES = re.compile(r'\b(?:the |this )?entry (?:then )?(?:closes|will close) (?:its|the|that|this) '
                         r'(?:queue |queued )?(?:item|check|lead|build)\b', re.I)
PLAN_BEST = re.compile(r'\bBest outcome\b(.*)', re.I | re.S)


def refuse_no_bearing_plan(source, next_html):
    """A next step may not plan, in a run of entries without bearing, an entry the finisher will refuse.

    After three research entries in a row on the route that declare no bearing, the finisher refuses an entry
    whose Best outcome says it gives nothing at the goal's parameters unless its follow-up closes its item.  On
    12 October 2026 a next step stated exactly that best outcome, was accepted, and the cycle made by it was
    refused at its end, when its reviewer had ruled the item open.  The run's length and the words for nothing
    are the finisher's own; like the finisher it reads only what follows "Best outcome", so a sentence about
    past work is not taken for the plan, and a next step that states no best outcome is not refused here.  A
    next step for the route review that is due is not a plan of a research entry."""
    import lead_queue
    if review_due(lead_queue.record_articles(source)):
        return
    checks = reporting_checks()
    tags = [t for t in re.findall(r'<article\b[^>]*>', source) if 'data-kind="research"' in t]
    if not tags:
        return
    route = re.search(r'data-route="([^"]+)"', tags[-1])
    run = 0
    for tag in reversed([t for t in tags if route and f'data-route="{route.group(1)}"' in t]):
        if 'data-bearing="none"' not in tag:
            break
        run += 1
    step = plain(next_html)
    best = PLAN_BEST.search(step)
    text = best.group(1) if best else ''                 # the closing may be said anywhere in the step
    if run >= checks.NO_BEARING_RUN and checks.NOTHING_BEST_RE.search(text) and not PLAN_CLOSES.search(step):
        raise ValueError(f'the last {run} research entries on the route declared no bearing, and this next step '
                         "says its best outcome is nothing at the goal's parameters without saying that the entry "
                         'closes its item: the finisher will refuse the entry it plans; plan an attempt whose '
                         'best outcome bears on the goal, or one that closes its item and says so (AGENTS.md, '
                         'goal progress)')


def branch_checks(tools=None):
    """The branch's own check(source, entry, next_html), or None where it has no tools/append_checks.py."""
    path = (tools or Path(__file__).parent) / 'append_checks.py'
    if not path.is_file():
        return None
    spec = importlib.util.spec_from_file_location('append_checks', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.check


@functools.cache
def reporting_checks():
    """Reuse the finalizer's rules, without running its checkpoint operations."""
    spec = importlib.util.spec_from_file_location('append_reporting',
                                                Path(__file__).with_name('finish-turn.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def preflight(source, ident):
    if 'data-route-item="' not in source:
        return
    article = re.search(r'<article\b[^>]*\sid="' + re.escape(ident) + '"', source).start()
    close = source.index('</article>', article)
    checks = reporting_checks()
    checks.validate_route(source, article)
    checks.validate_convergence(source, article, close)
    checks.validate_progress(source, article, close, check_registered_claims=False)


def append(source, entry, next_html=None, committed=None, reason=None, tools=None):
    """The notebook `source` with `entry` appended and, with `next_html`, its next step replaced.
    `committed` is the notebook as of the last commit, for the Where we stand rule, and `reason`
    what --stand-unchanged gave."""
    entry = entry.strip()
    m = re.match(r'<article\b[^>]*?\sid="([^"]+)"', entry)
    if not m or not entry.endswith('</article>'):
        raise ValueError('entry must be one <article id="..."> ... </article> element')
    refuse_broken_text('entry', entry)
    if next_html is not None:
        refuse_broken_text('next step', next_html)
        parked = PARKING.search(re.sub(r'<[^>]+>', ' ', next_html))
        # A branch's own module may name kinds of entry whose next step may wait.
        may_wait = '|'.join(map(re.escape, branch_extension.ask('PARKING_KINDS', (), tools)))
        waiting_kind = may_wait and re.match(rf'<article\b[^>]*\bdata-kind="(?:{may_wait})"', entry)
        if parked and goal_open(source) and not waiting_kind:
            raise ValueError(f'the next step parks the goal ("{parked.group(0)}"); while the goal is open '
                             'the next step is research: open a new line or test a new idea (AGENTS.md)')
    try:        # the finisher's rule, with the next step, which the finisher does not see
        reporting_checks().refuse_unverified_attempt(entry, next_html)
    except ValueError as error:
        raise ValueError(str(error)[0].lower() + str(error)[1:]) from None
    entry = with_stand_reason(source, entry, committed, reason)
    own = branch_checks(tools)
    if own:
        own(source, entry, next_html)
    if f'id="{m.group(1)}"' in source:
        raise ValueError(f'anchor already present: {m.group(1)}')
    start = source.find('<section id="research-record">')
    if start < 0:
        raise ValueError('research-record section missing')
    close = source.find('</section>', start)
    last = source.rfind('</article>', start, close)
    at = last + len('</article>') if last >= 0 else close
    source = source[:at] + '\n' + entry + source[at:]
    if next_html is not None:
        a = source.find('<section id="proposed-next-step">')
        if a < 0:
            raise ValueError('proposed-next-step section missing')
        b = source.index('</section>', a)
        body = source[a:b]
        if HEADING not in body:
            raise ValueError('proposed-next-step heading missing')
        head = body[:body.index(HEADING) + len(HEADING)]
        source = source[:a] + head + '\n' + next_html.strip() + '\n' + source[b:]
        require_named_item(source, next_html)
        require_quoted_items(source, next_html)
        refuse_excluded_item(source, next_html)
        refuse_no_bearing_plan(source, next_html)
    preflight(source, m.group(1))
    return source


def committed_version(path):
    """The notebook as of HEAD, or None outside a repository or for a notebook not yet committed."""
    try:
        rel = Path(path).resolve().relative_to(Path(ROOT).resolve())
    except ValueError:
        return None
    shown = subprocess.run(['git', '-C', str(ROOT), 'show', f'HEAD:{rel.as_posix()}'], capture_output=True, text=True)
    return shown.stdout if shown.returncode == 0 else None


def result_files_line(body, ident):
    """The line listing the result files the entries on queue item `ident` link, or '' when there are none or the
    item is not found: what its entries computed, from which a test posed on the item or a control planned for it
    starts."""
    import lead_queue
    try:
        files = lead_queue.result_files(body, getattr(ident, 'full', ident))
    except (ValueError, KeyError):
        return ''
    return f'  Result files its entries link ({len(files)}): ' + ', '.join(files) if files else ''


REVIEW_PERIOD = 6      # the finisher's; a test holds the two equal


def cadence_line(text):
    """One line on the review cadence after the last entry of the record, for a next step to be written against.

    Twice on 11 October 2026 a next step said which coming entry is the sixth since the last route review,
    counted from memory, and was wrong by one; the count is printed where the next step is written."""
    tags = re.findall(r'<article\b[^>]*>', text[text.find('<section id="research-record"'):])
    if not tags:
        return None
    streak = 0
    for tag in reversed(tags):      # as the finisher counts: every research entry back to the last review
        kind = re.search(r'data-kind="([^"]*)"', tag)
        if kind and kind.group(1) == 'review':
            break
        streak += bool(kind and kind.group(1) == 'research')
    left = REVIEW_PERIOD - streak
    return (f'Review cadence: {streak} research entries since the last route review, this one included; '
            + (f'{left} more, then the review.' if left > 0 else 'the next entry is the review.'))


def closing_followups(source, entry, articles=None):
    """[(kind, identifier, the follow-up's text, the item's listed text)] for the follow-up list items of
    `entry` that close a listed item (Closed or Developed, a merge apart), the listed text read whole from
    the article of `source` that listed it, or '' when that article or the item is not found.  `articles`,
    {anchor: article}, spares a search of the whole notebook for each item when many entries are read."""
    import lead_queue
    found = []
    for kind, ident, item in lead_queue.FOLLOWUP_ITEM.findall(entry):
        outcome = lead_queue.OUTCOME_RE.search(item)
        if not outcome or outcome.group(1) not in ('Closed', 'Developed') or ':' not in ident:
            continue
        if re.search(r'Closed:\s*merged into\b', item):
            continue
        anchor = ident.rsplit(':', 1)[0]
        if articles is not None:
            art = articles.get(anchor)
        else:
            hit = re.search(r'<article\b[^>]*\bid="' + re.escape(anchor) + r'"[^>]*>.*?</article>', source, re.S)
            art = hit.group(0) if hit else None
        listed = lead_queue.listed_item(kind, art, ident) if art else None
        found.append((kind, ident, plain(item), plain(listed[1]) if listed else ''))
    return found


def refuse_unquoted_closures(source, entry):
    """Lines to print, the listed text of each item the entry closes beside its follow-up; a closing follow-up
    that quotes no QUOTED_WORDS consecutive words of that text is refused.  On 12 October 2026 two sub-ideas
    were closed by what a result resembled and not by what their texts ask, and a reviewer caught both: the
    quotation puts the item's own words into the closure, where the reviewer and the author read them."""
    lines, bad = [], []
    for kind, ident, follow, text in closing_followups(source, entry):
        lines.append(f'The entry closes {kind}:{ident}. Its listed text, to read beside the follow-up:')
        lines.append(f'  Listed text: {text or "(not found in the notebook)"}')
        lines.append(f'  Follow-up: {follow}')
        if text and not quotes(follow, text, min(QUOTED_WORDS, len(words(text)))):    # a short text, whole
            bad.append(f'{kind}:{ident}, whose text is: {text}')
    if bad:
        raise ValueError(f'A follow-up that closes a listed item quotes {QUOTED_WORDS} consecutive words of the '
                         'item\'s listed text, so that the closure answers what the item asks; none is quoted '
                         'for ' + '; '.join(bad))
    return lines


def closures_count(source):
    """A line for each entry with closing follow-ups (how many, how many quote their item, how many items were
    not found), and the totals."""
    rows, kinds = [], {}
    whole = {m.group(1): m.group(0)
             for m in re.finditer(r'<article\b[^>]*\bid="([^"]+)"[^>]*>.*?</article>', source, re.S)}
    for ident, article in whole.items():
        found = closing_followups(source, article, whole)
        for kind, _, _, _ in found:
            kinds[kind] = kinds.get(kind, 0) + 1
        if found:
            rows.append((ident, len(found),
                         sum(1 for _, _, follow, text in found
                             if text and quotes(follow, text, min(QUOTED_WORDS, len(words(text))))),
                         sum(1 for _, _, _, text in found if not text)))
    lines = [f'{n}\t{quoted}\t{missing}\t{ident}' for ident, n, quoted, missing in rows]
    return '\n'.join(lines + [f'{sum(r[1] for r in rows)} closing follow-ups in {len(rows)} entries; '
                              f'{sum(r[2] for r in rows)} quote {QUOTED_WORDS} consecutive words of their item\'s '
                              f'listed text; {sum(r[3] for r in rows)} name an item whose text was not found '
                              '(columns: closing, quoting, not found). By kind of item: '
                              + (', '.join(f'{n} {kind}' for kind, n in sorted(kinds.items())) or 'none')
                              + f'. The notebook has {len(source.encode())} bytes.'])


def refuse_unanswered(entry, answers):
    """Refuse an entry whose summing-up sentences with a universal, negative or exact word are not each
    answered in the file given by --answers.  In one review period of 12 October 2026 the draft tool printed,
    in five entries of six, sentences that a reviewer then corrected: a printed list that nothing answers is
    passed over.  The answer is a line saying what the sentence rests on; whether it does is for the reviewer,
    who is given the file."""
    import draft_claim_sentences
    rows = draft_claim_sentences.summing_up(entry)
    if not rows:
        return
    if answers is None:
        raise ValueError(f'{len(rows)} summing-up sentences of the entry say no, every, exactly and the like; '
                         'answer each in a file and pass it with --answers FILE '
                         '(tools/draft_claim_sentences.py DRAFT --answers FILE writes the form)')
    left = draft_claim_sentences.unanswered(entry, answers)
    if left:
        raise ValueError(f'{len(left)} of {len(rows)} summing-up sentences are not answered in the --answers '
                         'file (a sentence changed since its answer counts as new):\n'
                         + '\n'.join(f'  {key} [{where}] {sentence[:160]}' for key, where, sentence in left))
    gaps = draft_claim_sentences.qualifier_gaps(entry, answers)
    if gaps:                    # the answer admits a limit that the sentence does not carry
        raise ValueError(draft_claim_sentences.qualifier_gaps_report(gaps))


def main():
    parser = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    parser.add_argument('entry', type=Path, nargs='?')
    parser.add_argument('--closures', action='store_true',
                        help='append nothing: count, over the notebook\'s entries, the follow-ups that close a '
                             'listed item and how many quote its listed text')
    parser.add_argument('--answers', type=Path,
                        help='the file answering the entry\'s summing-up sentences (see refuse_unanswered)')
    parser.add_argument('--next', type=Path, dest='next_file')
    parser.add_argument('--notebook')
    parser.add_argument('--stand-unchanged', metavar='REASON',
                        help='why Where we stand needs no change in this cycle; recorded in the entry')
    args = parser.parse_args()
    path = Path(ROOT) / selected(args.notebook)['source']
    if args.closures:
        print(closures_count(path.read_text()))
        return
    if args.entry is None:
        parser.error('an entry file is required')
    nxt = args.next_file.read_text() if args.next_file else None
    try:
        refuse_unanswered(args.entry.read_text(), args.answers.read_text() if args.answers else None)
        closures = refuse_unquoted_closures(path.read_text(), args.entry.read_text())
        result = append(path.read_text(), args.entry.read_text(), nxt, committed_version(path),
                        args.stand_unchanged)
    except ValueError as err:
        sys.exit(f'notebook-append.py: {err}')
    path.write_text(result)
    print(f'Appended to {path.relative_to(ROOT)}')
    for line in closures:
        print(line)
    if nxt and cadence_line(result):
        print(cadence_line(result))
    for ident, text, anchor, follow in (named_items(result, nxt) or []) if nxt else []:
        print(f'The next step names queue item {ident.label}. Check its description against the item\'s own '
              'words:')
        print(f'  Queued text: {text}')
        for claim, summary in registry_matches(f'{text} {follow or ""}',     # attempts are named in follow-ups
                                               home=home_of(path)):
            print(f'  Registry match for its text and latest follow-up, to read before planning: {claim} — {summary}')
        for line in older_claim_lines(result, ident):
            print(line)
        if anchor:
            print(f'  Latest development, #{anchor}. Follow-up: {follow}')
        earlier = [entry for entry in item_history(result, ident) if entry[0] != anchor]
        if earlier:
            print(f'  {len(earlier)} earlier entries developed it; read each before planning on it:')
            for entry_anchor, title in earlier:
                print(f'    #{entry_anchor}: {title[:140]}')
        line = result_files_line(result, ident)
        if line:
            print(line)


if __name__ == '__main__':
    main()
