#!/usr/bin/env python3
"""Export timing, archive evidence, and fill one notebook timing placeholder."""
import argparse
from datetime import datetime, timezone
import functools
import html
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import time

sys.path.insert(0, str(Path(__file__).resolve().parent))
from claim_registry import load as load_claims, read_json, render as render_claims
from claim_maintenance import check_revision
from notebook_context import check as check_context
from claim_attention import sync as sync_attention, brief as attention_brief
from lead_queue import LEADS_RE, BRIDGES_RE

ROOT = Path(__file__).resolve().parents[1]


def session_name(value):
    if not re.fullmatch(r'[A-Za-z0-9_.-]+', value) or value in ('.', '..'):
        raise argparse.ArgumentTypeError('Use a simple session name, not a path')
    return value


REVIEW_PERIOD = 6    # research entries allowed in a row before a route review is required
STATUS_LIMIT = 300   # characters of status-line text, before the producer credit
KINDS = ('research', 'review', 'formalization', 'audit')


def entry_tags(body, article):
    tag = body[article:body.index('>', article) + 1]
    found = {key: re.search(rf'data-{key}="([^"]*)"', tag) for key in ('kind', 'route')}
    return {key: match.group(1) if match else None for key, match in found.items()}


def validate_route(body, article):
    """Enforce AGENTS.md's periodic route review; active once the notebook declares route items."""
    items = set(re.findall(r'data-route-item="([^"]+)"', body))
    if not items:
        return
    tags = entry_tags(body, article)
    if tags['kind'] not in KINDS:
        raise ValueError('Tag the entry: <article ... data-kind="research|review|formalization|audit" '
                         'data-route="ITEM">, ITEM a data-route-item of The remaining route or side-...')
    if tags['kind'] in ('formalization', 'audit'):   # a queue audit is no research cycle and no route review
        return
    if tags['route'] not in items and not (tags['route'] or '').startswith('side-'):
        raise ValueError(f'data-route must be one of {sorted(items)} or start with side-; '
                         'name the top-level route item, not a sub-gap of the current line')
    record = body.find('<section id="research-record">')
    earlier = [m.start() for m in re.finditer(r'<article\b', body[:article]) if m.start() > record]
    streak, after_review = 0, False
    for position in reversed(earlier):
        kind = entry_tags(body, position)['kind']
        if kind == 'review':
            after_review = True
            break
        if kind != 'research':   # formalization, task or untagged entries neither count nor end the scan
            continue
        streak += 1
    if tags['kind'] == 'review':
        # One route review in seven entries (user, 3 October 2026: "That's too frequent. Drop to one in
        # seven"): a review needs REVIEW_PERIOD research entries since the previous one.
        if after_review and streak < REVIEW_PERIOD:
            raise ValueError(f'Only {streak} research entries since the last route review; a review comes after '
                             f'{REVIEW_PERIOD} (one entry in {REVIEW_PERIOD + 1}, AGENTS.md). Make this a research '
                             'entry and carry the concern to the scheduled review')
        return
    if streak >= REVIEW_PERIOD:
        raise ValueError(f'The last {streak} research entries have no route review. This entry must be '
                         'a route review (data-kind="review"): the general claim of the current line, '
                         'what the main goal needs from it, a falsification attempt, an estimate that '
                         'the line advances the goal, and the next step on the highest-risk route item')


LEADS_MIN, BRIDGES_MIN = 3, 2
# Outside draining, restore three passed leads and two bridges (user, 5 October 2026).
# Only picks enter the queue; if fewer tests pass, keep those rather than inventing successes.
PICKS = {'Outside leads': 3, 'Absurd bridges': 2}
PICK_RE = re.compile(r'^[^>]*\bdata-pick\b')
TEST_RE = re.compile(r'<strong>Test\.</strong>\s*(Passed|Falsified|Not run)\b')
OBSTACLE_RE = re.compile(r'<h4>Obstacle</h4>\s*<p>(.*?)</p>', re.S)
OBSTACLE_MIN = 80


def validate_leads(body, article, close, draining=None):
    """AGENTS.md: a route review reaches outside the record's toolkit (user instructions, 25 September
    2026, after classical tools were proposed only once the user named their fields).  It lists Outside
    leads, from fields that study the open statement's objects, and Absurd bridges, from fields that never
    stood near them.  Each item records the outcome of its cheap test, run in the review cycle (user
    instruction, 25 September 2026): passed, falsified, or not run with the reason. Falsified items stay
    listed and count."""
    if not re.search(r'data-route-item="', body):
        return
    if entry_tags(body, article)['kind'] == 'research':
        # Research entries no longer carry their own Outside leads or Absurd bridges (user, 9 October 2026:
        # "drop the \"at most one lead and at most one bridge\" produced by regular cycle"); only reviews add them.
        for pattern, heading in ((LEADS_RE, 'Outside leads'), (BRIDGES_RE, 'Absurd bridges')):
            if pattern.search(body, article, close) is not None:
                raise ValueError(f'A research entry has no <h4>{heading}</h4> section (user, 9 October 2026): '
                                 'only route reviews propose leads and bridges; list undone work under Sub-ideas')
        return
    if entry_tags(body, article)['kind'] == 'audit':
        # A queue audit lists ideas that earlier reviews named outside the standard sections; each item cites
        # its source review, whose record position it takes in the queue (tools/lead_queue.py).
        anchors = set(re.findall(r'<article\b[^>]*\bid="([^"]+)"', body[:article]))
        for pattern in (LEADS_RE, BRIDGES_RE):
            found = pattern.search(body, article, close)
            for item in re.findall(r'<li\b([^>]*)>', found.group(1)) if found else []:
                source = re.search(r'data-source="([^"]+)"', item)
                if source is None or source.group(1) not in anchors:
                    raise ValueError('Each Outside lead and Absurd bridge of a queue audit names its source with '
                                     'data-source="ANCHOR", an earlier entry of the record')
        return
    if entry_tags(body, article)['kind'] != 'review':
        return
    from lead_queue import is_draining, validate_review_generation
    if draining is None:
        draining = is_draining(body)
    validate_review_generation(body[article:body.find('>', article) + 1], body[article:close], draining)
    # Leads and bridges exist to answer the line's current obstacle, not as items of their own (user,
    # 26 September 2026): the review states the obstacle, and every item says how it would resolve it.
    obstacle = OBSTACLE_RE.search(body, article, close)
    if obstacle is None or len(re.sub(r'<[^>]+>', '', obstacle.group(1)).strip()) < OBSTACLE_MIN:
        raise ValueError('A route review needs an <h4>Obstacle</h4> section whose paragraph states precisely '
                         f'the obstacle the line is stuck on (at least {OBSTACLE_MIN} characters; AGENTS.md)')
    if draining:
        return
    for pattern, heading, least, what in (
            (LEADS_RE, 'Outside leads', LEADS_MIN, 'leads from areas of mathematics that study the open '
             'statement\'s objects: for each, a named theorem or source (not just a field), the open statement '
             'it targets, and where it would break. Include leads the record names but never followed'),
            (BRIDGES_RE, 'Absurd bridges', BRIDGES_MIN, 'bridges to areas that never stood near these objects, '
             'which nobody thought of applying here, from any field (mathematics, computer science, physics, chemistry or '
             'anything else): for each, the translation that would carry the objects '
             'across, what a theorem there would give, and the smallest test of the translation')):
        found = pattern.search(body, article, close)
        if found is None or len(re.findall(r'<li\b', found.group(1))) < least:
            raise ValueError(f'A route review needs an <h4>{heading}</h4> section followed by a <ul> of at '
                             f'least {least} {what} (AGENTS.md)')
        items = re.findall(r'<li\b(.*?)</li>', found.group(1), re.S)
        unanswered = [i for i, item in enumerate(items, 1) if '<strong>Answers.</strong>' not in item]
        if unanswered:
            raise ValueError(f'{heading} item(s) {unanswered} lack "<strong>Answers.</strong>": say how the '
                             'item would resolve the stated obstacle, since leads and bridges exist to answer '
                             'it (AGENTS.md)')
        untested = [i for i, item in enumerate(items, 1) if not TEST_RE.search(item)]
        if untested:
            raise ValueError(f'{heading} item(s) {untested} lack a test outcome: run each cheap test in the '
                             'review cycle and end the item with "<strong>Test.</strong> Passed ...", '
                             '"Falsified ..." or "Not run: <reason>" (AGENTS.md); falsified items stay and count')
        # Only the most promising passed items are queued; the rest are dropped at once.
        passed = [i for i, item in enumerate(items, 1) if (TEST_RE.search(item) or [None, None])[1] == 'Passed']
        picks = [i for i, item in enumerate(items, 1) if PICK_RE.search(item)]
        want = min(PICKS[heading], len(passed))
        if not set(picks) <= set(passed) or len(picks) != want:
            raise ValueError(f'Mark the {want} most promising passed {heading} item(s) with <li data-pick> '
                             f'(at most {PICKS[heading]}; passed: {passed or "none"}, marked: {picks or "none"}): '
                             'outside draining, only picks join the lead queue; the rest are dropped (user, 5 October 2026)')


OPEN_ITEMS_RE = re.compile(r'\bdata-open-items="(\d+)"')
CONVERGENCE_SPAN = 10   # research entries after which a line's open-item count must have dropped
ACROSS_GOAL_RE = re.compile(r'<h4>Across the goal</h4>\s*<ul>(.*?)</ul>', re.S)
DECISION_RE = re.compile(r'<strong>Decision\.</strong>\s*(Core|Switch)\b')


def convergence_reference(body, article, route):
    """(review id, research entries since it, its open-item count) for the line's latest review at least
    CONVERGENCE_SPAN research entries before position `article` on `route`, or None."""
    research = 0
    for position, ident, kind, _ in reversed(route_articles(body, article, route)):
        if kind == 'research':
            research += 1
        elif kind == 'review' and research >= CONVERGENCE_SPAN:
            earlier = OPEN_ITEMS_RE.search(body[position:body.index('>', position) + 1])
            if earlier:   # older reviews predating data-open-items are passed over, not a stop
                return ident, research, int(earlier.group(1))
    return None


def validate_convergence(body, article, close):
    """A line must converge, not only produce cases (user, 2 October 2026, after a day of conditional
    coverage proofs on one line left every open statement unchanged).  Each route review declares
    data-open-items="N", the open items its line still needs.  If N has not dropped since the line's
    review at least CONVERGENCE_SPAN research entries back, the line has stalled and only a goal-level
    review (data-scope="goal") is accepted: it weighs the cycles against the open statements across the
    whole goal and decides Core (work a core statement next) or Switch (take up another open statement).
    Otherwise a goal-level review is refused (user, 3 October 2026: goal-level reviews only when the
    open-item count stalls, machine-checked)."""
    if not re.search(r'data-route-item="', body) or entry_tags(body, article)['kind'] != 'review':
        return
    tag = body[article:body.index('>', article) + 1]
    count = OPEN_ITEMS_RE.search(tag)
    if count is None:
        raise ValueError('A route review declares data-open-items="N" in its article tag: the number of open '
                         'items its line still needs, so that the finisher can tell whether the line converges')
    reference = convergence_reference(body, article, entry_tags(body, article)['route'])
    stalled = reference is not None and int(count.group(1)) >= reference[2]
    goal = 'data-scope="goal"' in tag
    if goal and not stalled:
        where = (f'it dropped from {reference[2]} at review {reference[0]}, {reference[1]} research entries ago'
                 if reference else f'no review on this line is {CONVERGENCE_SPAN} or more research entries back')
        raise ValueError(f'A goal-level review is allowed only when the open-item count has stalled, but {where}. '
                         'Make it an ordinary route review (no data-scope="goal")')
    if goal:
        across = ACROSS_GOAL_RE.search(body, article, close)
        if across is None or len(re.findall(r'<li\b', across.group(1))) < 2:
            raise ValueError('A goal-level review needs an <h4>Across the goal</h4> section followed by a <ul> '
                             'with one item per open statement of the goal: its status change since the last '
                             'goal-level review and the cycles spent on it')
        if not DECISION_RE.search(body, article, close):
            raise ValueError('A goal-level review ends with "<strong>Decision.</strong> Core" (naming the core '
                             'statement worked next) or "<strong>Decision.</strong> Switch" (naming the open '
                             'statement taken up instead)')
        return
    if stalled:
        raise ValueError(f'The line still needs {count.group(1)} open items, against {reference[2]} '
                         f'at review {reference[0]}, {reference[1]} research entries ago: it is not converging. '
                         'This review must be goal-level (data-scope="goal", an Across the goal '
                         'section and a Core or Switch decision)')


FOLLOWUP_RE = re.compile(r'<h4>Bridge follow-up</h4>\s*<ul>(.*?)</ul>', re.S)
FOLLOWUP_ITEM = re.compile(r'<li\b[^>]*data-bridge="([^"]+)"[^>]*>(.*?)</li>', re.S)
LEAD_FOLLOWUP_RE = re.compile(r'<h4>Lead follow-up</h4>\s*<ul>(.*?)</ul>', re.S)
LEAD_FOLLOWUP_ITEM = re.compile(r'<li\b[^>]*data-lead="([^"]+)"[^>]*>(.*?)</li>', re.S)
FOLLOWUP_OUTCOME = re.compile(r'<strong>Follow-up\.</strong>\s*(Developed|Continuing|Closed|Reopened)\b')

# Passed Outside leads and passed Absurd bridges are both leads to develop (user, 26 September 2026:
# "Both should have followups").  (kind, section, follow-up section, follow-up item, heading, attribute)
FOLLOWUP_KINDS = (
    ('Absurd bridges', BRIDGES_RE, FOLLOWUP_RE, FOLLOWUP_ITEM, 'Bridge follow-up', 'data-bridge'),
    ('Outside leads', LEADS_RE, LEAD_FOLLOWUP_RE, LEAD_FOLLOWUP_ITEM, 'Lead follow-up', 'data-lead'),
)


def route_articles(body, article, route):
    """(position, id, kind, close) of the earlier Research-record articles on one route."""
    record = body.find('<section id="research-record">')
    out = []
    for m in re.finditer(r'<article\b', body[:article]):
        if m.start() <= record:
            continue
        tags = entry_tags(body, m.start())
        if tags['route'] != route:
            continue
        tag = body[m.start():body.index('>', m.start()) + 1]
        ident = re.search(r'\bid="([^"]+)"', tag)
        out.append((m.start(), ident.group(1) if ident else None, tags['kind'], body.find('</article>', m.start())))
    return out


def open_items(body, articles, section_re=BRIDGES_RE, followup_re=FOLLOWUP_RE, item_re=FOLLOWUP_ITEM):
    """IDs (review-anchor:item) of items of one section (Absurd bridges by default) that passed their test
    and that no follow-up item has closed."""
    passed, closed = [], set()
    for position, ident, kind, close in articles:
        text = body[position:close]
        if kind == 'review' and ident:
            found = section_re.search(text)
            if found:
                for n, item in enumerate(re.findall(r'<li\b(.*?)</li>', found.group(1), re.S), 1):
                    outcome = TEST_RE.search(item)
                    if outcome and outcome.group(1) == 'Passed':
                        passed.append(f'{ident}:{n}')
        found = followup_re.search(text)
        if found:
            for ident2, item in item_re.findall(found.group(1)):
                outcome = FOLLOWUP_OUTCOME.search(item)
                if outcome and outcome.group(1) == 'Closed':
                    closed.add(ident2)
    return [b for b in passed if b not in closed]


def validate_bridges(body, article, close):
    """Passed Absurd bridges and passed Outside leads must be developed, not only listed (user, 26 September
    2026: six bridges had passed their smallest tests and none was explored further; later "Both should have
    followups").  Open passed items wait in the lead queue (tools/lead_queue.py, checked in finish()); a
    review's Bridge follow-up and Lead follow-up lists report only items whose status changed, and every item
    they list states its outcome."""
    if not re.search(r'data-route-item="', body):
        return
    tags = entry_tags(body, article)
    if tags['kind'] not in ('research', 'review') or not tags['route']:
        return
    # Open passed items now wait in the lead queue (tools/lead_queue.py, checked in finish()), so a review
    # reports follow-ups only for items whose status changed (user, 3 October 2026: "Then you can report only
    # changes in the route reviews").  Any follow-up item it does list still states its outcome.
    if tags['kind'] == 'review':
        for name, section_re, followup_re, item_re, heading, attr in FOLLOWUP_KINDS:
            found = followup_re.search(body, article, close)
            items = dict(item_re.findall(found.group(1))) if found else {}
            bare = [b for b, text in items.items() if not FOLLOWUP_OUTCOME.search(text)]
            if bare:
                raise ValueError(f'{heading} item(s) ' + ', '.join(bare) + ' lack an outcome: end each with '
                                 '"<strong>Follow-up.</strong> Developed ...", "Continuing ..." or "Closed: '
                                 '<reason found by the attempt>" (AGENTS.md)')


GENERAL_RE = re.compile(r'<p><strong>General statement\.</strong>(.*?)</p>', re.S)


GENERAL_ID = re.compile(r'\b(?:conj|lem|thm|prop|cor):[A-Za-z0-9-]+')

ARCHITECTURE_HEADING = '<h4>Architecture review</h4>'
ARCHITECTURE_FIELDS = ('Necessary target', 'Extra requirements', 'Independent alternative',
                       'Rank normalization', 'Decision', 'Decisive test')
PROGRESS_STATES = ('advanced', 'unchanged')


def article_attribute(body, article, name):
    tag = body[article:body.index('>', article) + 1]
    found = re.search(rf'\b{re.escape(name)}="([^"]*)"', tag)
    return html.unescape(found.group(1)) if found else None


def report_paragraph(text, label):
    found = re.search(r'<p\b[^>]*>\s*<strong>' + re.escape(label) + r'\.</strong>(.*?)</p>',
                      text, re.S)
    return found.group(1) if found else ''


def validate_nonvacuity(text):
    """An entry registering a finite check says, in its own paragraph, why the check could decide."""
    found = re.search(r'<strong>Nonvacuity\.</strong>(.*?)</p>', text, re.S)
    plain = html.unescape(re.sub(r'<[^>]*>', ' ', found.group(1))).strip() if found else ''
    if len(plain) < 60:
        raise ValueError('An entry registering a finite check (an ex: claim) needs "<strong>Nonvacuity.</strong>" '
                         'with at least 60 characters: what recorded bounds give on the object at the sizes '
                         'computed, and why the outcomes that matter differ there (COMPUTATION_RULES.md, '
                         'numerical verification)')


def require_report(text, label):
    value = report_paragraph(text, label)
    plain = html.unescape(re.sub(r'<[^>]*>', ' ', value)).strip()
    if len(plain) < 40:
        raise ValueError(f'Add a substantive <p><strong>{label}.</strong> ...</p> paragraph '
                         '(AGENTS.md, goal progress and scheduled architecture review)')
    return value


def progress_history(body, before=None):
    """Read existing declarations, not guesses about the mathematics of legacy entries."""
    record = body.find('<section id="research-record">')
    if record < 0:
        return []
    end = body.find('</section>', record)
    stop = min(before if before is not None else len(body), end if end >= 0 else len(body))
    history = []
    for match in re.finditer(r'<article\b', body[record:stop]):
        position = record + match.start()
        close = body.find('</article>', position, stop)
        if close < 0:
            continue
        tags = entry_tags(body, position)
        if tags['kind'] not in ('research', 'review'):
            continue
        history.append(dict(tags, position=position, close=close,
                            obligation=article_attribute(body, position, 'data-obligation'),
                            progress=article_attribute(body, position, 'data-goal-progress'),
                            ident=article_attribute(body, position, 'id'),
                            picked=article_attribute(body, position, 'data-picked') == 'user'))
    return history


def progress_warnings(body):
    """Two unchanged research cycles flag the scheduled review; never change its cadence."""
    counts = {}
    for entry in progress_history(body):
        route = entry['route']
        if entry['kind'] == 'review':
            counts = {key: value for key, value in counts.items() if key[0] != route}
        elif entry['obligation'] and entry['progress'] in PROGRESS_STATES:
            key = (route, entry['obligation'])
            counts[key] = counts.get(key, 0) + 1 if entry['progress'] == 'unchanged' else 0
    return [f'Route {route}, obligation {obligation}: {count} cycles report unchanged goal progress. '
            'Flag this for the next scheduled Architecture review; do not add an early review.'
            for (route, obligation), count in counts.items() if count >= 2]


def pending_architecture_test(body, before=None):
    """Keep each scheduled decision pending until research tests it; audits do not consume it."""
    pending = {}
    for entry in progress_history(body, before):
        route = entry['route']
        text = body[entry['position']:entry['close']]
        if entry['kind'] == 'review':
            if ARCHITECTURE_HEADING in text and entry['ident']:
                pending[route] = entry['ident']
            else:  # historical reviews have no new-format test to enforce
                pending.pop(route, None)
        elif route in pending:
            evidence = report_paragraph(text, 'Architecture test')
            plain = html.unescape(re.sub(r'<[^>]*>', ' ', evidence)).strip()
            if len(plain) >= 40 and re.search(r'href=["\']#' + re.escape(pending[route]) + r'["\']', evidence):
                pending.pop(route)
    return pending


CLOSED_RE = re.compile(r'<strong>Follow-up\.</strong>\s*Closed\b')
STAKES_RE = re.compile(r'<strong>Stakes\.</strong>((?:(?!<strong>Follow-up\.</strong>)(?!</li>)(?!</p>).)*)', re.S)


def validate_closures(text):
    """A closed queue item states its stakes and is seen by the reviewer.

    Closing is cheap and a wrong reason passes unnoticed (10 October 2026: an item on a ceiling was closed as
    "off the critical path" although a ceiling with a deficit term is a condition on candidates, and as a
    "restatement" although the restated form was the handle).  Each Closed follow-up therefore carries
    <strong>Stakes.</strong> saying what a yes and what a no to the item's question would each give the
    open statement, and the entry links the reviewer's record, so that the reviewer has
    read the closure."""
    closed = len(CLOSED_RE.findall(text))
    if not closed:
        return
    stakes = [html.unescape(re.sub(r'<[^>]*>', ' ', found)).strip() for found in STAKES_RE.findall(text)]
    if len([s for s in stakes if len(s) >= 60]) < closed:
        raise ValueError(f'This entry closes {closed} queue item(s): give each a <strong>Stakes.</strong> '
                         'statement of at least 60 characters, in the paragraph or list item that closes it, '
                         'saying what a yes and what a no to its question would each give the open '
                         'statement (AGENTS.md; user, 10 October 2026)')
    if not re.search(r'href="[^"]*review[^"/]*\.txt"', text):
        raise ValueError('An entry that closes a queue item links the reviewer\'s record (review.txt): the '
                         'reviewer reads every closure and its stakes (AGENTS.md; user, 10 October 2026)')
    # A reviewer on 10 October 2026 twice refused a closure that rested on a paper's abstract.
    read = re.search(r'<strong>Sources read\.</strong>((?:(?!</p>)(?!</li>).)*)', text, re.S)
    plain = html.unescape(re.sub(r'<[^>]*>', ' ', read.group(1))).strip() if read else ''
    if len(plain) < 40:
        raise ValueError('An entry that closes a queue item says, after <strong>Sources read.</strong> and in at '
                         'least 40 characters, which statements of each source the closure relies on were read, '
                         'or that it relies on recorded results only (AGENTS.md)')
    if re.search(r'abstract(s)?\s+only|only\s+(the|its|their)\s+abstract|abstract,?\s+not\s+the', plain, re.I):
        raise ValueError('A closure may not rest on an abstract: read the statement of the theorem the closure '
                         'relies on, or keep the item open with the reading queued (AGENTS.md)')


READING_ITEM_RE = re.compile(r'<li\b[^>]*>((?:(?!</li>).)*?)<strong>Follow-up\.</strong>\s*Developed\b((?:(?!</li>).)*)</li>',
                             re.S)
READING_ASK_RE = re.compile(r'\bRead (?:in full |in its text )?(?:the |a |one )?(?:statements?|definitions?|theorems?|'
                            r'construction|text|paper|source)')
UNREAD_RE = re.compile(r'\bfrom memory\b|\bas (?:I )?recall(?:ed)?\b|abstract(s)?\s+only|only\s+(the|its|their)\s+abstract|'
                       r'abstract,?\s+not\s+the|\bby report\b', re.I)


def validate_developed_readings(text):
    """A sub-idea that asks for a reading is developed only by a reading that is stated.

    The closure rule (above) covers items that are Closed.  On 11 October 2026 a check that asked for the
    statement of a theorem "with its window as a function of the density" was marked Developed on a form of
    the statement recalled from memory, in the entry meant to end such readings; a reviewer returned it.  So a
    list item whose text asks to read a statement, definition, theorem, construction, text, paper or source and
    whose follow-up is Developed says, after <strong>Sources read.</strong> inside that item, which statement
    was read in its text, and may not say it rests on memory, an abstract or a report."""
    for asked, outcome in READING_ITEM_RE.findall(text):
        if not READING_ASK_RE.search(html.unescape(re.sub(r'<[^>]*>', ' ', asked))):
            continue
        item = asked + outcome
        read = re.search(r'<strong>Sources read\.</strong>((?:(?!<strong>Follow-up\.</strong>).)*)', item, re.S)
        if not read:                      # also accepted after the follow-up, inside the same item
            read = re.search(r'<strong>Sources read\.</strong>(.*)', outcome, re.S)
        plain = html.unescape(re.sub(r'<[^>]*>', ' ', read.group(1))).strip() if read else ''
        if len(plain) < 40:
            raise ValueError('A sub-idea that asks for a reading is marked Developed: say in that list item, after '
                             '<strong>Sources read.</strong> and in at least 40 characters, which statement was '
                             'read in its text (AGENTS.md; a check was marked resolved on memory, 11 October 2026)')
        if UNREAD_RE.search(plain):
            raise ValueError('A reading check may not be Developed on memory, an abstract or a report: read the '
                             'statement in its text, or keep the sub-idea Continuing (AGENTS.md)')


def validate_structural_reason(text, statuses=()):
    """An entry reporting a counterexample or a refutation of a hypothesis says why it works.

    AGENTS.md asks that an exclusion's structural reason be extracted and tried on the other candidates.  Two
    entries of 11 October 2026 reported counterexamples to a hypothesis without it, and the reason, that 1 was
    a constant-coefficient combination of the rows, was drawn only by a reviewer two entries later.  The
    trigger is the word counterexample in the title or the New mathematics paragraph, or a claim registered as
    a refutation; "refutation" alone is not one, being the name of a proof in this subject."""
    title = re.search(r'<h3\b[^>]*>(.*?)</h3>', text, re.S)
    told = (title.group(1) if title else '') + ' ' + report_paragraph(text, 'New mathematics')
    if 'refutation' not in statuses and not re.search(r'\bcounterexamples?\b', told, re.I):
        return
    given = re.search(r'<strong>Structural reason\.</strong>((?:(?!</p>)(?!</li>).)*)', text, re.S)
    plain = html.unescape(re.sub(r'<[^>]*>', ' ', given.group(1))).strip() if given else ''
    if len(plain) < 60:
        raise ValueError('This entry reports a counterexample or registers a refutation: say, after '
                         '<strong>Structural reason.</strong> and in at least 60 characters, why it works and to '
                         'which other candidates or hypotheses the reason applies (AGENTS.md)')


PROVED = {'working_proof', 'conditional'}


def validate_degenerate_cases(text, statuses=()):
    """An entry registering a proved statement says what the statement gives on degenerate inputs.

    Two theorems of 11 October 2026 were false as first drafted for want of a hypothesis, unsatisfiability in
    one and multilinear blocks in the other; each fails on the first degenerate input one writes down, and a
    reviewer found both.  The paragraph is asked of the author before the review."""
    if not PROVED & set(statuses):
        return
    given = re.search(r'<strong>Degenerate cases\.</strong>((?:(?!</p>)(?!</li>).)*)', text, re.S)
    plain = html.unescape(re.sub(r'<[^>]*>', ' ', given.group(1))).strip() if given else ''
    if len(plain) < 60:
        raise ValueError('This entry registers a proved statement: say, after <strong>Degenerate cases.</strong> '
                         'and in at least 60 characters, what the statement gives on a satisfiable system, an '
                         'empty one and an input outside its stated form, or which hypothesis excludes each '
                         '(AGENTS.md)')


def validate_process_audit(text):
    """A reviewed entry reports the reviewer's audit of how the work was done (user, 10 October 2026: the
    agent should find its own mistakes without the user's hand-holding)."""
    gate = report_paragraph(text, 'Verification gate')
    if not re.search(r'href="[^"]*review[^"/]*\.txt"', gate):
        return
    found = re.search(r'<strong>Process audit\.</strong>(.*)', gate, re.S)
    plain = html.unescape(re.sub(r'<[^>]*>', ' ', found.group(1))).strip() if found else ''
    if len(plain) < 40:
        raise ValueError('This entry links a reviewer record: report in its Verification gate, after '
                         '<strong>Process audit.</strong>, what the reviewer found about how the work was done '
                         'and what was changed, or that it found nothing (AGENTS.md, framework maintenance)')


DERIVES = re.compile(r'\bextrapolat|\bwhat-if\b|\bderived relation', re.I)


def validate_unreviewed_derivations(text):
    """A research entry that derives relations of its own goes to the cycle's reviewer.

    Three reading entries of 11 October 2026 registered no claim, so their gates said no reviewer was used,
    while they extrapolated a source's formulas and evaluated a what-if; one conclusion took a fixed constant
    for an inherited bound and steered a route review before a reviewer saw it.  An entry whose gate says no
    reviewer was used may quote a source, and may not extrapolate from it."""
    gate = html.unescape(re.sub(r'<[^>]*>', ' ', report_paragraph(text, 'Verification gate')))
    if not re.search(r'\bno reviewer\b', gate, re.I):
        return
    body = html.unescape(re.sub(r'<[^>]*>', ' ', text.replace(report_paragraph(text, 'Verification gate'), '')))
    found = DERIVES.search(body)
    if found:
        raise ValueError(f'This entry\'s Verification gate says no reviewer was used, and its text derives beyond '
                         f'its sources ("{found.group(0)}"): give the derived relations, with the definition of '
                         'every symbol a what-if varies, to the cycle\'s reviewer, and report the verdict in the '
                         'gate (AGENTS.md, one focused correctness review)')


def validate_prevention(text):
    """A Process assessment says what prevents each mistake it reports (user, 10 October 2026: the user should
    not have to ask "what will you do to prevent such mistakes in the future?")."""
    assessment = report_paragraph(text, 'Process assessment')
    if not assessment:
        return
    found = re.search(r'<strong>Prevention\.</strong>(.*)', assessment, re.S)
    plain = html.unescape(re.sub(r'<[^>]*>', ' ', found.group(1))).strip() if found else ''
    if len(plain) < 40:
        raise ValueError('End the Process assessment with <strong>Prevention.</strong> and at least 40 '
                         'characters: the committed check or rule for each mistake it reports, or why none '
                         'applies (AGENTS.md, framework maintenance)')


REVIEW_MINUTES = 40    # between two stand-in reviews: a research cycle is longer than a task's


def reviewer():
    """tools/stand_in_review.py as a module, or None where the checkout does not hold it or what it needs."""
    try:
        import stand_in_review
    except ImportError:
        return None
    return stand_in_review


def validate_review_answer(root, body, marker):
    """The stand-in review an entry owes an answer, or None. While one is unanswered, the entry being finished
    says after <strong>Review.</strong> what became of each objection (user, 11 October 2026: the reviewer
    stands in for the user's reading of the session, tools/stand_in_review.py)."""
    owed = reviewer() and reviewer().unanswered(root)
    if not owed:
        return None
    position = body.index(marker)
    article = body.rfind('<article', 0, position)
    answer = report_paragraph(body[article:body.find('</article>', article)], 'Review')
    if len(html.unescape(re.sub(r'<[^>]*>', ' ', answer)).strip()) < 40:
        raise ValueError(f'The stand-in review in {owed} is unanswered: check each of its objections against the '
                         'record, then say in a paragraph of the entry starting <strong>Review.</strong> what became '
                         'of each: fixed, queued, or wrong and why (AGENTS.md, framework maintenance)')
    return owed


def stand_in(root, owed, now=None):
    """After the finisher's work: the review that was answered is settled, and one that is due runs. Its lines
    to print; nothing here fails the finisher."""
    stand_in_review = reviewer()
    if stand_in_review is None:
        return []
    try:
        if owed:
            stand_in_review.keep(root, {**stand_in_review.state_of(root), 'unanswered': None})
        return stand_in_review.review(root, stand_in_review.session_transcript(root),
                                      now or datetime.now(timezone.utc), minutes=REVIEW_MINUTES)
    except Exception as error:      # a review is never the finisher's failure
        return [f'Stand-in review failed ({type(error).__name__}: {error}); the finisher passes without one.']


BEARING_AFTER = 2      # earlier research entries in a row, on the route, reporting unchanged goal progress
BEARING_MIN = 60
NOT_COVERED_MIN = 40


def validate_bearing(body, article, progress, text=None):
    """From the third research entry in a row that leaves a route's goal progress unchanged, the entry says
    what its result gives at the goal's own parameters (a reviewer on 10 October 2026 found three entries of
    lemmas at a fixed small size after the test they served was answered; the start warning was not enough)."""
    route = article_attribute(body, article, 'data-route')
    run = 0
    for tag in reversed(re.findall(r'<article\b[^>]*>', body[:article])):
        if f'data-route="{route}"' not in tag or 'data-kind="research"' not in tag:
            continue
        if 'data-goal-progress="unchanged"' not in tag:
            break
        run += 1
    if run < BEARING_AFTER:
        return
    found = re.search(r'<strong>Bearing\.</strong>(.*)', progress, re.S)
    plain = html.unescape(re.sub(r'<[^>]*>', ' ', found.group(1))).strip() if found else ''
    if len(plain) < BEARING_MIN:
        raise ValueError(f'{run} research entries in a row on {route} report unchanged goal progress: end the '
                         f'Goal progress paragraph with <strong>Bearing.</strong> and at least {BEARING_MIN} '
                         "characters saying what this entry's result gives at the goal's own parameters, or "
                         'that it gives nothing there and why the cycle was spent on it (AGENTS.md, goal progress)')
    # The statement alone did not stop a spell: four entries on one item each said they gave nothing at the
    # goal's parameters (review of 10 October 2026).  So the entry also declares it, and two such entries in a
    # row on one queue item end that item's turn.
    # A follow-up named as its next attempt a line the record already held and a review had stopped (10
    # October 2026): in such a run, an entry that continues its item says what it searched before naming it.
    if text is not None and re.search(r'<strong>Follow-up\.</strong>\s*Continuing', text):
        searched = re.search(r'<strong>Record search\.</strong>\s*([^<]*)', text)
        if searched is None or len(searched.group(1).strip()) < 40:
            raise ValueError('This entry continues its item after a run of unchanged goal progress: state '
                             '"<strong>Record search.</strong>" with the registry searches made for the next '
                             'attempt it names and what they returned (AGENTS.md, goal progress)')
    tag = body[article:body.find('>', article) + 1]
    declared = re.search(r'data-bearing="(none|some)"', tag)
    if declared is None:
        raise ValueError('Declare data-bearing="none" or "some" on the article: whether this entry gives '
                         "anything at the goal's own parameters, as its Bearing statement says (AGENTS.md)")
    # A bearing that claims something was closed, in two entries in a row, with a summary sentence wider
    # than the proof (reviews of 10 October 2026): it ends with what the result does not cover.
    if declared.group(1) == 'some':
        uncovered = re.search(r'<strong>Not covered\.</strong>(.*)', found.group(1), re.S)
        plain = html.unescape(re.sub(r'<[^>]*>', ' ', uncovered.group(1))).strip() if uncovered else ''
        if len(plain) < NOT_COVERED_MIN:
            raise ValueError('This entry declares data-bearing="some": end its Bearing statement with '
                             f'"<strong>Not covered.</strong>" and at least {NOT_COVERED_MIN} characters '
                             'listing the cases its result does not reach, with no summary after the list '
                             '(AGENTS.md, goal progress)')
    item =re.search(r'data-(?:check|lead|bridge)="([^"]+)"', tag)
    if item is None:
        return
    earlier = [t for t in re.findall(r'<article\b[^>]*>', body[:article])
               if f'data-route="{route}"' in t and 'data-kind="research"' in t][-2:]
    same = [t for t in earlier if re.search(r'data-(?:check|lead|bridge)="' + re.escape(item.group(1)) + '"', t)
            and 'data-bearing="none"' in t]
    if len(same) == 2:
        raise ValueError(f'The last two entries developed {item.group(1)} and declared that they give nothing '
                         "at the goal's parameters: develop a different queue item now (AGENTS.md, goal progress)")


def validate_progress(body, article, close, *, check_registered_claims=True):
    """Check reporting and follow-through, not the mathematical truth of an advance.

    Draft append checks structure before claim registration; finalization always checks
    the registered evidence as well.
    """
    if not re.search(r'data-route-item="', body):
        return
    tags = entry_tags(body, article)
    if tags['kind'] not in ('research', 'review'):
        return
    obligation = article_attribute(body, article, 'data-obligation')
    state = article_attribute(body, article, 'data-goal-progress')
    if not obligation or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9:_.-]*', obligation):
        raise ValueError('Name the stable open-statement ID in data-obligation; do not use a new local '
                         'subproblem name each cycle')
    if state not in PROGRESS_STATES:
        raise ValueError('Set data-goal-progress="advanced" or "unchanged"; new mathematics alone '
                         'does not establish goal progress')
    text = body[article:close]
    require_report(text, 'New mathematics')
    progress = require_report(text, 'Goal progress')
    validate_prevention(text)
    validate_process_audit(text)
    if any(cid.startswith('ex:') for cid in entry_claims(body, article)):
        validate_nonvacuity(text)
    if tags['kind'] == 'research':      # queue items are developed, and so closed, in research entries
        validate_unreviewed_derivations(text)
        validate_closures(text)
        validate_developed_readings(text)
        if check_registered_claims:
            known = registered_status()
            statuses = {known.get(cid) for cid in entry_claims(body, article)}
            validate_structural_reason(text, statuses)
            validate_degenerate_cases(text, statuses)
        else:
            validate_structural_reason(text)
        if state == 'unchanged':
            validate_bearing(body, article, progress, text)
    if state == 'advanced':
        supporting = [cid for cid in entry_claims(body, article)
                      if re.search(r'(?<![\w:-])' + re.escape(cid) + r'(?![\w:-])', progress)]
        if check_registered_claims:
            statuses = registered_status()
            supporting = [cid for cid in supporting if statuses.get(cid) in
                          ('working_proof', 'established', 'conditional', 'refutation')]
        if not supporting:
            raise ValueError('Advanced Goal progress must cite a claim declared by this entry with a '
                             'proof, conditional reduction, or refutation; finite checks and conjectures '
                             'alone do not certify the goal-critical implication')
    if tags['kind'] == 'review':
        if not article_attribute(body, article, 'id'):
            raise ValueError('An Architecture review needs a stable article id for its next test')
        if ARCHITECTURE_HEADING not in text:
            raise ValueError('The scheduled review needs an <h4>Architecture review</h4> section; '
                             'the six-research-cycles/one-review cadence is unchanged')
        section = text.split(ARCHITECTURE_HEADING, 1)[1].split('<h4>', 1)[0]
        for label in ARCHITECTURE_FIELDS:
            value = require_report(section, label)
            if label == 'Independent alternative' and not re.search(r'href=["\'][^"\']+["\']', value):
                raise ValueError('Independent alternative must link the existing reviewer evidence; '
                                 'brief the same medium reviewer with goal and tools before the preferred route')
            if label == 'Necessary target':
                down = re.search(r'<strong>Downstream\.</strong>(.*)', value, re.S)
                plain = html.unescape(re.sub(r'<[^>]*>', ' ', down.group(1))).strip() if down else ''
                if len(plain) < 60 or not re.search(r'\b(?:thm|cor|prop|lem):[\w-]+', plain):
                    raise ValueError('Necessary target must end with "<strong>Downstream.</strong>": the target '
                                     'evaluated through the proved downstream statements, citing their claim '
                                     'IDs, with the explicit consequence and whether it is the goal or weaker '
                                     '(AGENTS.md, Necessary target)')
            if label == 'Decisive test':
                searched = re.search(r'<strong>Record search\.</strong>(.*)', value, re.S)
                plain = html.unescape(re.sub(r'<[^>]*>', ' ', searched.group(1))).strip() if searched else ''
                if len(plain) < 40:
                    raise ValueError('Decisive test must end with "<strong>Record search.</strong>" naming the '
                                     'registry searches made for the test and what they returned: a test the '
                                     'record already answers decides nothing (AGENTS.md, Decisive test)')
                power = re.search(r'<strong>Power\.</strong>(.*?)(?=<strong>Record search\.</strong>|$)', value, re.S)
                plain = html.unescape(re.sub(r'<[^>]*>', ' ', power.group(1))).strip() if power else ''
                if len(plain) < 40:
                    raise ValueError('Decisive test must state "<strong>Power.</strong>" before its Record search: '
                                     'what the recorded ceilings and method limits give on the test\'s object, '
                                     'and, for a computation, the sizes reachable and why its outcomes differ '
                                     'there; a test whose every outcome fits every answer decides nothing '
                                     '(AGENTS.md, Decisive test)')
    else:
        target = pending_architecture_test(body, article).get(tags['route'])
        if target and article_attribute(body, article, 'data-picked') != 'user':
            evidence = require_report(text, 'Architecture test')
            if not re.search(r'href=["\']#' + re.escape(target) + r'["\']', evidence):
                raise ValueError(f'Architecture test must report the outcome of the scheduled decision '
                                 f'and link #{target}; a further local lemma is not a substitute')


def entry_claims(body, article):
    tag = body[article:body.index('>', article) + 1]
    return [c for c in (re.search(r'data-claims="([^"]*)"', tag) or [None, ''])[1].split() if c != 'none']


FINITE_PREFIXES = ('ex:', 'check:')


@functools.cache
def registered_status():
    """Claim ID to mathematical status, parsed once per process: nothing here writes the registry,
    and validating it belongs to the claim checks, not to a status lookup."""
    registry = ROOT / 'research/claims/index.json'
    return {c['id']: c.get('mathematical_status') for c in read_json(registry)['claims']} if registry.exists() else {}


def cases_only(body, article, status_of=None):
    """An entry that reports only cases: every registered claim is a finite check (ex: or check:) and
    none of them is registered as a refutation.  Decided from the claims, not from status-line words:
    a status such as "a failed proof route" does not make an entry more than a finite check."""
    claims = entry_claims(body, article)
    reports_cases = 'finite check' in entry_status(body, article).lower() or any(c.startswith(FINITE_PREFIXES) for c in claims)
    if not reports_cases or not all(c.startswith(FINITE_PREFIXES) for c in claims):
        return False
    if not claims:
        return True
    status_of = registered_status() if status_of is None else status_of
    return not any(status_of.get(c) == 'refutation' for c in claims)


def registers_cases(body, article, status_of=None):
    """The entry registers a new finite check that is not a refutation (a decisive refutation is not
    case-list growth, so it is exempt)."""
    claims = [c for c in entry_claims(body, article) if c.startswith(FINITE_PREFIXES)]
    if not claims:
        return False
    status_of = registered_status() if status_of is None else status_of
    return any(status_of.get(c) != 'refutation' for c in claims)


CASE_WINDOW, CASE_LIMIT = 5, 3


def entry_status(body, article):
    meta = body.find('<p class="entry-meta">', article)
    return re.sub(r'<[^>]*>', '', body[meta:body.find('</p>', meta)]).split('Produced by')[0]


ENTRY_PARAGRAPHS = re.compile(r'data-entry-paragraphs="([^"]+)"')


def required_paragraphs(body, kind='research'):
    """Labels this notebook requires in each new entry of the given kind.  A living section of the notebook
    itself declares them as data-entry-paragraphs="Label one|review:Label two": an item without a kind
    applies to research entries.  A notebook without the attribute requires nothing, so the duty stays
    local to the notebook that states it (a rule kept only in prose is forgotten)."""
    record = body.find('<section id="research-record">')
    found = ENTRY_PARAGRAPHS.search(body, 0, record if record >= 0 else len(body))
    labels = []
    for item in (found.group(1).split('|') if found else []):
        owner, _, label = item.rpartition(':')
        if label.strip() and (owner.strip() or 'research') == kind:
            labels.append(label.strip())
    return labels


def validate_paragraphs(body, article, close):
    """Each entry carries every paragraph its notebook declares for its kind, with real content."""
    kind = entry_tags(body, article)['kind']
    for label in required_paragraphs(body, kind):
        found = re.search(r'<p><strong>' + re.escape(label) + r'\.</strong>(.*?)</p>', body[article:close], re.S)
        if not found or len(re.sub(r'<[^>]*>', ' ', found.group(1)).strip()) < 40:
            raise ValueError(f'This notebook requires a <p><strong>{label}.</strong> ...</p> paragraph in every '
                             f'{kind} entry (data-entry-paragraphs on its living sections)')


SUGGESTIONS_RE = re.compile(r"<h4>Reviewer(?:'s|&#39;s|\u2019s)? suggestions[^<]*</h4>(.*?)(?=<h4>|<p><strong>|$)", re.S)
RECORD_RE = re.compile(r'<strong>Record\.</strong>(.*)', re.S)


def validate_suggestions(body, article, close):
    """A reviewer's suggestion is a lead like any other: before it is recorded, let alone adopted, the
    record is searched for it (user, 9 October 2026, after an adopted count contradicted a computation two
    reviews old).  Every item under an <h4>Reviewer's suggestions ...</h4> heading ends with
    <strong>Record.</strong> and what the search found: claim IDs or anchors, or the words searched without
    a match."""
    for section in SUGGESTIONS_RE.finditer(body[article:close]):
        items = re.findall(r'<li\b[^>]*>(.*?)</li>', section.group(1), re.S)
        if not items:
            raise ValueError("A Reviewer's suggestions section lists each suggestion as a <li> item")
        bare = [i for i, item in enumerate(items, 1)
                if not (found := RECORD_RE.search(item))
                or len(re.sub(r'<[^>]*>', ' ', found.group(1)).strip()) < 20]
        if bare:
            raise ValueError(f"Reviewer's suggestions item(s) {bare} lack \"<strong>Record.</strong>\" with the "
                             'outcome of a record search (tools/search-claims.py and the notebook): the claim '
                             'IDs or anchors that bear on the suggestion, or the words searched without a '
                             'match (AGENTS.md)')


def validate_general(body, article, close):
    """AGENTS.md: restricted examples must test a named general statement; enforce it mechanically.
    Every research entry states its general claim for all parameters, and two finite-check entries
    in a row on one route (neither with a proof or refutation) are rejected."""
    if not re.search(r'data-route-item="', body):     # active once the notebook declares route items
        return
    tags = entry_tags(body, article)
    if tags['kind'] != 'research':
        return
    found = GENERAL_RE.search(body, article, close)
    text = re.sub(r'<[^>]*>', ' ', found.group(1)).strip() if found else ''
    if len(text) < 40:
        raise ValueError('A research entry needs a <p><strong>General statement.</strong> ...</p> '
                         'paragraph: the claim this cycle tests or proves, for all parameters, with '
                         'its conjectured bound as a formula (AGENTS.md, restricted examples)')
    ids = GENERAL_ID.findall(found.group(1))
    if (ROOT / 'research/claims/index.json').exists():
        ids = [i for i in ids if i in registered_status()]
    if not ids:
        raise ValueError('The General statement must cite the registered claim ID (conj:, lem:, thm:, '
                         'prop: or cor:) that states it for all parameters; register a conjecture if '
                         'it is not proved')
    record = body.find('<section id="research-record">')
    earlier = [m.start() for m in re.finditer(r'<article\b', body[:article]) if m.start() > record]
    status_of = registered_status()
    if cases_only(body, article, status_of):
        for position in reversed(earlier):
            previous = entry_tags(body, position)
            if previous['kind'] == 'formalization' or previous['route'] != tags['route']:
                continue
            if previous['kind'] == 'research' and cases_only(body, position, status_of):
                raise ValueError('The previous research entry on this route was also a finite check '
                                 'without a proof or refutation. Stop adding cases: this entry must '
                                 'attempt a proof or a refutation of its General statement (AGENTS.md)')
            break
    if registers_cases(body, article, status_of):
        window = [article]
        for position in reversed(earlier):
            previous = entry_tags(body, position)
            if previous['kind'] != 'research' or previous['route'] != tags['route']:
                continue            # reviews and formalization entries neither count nor reset
            window.append(position)
            if len(window) == CASE_WINDOW:
                break
        count = sum(registers_cases(body, position, status_of) for position in window)
        if count > CASE_LIMIT:
            raise ValueError(f'{count} of the last {len(window)} research entries on this route register '
                             f'new finite checks other than refutations (at most {CASE_LIMIT} of any {CASE_WINDOW}). The case list is '
                             'growing: this entry must derive a general formula or proof without new finite '
                             'checks (AGENTS.md, restricted examples)')


# External labels kept by the odd-prime name map (entry-2026-09-22-result-names); every other
# "Lemma K"-style code must be replaced by a descriptive name.
from result_names import KEPT_LABELS, LABEL_NOUNS, letter_code_labels  # noqa: E402


def validate_marker(body, marker, draining=None):
    if body.count(marker) != 1:
        raise ValueError(f'Notebook must contain exactly one {marker}')
    position = body.index(marker)
    record = body.find('<section id="research-record">')
    end = body.find('</section>', record) if record >= 0 else -1
    article = body.rfind('<article', record, position) if record >= 0 else -1
    close = body.find('</article>', article) if article >= 0 else -1
    if not (0 <= record < article < position < close < end):
        raise ValueError('Timing marker must be inside a Research-record article')
    meta = body.find('<p class="entry-meta">', article, position)
    if meta < 0 or body.find('</p>', meta, position) < 0:
        raise ValueError('The entry needs a <p class="entry-meta"> status line before its timing marker')
    status = re.sub(r'<[^>]*>', '', body[meta:body.find('</p>', meta)]).split('Produced by')[0]
    if len(status.strip()) > STATUS_LIMIT:
        raise ValueError(f'The status line has {len(status.strip())} characters; keep it under '
                         f'{STATUS_LIMIT}: the status and one clause of scope, details in the entry')
    validate_route(body, article)
    validate_general(body, article, close)
    validate_paragraphs(body, article, close)
    validate_suggestions(body, article, close)
    validate_leads(body, article, close, draining=draining)
    validate_convergence(body, article, close)
    validate_bridges(body, article, close)
    validate_progress(body, article, close)
    if '$' in body[article:close]:
        # MathJax treats a dollar sign as an inline-math delimiter; the notebook uses \( \).
        raise ValueError('The entry contains a dollar sign, which MathJax reads as a math delimiter; '
                         'write mathematics with \\( \\) and currency as "USD 5"')
    coded = letter_code_labels(body[article:close])
    if coded:
        raise ValueError('The entry names results by letter codes ' + ', '.join(coded) + ': cite them '
                         'by descriptive names (CLAUDE.md, Naming results), e.g. "the constant-row clamp" '
                         'rather than "Lemma K"; the claim ID usually gives the name')
    control = sorted({c for c in body[article:close] if ord(c) < 32 and c != '\n'})
    if control:
        # "\rho", "\text", "\bigl" written through a non-raw Python string become CR, TAB, BS.
        raise ValueError('The entry contains control characters ' + repr(control) + ': a TeX command '
                         'was written through a non-raw string (\\r, \\t, \\b, \\f); repair the formulas')


def credit_producer(body, marker, producer):
    """Name the recorded agent and model at the end of the entry's status line."""
    article = body.rfind('<article', 0, body.index(marker))
    meta = body.index('<p class="entry-meta">', article)
    close = body.index('</p>', meta)
    if producer in body[meta:close]:
        return body
    return (body[:close] + ' <span data-generated="finish-turn-producer-v1">'
            + producer + '</span>' + body[close:])


CHECKS_WARN_S = 5.0


def checks_note(elapsed):
    """A warning when the checks before the clock stops are slow: they read the notebook and the claim
    registry, so repeated work there grows with the repository and recurs at every cycle."""
    if elapsed <= CHECKS_WARN_S:
        return ''
    return (f"Warning: the finisher's checks took {elapsed:.1f} s (limit {CHECKS_WARN_S:g} s). Profile "
            'them (python3 -m cProfile -s cumtime tools/finish-turn.py TURN) and remove the repeated '
            'work before it grows.\n')


def validate_append_only(root):
    """Earlier entries must match HEAD; corrections belong in a new dated entry."""
    checker = root / 'tools/check-append-only.py'
    if not checker.exists():
        return
    result = subprocess.run([sys.executable, str(checker), '--base', 'HEAD'], cwd=root,
                            capture_output=True, text=True)
    if result.returncode != 0:
        raise ValueError(result.stdout.strip())


def validate_queue(root, notebook):
    """The lead and bridge queue against HEAD's notebook (tools/lead_queue.py)."""
    from lead_queue import check, is_draining, SECTION_RE
    relative = notebook.resolve().relative_to(root.resolve()).as_posix()
    head = subprocess.run(['git', 'show', f'HEAD:{relative}'], cwd=root, capture_output=True, text=True)
    body = notebook.read_text()
    check(head.stdout if head.returncode == 0 else None, body, notebook, root)
    section = SECTION_RE.search(body)
    return is_draining(head.stdout if head.returncode == 0 else None,
                       section.group(1) if section else None)


SCRATCH_CAP = 500 * 10**6   # bytes a session may keep in its scratchpad at a checkpoint


def scratchpad(env=os.environ, home=Path.home(), uid=None):
    """The Claude Code session's scratchpad, or None: ~/.claude/jobs/<id[:8]>/tmp for background sessions,
    /tmp/claude-<uid>/<project>/<id>/scratchpad for interactive ones."""
    ident = env.get('CLAUDE_CODE_SESSION_ID')
    if not ident:
        return None
    job = home / '.claude/jobs' / ident[:8] / 'tmp'
    if job.is_dir():
        return job
    base = Path(f'/tmp/claude-{os.getuid() if uid is None else uid}')
    found = sorted(base.glob(f'*/{ident}/scratchpad')) if base.is_dir() else []
    return found[0] if found else None


def check_scratch(env=os.environ, home=Path.home(), cap=SCRATCH_CAP):
    """A session's scratch files are its own to delete (user, 3 October 2026, with the disk near its floor).
    Fail while the scratchpad exceeds the cap; never delete, since promotion comes first."""
    if env.get('CODEX_THREAD_ID') and not env.get('CLAUDE_CODE_SESSION_ID'):
        from codex_state import check_owned_scratch
        check_owned_scratch(ROOT, env['CODEX_THREAD_ID'], cap)
        return
    pad = scratchpad(env, home)
    if pad is None:
        return
    files = []
    for path in pad.rglob('*'):
        try:   # a file can vanish between the listing and the stat
            if path.is_file() and not path.is_symlink():
                files.append((path.stat().st_size, path))
        except OSError:
            continue
    total = sum(size for size, _ in files)
    if total > cap:
        largest = ', '.join(f'{p.relative_to(pad)} ({size // 10**6} MB)' for size, p in sorted(files)[-5:][::-1])
        raise ValueError(f'The session scratchpad {pad} holds {total // 10**6} MB, over the {cap // 10**6} MB cap '
                         f'(AGENTS.md). Largest: {largest}. Promote what is still needed to research/results or '
                         'research/provenance, delete the rest, and rerun')


def finish(root, turn, next_turn=None, notebook_name=None):
    from notebooks import selected, paths
    started = time.monotonic()
    check_scratch()
    item = selected(notebook_name, root)
    notebook = root / item["source"]
    first = json.loads((root/'research/logs'/f'{turn}.jsonl').read_text().splitlines()[0])
    if first.get('notebook',item['name']) != item['name']:
        raise ValueError('Selected notebook differs from timing session notebook')
    marker = f'<!-- TIMING {turn} -->'
    owners = [p for p in paths(root) if marker in p.read_text()]
    if owners != [notebook]:
        raise ValueError("Timing marker must belong uniquely to selected notebook " + item["name"])
    draining = validate_queue(root, notebook)
    validate_marker(notebook.read_text(), marker, draining=draining)
    owed = validate_review_answer(root, notebook.read_text(), marker)
    check_context(root, item["name"])  # Fail before stopping timing, archiving, or changing the notebook.
    validate_append_only(root)
    if (root / 'research/claims/index.json').exists():
        claims = load_claims(root / 'research/claims/index.json')
        if (root / 'research/CLAIM_INDEX.md').read_text() != render_claims(claims):
            raise ValueError('Generated claim index is stale; run tools/claim-index.py render')
        contract = check_revision(claims, root=root)
        if not contract['passed']:
            raise ValueError('Changed-claim metadata incomplete:\n' + '\n'.join(contract['errors']))
    if next_turn and (root / 'research/logs' / f'{next_turn}.jsonl').exists():
        raise ValueError('Next session already exists; omit --next when retrying finalization')
    print(checks_note(time.monotonic() - started), end='')

    if (root / 'research/claims/index.json').exists():
        # The existing maintenance gate already requires reasoned significance
        # dispositions. Reuse that work; no second essay or automatic web audit.
        assessed = [r for r in contract['required_reviews'] if 'significance' in r['fields']]
        history, added = sync_attention(root, claims)
        print(f'Significance check: {len(assessed)} changed claim dispositions; '
              f'{len(added)} new/reopened attention items.')
        print(attention_brief(claims, history), end='')
        print('Stage attention history/view if changed: research/claims/attention.json research/ATTENTION.md')

    compute = str(root / 'compute.sh')
    fragment = root / 'research/results' / turn / 'timing.html'
    subprocess.run([compute, 'report', turn, '--stop', '--html-out', str(fragment)],
                   cwd=root, check=True, stdout=subprocess.PIPE, text=True)
    if next_turn:
        # Continuous research keeps the finished cycle's recorded agent and model.
        journal = root / 'research/logs' / f'{turn}.jsonl'
        first = json.loads(journal.read_text().splitlines()[0]) if journal.exists() else {}
        inherit = [f'--{key}={first[key]}' for key in ('agent', 'model') if first.get(key)]
        started = subprocess.run([compute, 'start', next_turn, *inherit, '--notebook', item['name']], cwd=root,
                                 check=True, stdout=subprocess.PIPE, text=True)
        guidance = next_cycle_guidance(started.stdout)
        subprocess.run([compute, 'phase', next_turn, 'preparation', '--note',
                        f'Finalize checkpoint {turn}, then begin the next research cycle'],
                       cwd=root, check=True)

    # Archival may copy large outputs, so keep it inside the shared resource limits.
    archive = [compute]
    if next_turn:
        archive += ['--session', next_turn]
    archive += ['--threads', '1', '--category', 'local_processing',
                '--tail-bytes', '1000', sys.executable,
                str(root / 'tools/archive-session.py'), turn]
    subprocess.run(archive, cwd=root, check=True)

    # Re-read after commands so unrelated edits made meanwhile are retained.
    current = notebook.read_text()
    try:
        validate_marker(current, marker)
    except ValueError as error:
        raise ValueError(f'Timing and archive are saved, but {error}') from error
    first = json.loads((root / 'research/logs' / f'{turn}.jsonl').read_text().splitlines()[0])
    producer = (f"Produced by {html.escape(first.get('agent', 'unrecorded'))} "
                f"({html.escape(first.get('model', 'unrecorded'))}).")
    timing = fragment.read_text().strip()
    timing = timing.replace('<div class="timing-report"',
                            '<div data-generated="finish-turn-timing-v1" class="timing-report"', 1)
    updated = credit_producer(current, marker, producer).replace(marker, timing)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode='w', dir=root, prefix='.notebook-timing-',
                                         encoding='utf-8', delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(updated)
        temporary.chmod(notebook.stat().st_mode & 0o777)
        os.replace(temporary, notebook)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
    print(f'Finished {turn} in {item["name"]}: timing embedded and evidence archived; review and commit.')
    print(f'Stage with the entry: {item["source"]} '
          f'research/results/{turn}/timing.html research/provenance/session-records/{turn}')
    for line in stand_in(root, owed):
        print(line)
    if next_turn:
        print(f'{next_turn} is running in preparation phase.')
        # Printed last so that a truncated view of this output still shows what the next entry must be.
        for line in guidance:
            print(f'NEXT CYCLE {next_turn}: {line}')


def next_cycle_guidance(start_stdout):
    """The advisory notes `compute.sh start` printed after the session path (user instruction,
    24 September 2026: a required route review went unnoticed because this output was discarded)."""
    lines = [line.strip() for line in start_stdout.splitlines() if line.strip()]
    return lines[1:]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('turn', type=session_name)
    parser.add_argument('--next', dest='next_turn', type=session_name,
                        help='Start the next cycle immediately after the timing snapshot')
    parser.add_argument('--notebook', help='Research thread name; defaults to worktree selection or main')
    args = parser.parse_args()
    finish(ROOT, args.turn, args.next_turn, args.notebook)


if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError, subprocess.CalledProcessError) as error:
        print(f'finish-turn.py: {error}', file=sys.stderr)
        sys.exit(1)
