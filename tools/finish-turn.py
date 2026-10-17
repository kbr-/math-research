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
from claim_registry import cached_json, read_json, validate as validate_claims, render as render_claims
from claim_maintenance import check_revision
from notebook_context import check as check_context
from claim_attention import sync as sync_attention, brief as attention_brief
from lead_queue import LEADS_RE, BRIDGES_RE
from bearing_ledger import validate as validate_bearing_ledger
from notebook_math import strip_tags, strip_tags_tight

ROOT = Path(__file__).resolve().parents[1]


_registry_snapshot = sys.modules['claim_registry']._snapshot     # the shared cache, cleared by tests


def registry_data(path):
    """The shared parse of claim_registry.cached_json."""
    return cached_json(path)


def load_claims(path):
    # Status lookup is intentionally cheap; finalization still validates the full schema.
    return validate_claims(registry_data(path))


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


def review_cadence(kinds):
    """Notebook-wide research count since the latest review; other entry kinds do not count."""
    streak = 0
    for kind in reversed(list(kinds)):
        if kind == 'review':
            return streak, True
        if kind == 'research':
            streak += 1
    return streak, False


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
    streak, after_review = review_cadence(entry_tags(body, position)['kind'] for position in earlier)
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
# Read after the Test label only, so that an item's description or Answers paragraph may use the words.
PASSED_ELSEWHERE_RE = re.compile(r'^\s*Passed\s+(?:only\s+)?for\b|\bin another form\b|\brestates the open problem\b',
                                 re.I)
NOT_RUN_UNREAD_RE = re.compile(r'\b(recalled|not read|unread|not retrieved)\b', re.I)
# A Retrieval paragraph names a tool or a search or fetch it made; "Retrieval. None tried." does not pass.
RETRIEVAL_RE = re.compile(r'<strong>Retrieval\.</strong>(?:(?!</li>).)*?\b(held_sources|arxiv_source|browser_get|'
                          r'firefox_get|search(?:ed|es)?|fetch(?:ed)?|WebSearch|WebFetch)\b', re.I | re.S)
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
    if obstacle is None or len(strip_tags_tight(obstacle.group(1)).strip()) < OBSTACLE_MIN:
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
        # A review of 11 October 2026 marked two leads passed on tests of a recalled theorem; each lead's own
        # stated break point, a line of arithmetic, was never evaluated, and one of them broke there.
        unbroken = [i for i in passed if '<strong>Break point.</strong>' not in items[i - 1]]
        if unbroken:
            raise ValueError(f'{heading} item(s) {unbroken} are marked Passed without "<strong>Break point.'
                             '</strong>": say where the translation would break and what the test found there; a '
                             'test of the named theorem alone, or of a recalled statement, is Not run for the '
                             'translation (AGENTS.md)')
        # A review of 16 October 2026 marked items Passed on a test of another cost ("Passed for the quadratic
        # cost") or of a translation whose Break point found it the open problem "in another form"; such a mark is
        # Not run or Falsified for the translation.  It does not catch a test of the named theorem's hypotheses
        # alone (the same review's third such mark).
        narrowed = [(i, found.group(0).strip()) for i in passed
                    if (found := PASSED_ELSEWHERE_RE.search(items[i - 1].split('<strong>Test.</strong>', 1)[1]))]
        if narrowed:
            raise ValueError(f'{heading} item(s) marked Passed on a test of another object, or on a translation its '
                             f'own Break point finds a restatement: {narrowed}. Mark it Not run for the translation, '
                             'or Falsified, and pick only items whose test reached the translation (AGENTS.md)')
        # A review of 16 October 2026 left items Not run as "recalled, not read" although the statements were a
        # search away; such an item says what retrieval was tried and how it ended. The source may be marked
        # unread in its citation, before the Test label, as well as in the reason after it.
        unretrieved = [i for i, item in enumerate(items, 1) if (TEST_RE.search(item) or [None, None])[1] == 'Not run'
                       and NOT_RUN_UNREAD_RE.search(item)
                       and not RETRIEVAL_RE.search(item)]
        if unretrieved:
            raise ValueError(f'{heading} item(s) {unretrieved} are Not run on a source recalled or unread without '
                             'a "<strong>Retrieval.</strong>" paragraph naming what retrieval was tried '
                             '(tools/held_sources.py, tools/arxiv_source.py, tools/browser_get.cjs, a search or a '
                             'fetch) and how it ended (AGENTS.md); the check reads the names, not the outcome')
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


QUEUE_SECTION_RE = re.compile(r'<section id="lead-queue"[^>]*>(.*?)</section>', re.S)
QUEUED_BUILD_RE = re.compile(r'<li\b[^>]*data-build="([^"]+)"[^>]*data-source="([^"]+)"')
BUILT_RE = re.compile(r'<li\b[^>]*data-build="[^"]+"[^>]*>(?:(?!</li>).)*?<strong>Follow-up\.</strong>\s*Developed\b', re.S)
BUILDS_PARAGRAPH_RE = re.compile(r'<p><strong>Builds\.</strong>(.*?)</p>', re.S)
QUEUED_ITEM_RE = re.compile(r'<li\b[^>]*data-build="([^"]+)"[^>]*>')
# An entry that develops a build item itself: the item on its tag and a Developed follow-up of its own.
BUILT_ENTRY_RE = re.compile(r'\A<article\b[^>]*\bdata-build="[^"]+"[^>]*>.*<p><strong>Follow-up\.</strong>\s*Developed\b',
                            re.S)


def queued_in(tag, idents):
    """Whether a queued item's <li> tag places it in the period whose entries have the anchors `idents`."""
    source = re.search(r'\bdata-source="([^"]*)"', tag)
    after = re.search(r'\bdata-after="([^"]*)"', tag)
    named = re.match(r'[A-Za-z0-9-]+', html.unescape(source.group(1))) if source else None
    return (bool(source and html.unescape(source.group(1)) in idents) or bool(named and named.group(0) in idents)
            or bool(after and after.group(1) in idents))


OWED_PARAGRAPH_RE = re.compile(r'<strong>Owed attempt\.</strong>((?:(?!</p>)(?!</li>).)*)', re.S)
OWED_UNMADE_RE = re.compile(r'\bnot reached\b|\bnot made\b|\bunmade\b|\b(?:is|was) not run\b|\bskipped\b|'
                            r'\b(?:did|have) not read\b|\bnot read by me\b|'
                            r'\bread by the reviewer\b|\bthe reviewer (?:then )?read\b', re.I)
OWED_REASON_RE = re.compile(r'\bbecause\b|\bsince\b|\bcame first\b|\bcomes first\b|\bthe reason\b', re.I)
OWED_PROCEDURAL_RE = re.compile(r'\b(?:\w+ )?review(?:\'s)? (?:decided|asked|named|gave|said|listed|put|having put|'
                                r'replaced|chose|decision)\b|\bby the (?:\w+ )?review\'s decision\b|'
                                r'\bthe (?:last )?next step (?:asked|named|said)\b|\bthe reviewer asked\b|'
                                r'\bby the decision\b|\bthe order chosen\b|\bthe plan was\b', re.I)
OWED_REVIEWER_READ_RE = re.compile(r'\bread by the reviewer\b|\bthe reviewer (?:then )?read\b', re.I)
OWED_VERDICT_RE = re.compile(r'\bvacuous\b|\bcannot\b|\bimpossible\b|\bnot needed\b|\bunnecessary\b|'
                             r'\balready (?:decided|settled|answered)\b|\bpointless\b', re.I)
OWED_FROM = '2026-10-12'
WINDOW_FROM = '2026-10-16'      # reviews from this date say where their test's instance stands
GATE_PARAGRAPH_RE = re.compile(r'<p><strong>Verification gate\.</strong>(.*?)</p>', re.S)


def attempt_checked(text):
    """Whether the entry's Verification gate paragraph says, after its Attempt checked. marker, at least forty
    characters of plain text before the next marker."""
    gate = GATE_PARAGRAPH_RE.search(text)
    said = re.search(r'<strong>Attempt checked\.</strong>(.*?)(?=<strong>|$)', gate.group(1) if gate else '', re.S)
    return bool(said) and len(html.unescape(strip_tags(said.group(1))).strip()) >= 40


def validate_owed_unmade(body, article, close):
    """An Owed attempt paragraph that reports the named attempt unmade, or made by the reviewer, gives the reason
    another came first: two entries of 11 October 2026 on one item wrote "not reached" and went on to an easier
    neighbour of the owed proof, which their reviewer then read.  Entries dated before the check are exempt."""
    tag = body[article:body.index('>', article) + 1]
    dated = re.search(r'\bid="entry-(\d{4}-\d{2}-\d{2})-', tag)
    if dated is None or dated.group(1) < OWED_FROM:
        return
    for found in OWED_PARAGRAPH_RE.finditer(body[article:close]):
        plain = html.unescape(strip_tags(found.group(1)))
        handed = OWED_REVIEWER_READ_RE.search(plain)
        if handed:
            # The queued item's own case: on 11 October 2026 an entry said of an owed proof "I did not read: I
            # chose the induction first because ... the reviewer then read the transfer proof", and passed the
            # check by its "because".  A reviewer's reading is not the author's attempt.
            raise ValueError(f'The Owed attempt paragraph gives the reviewer\'s reading in place of the named '
                             f'attempt ("{handed.group(0)}"): give the result of your own reading, or report the '
                             'attempt unmade with what about the mathematics puts another first, and leave the '
                             'reviewer\'s reading to the Verification gate (AGENTS.md, Owed attempt)')
        procedural = OWED_UNMADE_RE.search(plain) and (OWED_PROCEDURAL_RE.search(plain)
                                                       or PROCEDURAL_REASON_RE.search(plain))
        if procedural:
            # Measured on 11 October 2026 on every notebook: of 109 Owed attempt paragraphs 2 give the reviewer's
            # reading and 25 more report the attempt unmade; of the 25, 14 have no reason word, 5 name a
            # procedure (a review's decision, the order chosen) and 6 pass.
            raise ValueError(f'The Owed attempt paragraph reports the named attempt unmade and gives a procedural '
                             f'reason ("{procedural.group(0)}"): say what about the mathematics, or the evidence, '
                             'puts another attempt first, or make it (AGENTS.md, Owed attempt)')
        verdict = OWED_UNMADE_RE.search(plain) and OWED_VERDICT_RE.search(plain)
        if verdict:
            # On 16 October 2026 an entry skipped the computation its item named, "it is vacuous", resting on a
            # remark in its own unreviewed proof; the reviewer found the remark false and the bound sharper.
            own = set((re.search(r'\bdata-claims="([^"]*)"', tag) or [None, ''])[1].split())
            if not set(CLAIM_ID_RE.findall(plain)) - own:
                raise ValueError(f'The Owed attempt paragraph leaves the named attempt unmade on a mathematical '
                                 f'verdict ("{verdict.group(0)}") that cites no claim of an earlier entry: an '
                                 "unreviewed remark of this entry is not evidence; make the attempt, or cite the "
                                 'registered claim that settles it (AGENTS.md, Owed attempt)')
        if OWED_UNMADE_RE.search(plain) and not OWED_REASON_RE.search(plain):
            raise ValueError('The Owed attempt paragraph reports the named attempt unmade, or made by the reviewer, '
                             'without the reason another came first: make the attempt, or say why it waits '
                             '(AGENTS.md, Owed attempt)')


def third_deferral_line(body, article, close):
    """A line for the finisher to print, or None: this entry's Owed attempt paragraph reports an attempt unmade,
    as those of the last two entries on its item did (tools/deferred_attempts.py).  A reading deferred three
    times held a published form of a period's main result.

    It prints and does not refuse.  The words cannot tell which attempt each entry defers: as a refusal it
    stopped an entry that made the attempt deferred twice and named a new one, and one of four recorded cases
    it would have refused was of that kind (a reviewer's finding, 11 October 2026)."""
    try:
        import deferred_attempts
    except ImportError:      # a checkout without the tool has nothing to print
        return None
    record = body.find('<section id="research-record"')
    earlier = deferred_attempts.ARTICLE.findall(body[record:article]) if record >= 0 else []
    tag = body[article:body.index('>', article) + 1]
    previous = deferred_attempts.third_deferral(earlier, tag, body[article:close])
    if not previous:
        return None
    return ('Deferred attempts: this entry reports an owed attempt unmade, as the last two entries on its item did '
            '(#' + ', #'.join(previous) + '). If one attempt is unmade in all three, make it or drop it with the '
            'reason; if they are different attempts, say in the Owed attempt paragraph which each entry left '
            '(AGENTS.md, Owed attempt).')


def validate_review_builds(body, article, close):
    """A review whose period (the entries on its route since the previous review, itself included) queued
    build items that are still queued, and which made fewer builds than remain queued from it, names each of
    them in a <p><strong>Builds.</strong> paragraph with what becomes of it: a queued check that is never
    built prevents nothing (reviewer, 11 October 2026: seven checks queued in one period, none built)."""
    tags = entry_tags(body, article)
    if tags['kind'] != 'review':
        return
    earlier = route_articles(body, article, tags['route'])
    start = next((position for position, _, kind, _ in reversed(earlier) if kind == 'review'), None)
    period = [(position, ident, end) for position, ident, _, end in earlier
              if start is None or position > start]
    own = re.search(r'\bid="([^"]+)"', body[article:body.index('>', article) + 1])
    period.append((article, own.group(1) if own else None, close))
    idents = {ident for _, ident, _ in period if ident}
    queue = QUEUE_SECTION_RE.search(body)
    # An item is of the period by the entry its source names (the entry's anchor, alone or leading the source's
    # words) or, where the source is given in words, by the record's last entry when the queue tool added it.
    # Measured on 11 October 2026 on one notebook: of 20 queued build items the exact match of the source alone
    # saw 10; one names an entry and goes on in words, and nine give words only.
    queued = [match.group(1) for match in QUEUED_ITEM_RE.finditer(queue.group(1) if queue else '')
              if queued_in(match.group(0), idents)]
    # Builds made in the period excuse the review only when they are at least as many as the builds it queued: one
    # build entry among several queued items would otherwise silence the check for all of them.
    built = sum(bool(BUILT_RE.search(body[position:end]) or BUILT_ENTRY_RE.search(body[position:end]))
                for position, _, end in period)
    if not queued or built >= len(queued):
        return
    paragraph = BUILDS_PARAGRAPH_RE.search(body, article, close)
    missing = [build for build in queued if paragraph is None or build not in paragraph.group(1)]
    if missing:
        raise ValueError('This review\'s period made fewer builds than remain queued from it: say in a '
                         '<p><strong>Builds.</strong> paragraph what becomes of each (built now, dropped, or '
                         'the dated reason it waits): ' + ', '.join(missing) + ' (AGENTS.md)')


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


def validate_test_disposition(body, article, value):
    """Require a reviewed operation/prediction or an explicit retained question.

    This checks the classification and evidence fields, not mathematical novelty.
    The existing reviewer audits whether the operation is more than a rewrite.
    """
    note = re.search(r'<strong>Test disposition\.</strong>(.*?)(?=<strong>|$)', value, re.S)
    kind = re.match(r'\s*(New operation|Retained exploratory)\b', note.group(1) if note else '')
    if not kind:
        raise ValueError('Decisive test needs Test disposition: New operation or Retained exploratory; '
                         'a rewritten parameterization is not a new test')
    if kind.group(1) == 'New operation':
        for label in ('Operation', 'Prediction'):
            field = re.search(r'<strong>' + label + r'\.</strong>(.*?)(?=<strong>|$)', value, re.S)
            plain = html.unescape(strip_tags(field.group(1))).strip() if field else ''
            if len(plain) < 40:
                raise ValueError(f'A new Decisive test needs {label} describing the actual operation '
                                 'and its distinguishing predicted outcomes; the reviewer checks their content')
        return
    earlier = set()
    for tag in re.finditer(r'<article\b([^>]*)>(.*?)</article>', body[:article], re.S):
        if (re.search(r'\bdata-kind="review"', tag.group(1))
                and '<strong>Decisive test.</strong>' in tag.group(2)):
            ident = re.search(r'\bid="([^"]+)"', tag.group(1))
            if ident:
                earlier.add(ident.group(1))
    links = set(re.findall(r'href=["\']#([^"\']+)["\']', note.group(1)))
    if not links.intersection(earlier):
        raise ValueError('A Retained exploratory test must link its earlier review after Test disposition; '
                         'another representation alone does not make it a new decisive operation')


def report_paragraph(text, label):
    found = re.search(r'<p\b[^>]*>\s*<strong>' + re.escape(label) + r'\.</strong>(.*?)</p>',
                      text, re.S)
    return found.group(1) if found else ''


def validate_nonvacuity(text):
    """An entry registering a finite check says, in its own paragraph, why the check could decide."""
    found = re.search(r'<strong>Nonvacuity\.</strong>(.*?)</p>', text, re.S)
    plain = html.unescape(strip_tags(found.group(1))).strip() if found else ''
    if len(plain) < 60:
        raise ValueError('An entry registering a finite check (an ex: claim) needs "<strong>Nonvacuity.</strong>" '
                         'with at least 60 characters: what recorded bounds give on the object at the sizes '
                         'computed, and why the outcomes that matter differ there (COMPUTATION_RULES.md, '
                         'numerical verification)')


VERDICT_RE = re.compile(r'<strong>\s*(?:Not decided|Decided)\.?\s*</strong>')


def require_report(text, label):
    value = report_paragraph(text, label)
    plain = html.unescape(strip_tags(value)).strip()
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
        else:
            evidence = report_paragraph(text, 'Architecture test')
            plain = html.unescape(strip_tags(evidence)).strip()
            if len(plain) >= 40 and re.search(r'<strong>(?:Not decided|Decided)\.</strong>', evidence):
                for reviewed_route, target in tuple(pending.items()):
                    if re.search(r'href=["\']#' + re.escape(target) + r'["\']', evidence):
                        pending.pop(reviewed_route)
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
    stakes = [html.unescape(strip_tags(found)).strip() for found in STAKES_RE.findall(text)]
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
    plain = html.unescape(strip_tags(read.group(1))).strip() if read else ''
    if len(plain) < 40:
        raise ValueError('An entry that closes a queue item says, after <strong>Sources read.</strong> and in at '
                         'least 40 characters, which statements of each source the closure relies on were read, '
                         'or that it relies on recorded results only (AGENTS.md)')
    if re.search(r'abstract(s)?\s+only|only\s+(the|its|their)\s+abstract|abstract,?\s+not\s+the', plain, re.I):
        raise ValueError('A closure may not rest on an abstract: read the statement of the theorem the closure '
                         'relies on, or keep the item open with the reading queued (AGENTS.md)')
    # Two closures drafted on 11 October 2026 covered the forms examined while the item named others (its
    # sources, a construction, a consequence); reviewers overturned both.  The author lists the remainder.
    left = re.search(r'<strong>Not examined\.</strong>((?:(?!</p>)(?!</li>).)*)', text, re.S)
    plain = html.unescape(strip_tags(left.group(1))).strip() if left else ''
    if len(plain) < 40 and not re.search(r'Closed:\s*merged into\b', text):
        raise ValueError('An entry that closes a queue item says, after <strong>Not examined.</strong> and in at '
                         'least 40 characters, what the item\'s own statement names (objects, sources, forms) that '
                         'the entry did not examine and why the closure stands without each, or that nothing it '
                         'names is left; an item with a named part unexamined is Continuing (AGENTS.md)')
    # On 11 October 2026 three closures of one item were drafted while the attempt its last reviewer had
    # named stayed unmade; each reviewer refused.  The closure accounts for that attempt in its own paragraph.
    owed = re.search(r'<strong>Owed attempt\.</strong>((?:(?!</p>)(?!</li>).)*)', text, re.S)
    plain = html.unescape(strip_tags(owed.group(1))).strip() if owed else ''
    if len(plain) < 40 and not re.search(r'Closed:\s*merged into\b', text):
        raise ValueError('An entry that closes a queue item says, after <strong>Owed attempt.</strong> and in at '
                         'least 40 characters, which attempt the item\'s latest follow-up or its reviewer named '
                         '(a run, a source, a proof) and that it was made, with its outcome, or that none was '
                         'named; an item whose named attempt is unmade is Continuing (AGENTS.md)')
    if closure_admits_unmade(plain) and not re.search(r'Closed:\s*merged into\b', text):   # a merge carries it
        raise ValueError('The closing entry\'s Owed attempt paragraph says an attempt is unmade or undecided: an '
                         'item whose named attempt is unmade is Continuing (AGENTS.md); make it, or continue')
    missing = unlisted_limits(text)
    if missing and not re.search(r'Closed:\s*merged into\b', text):
        raise ValueError('The closing entry declares limits of its own work (' + ', '.join(missing) + ') that its '
                         '<strong>Not examined.</strong> paragraph does not quote: say there, in the same words, '
                         'why the closure stands with each, or remove the limit by doing the work (AGENTS.md)')


# A fifth closure of that item rested on a bound with a free parameter, "by this count", sent to closure without
# its optimum, and on an example "not sought"; its reviewer found both.  A closing entry's own declared limits
# are quoted in its Not examined paragraph.
DECLARED_LIMIT_RE = re.compile(r'\bby this count\b|\bnot sought\b|\bdid not search\b|\bnot the exact reach\b', re.I)
NOT_EXAMINED_RE = re.compile(r'<strong>Not examined\.</strong>((?:(?!</p>)(?!</li>).)*)', re.S)


def unlisted_limits(text):
    """The self-declared limits of an entry's body that none of its Not examined paragraphs quotes."""
    plain = lambda fragment: html.unescape(strip_tags(fragment)).lower()
    listed = ' '.join(plain(found) for found in NOT_EXAMINED_RE.findall(text))
    declared = {found.lower() for found in DECLARED_LIMIT_RE.findall(plain(NOT_EXAMINED_RE.sub(' ', text)))}
    return sorted(limit for limit in declared if limit not in listed)


# A fourth closure of that item, drafted the same day, said "None is left unmade except" one attempt, with an
# excuse covering one family; its reviewer refused it.  A closing paragraph may not carry such an exception.
CLOSURE_EXCEPTION_RE = re.compile(r'\bunmade except\b|\bexcept\b[^.]*\b(?:unmade|undecided|not decided|not made)\b|'
                                  r'\b(?:is|are|stays?|left) (?:undecided|not decided|unmade)\b|\bnot made\b', re.I)


def closure_admits_unmade(plain):
    """Whether a closing entry's Owed attempt text reports an attempt unmade or undecided."""
    denied = re.sub(r'\b(?:none|nothing|no attempt)\b[^.]*?\bunmade\b(?!\s+except\b)', ' ', plain, flags=re.I)
    return bool(CLOSURE_EXCEPTION_RE.search(denied))


NOTHING_BEST_RE = re.compile(r"\bnothing (?:at|for) the goal|\bnothing for the family statement|"
                             r"\bneither gives a candidate", re.I)
# Closed and Developed both remove the item: an entry that removed a built item as Developed was refused as
# closing none (11 October 2026)
CLOSED_FOLLOW_UP_RE = re.compile(r'<strong>Follow-up\.</strong>\s*(?:Closed|Developed)\b')
DEVELOPED_RE =re.compile(r'<strong>Follow-up\.</strong>\s*Developed\b')
UNREAD_CORRECTIONS = re.compile(r'\b(?:did|has) not (?:read|seen?) (?:the|my|these|those|its) (?:last |later )?'
                                r'(?:corrections|changes|code as changed)'
                                r'|\bnot shown to (?:it|him|her|them|the reviewer)(?: again)?\b', re.I)


def validate_corrections_read(text):
    """A removal the reviewer has not seen as corrected is not yet reviewed.

    On 11 October 2026 three entries in a row of one notebook removed a build item while their gates said the
    reviewer "did not read the corrections", which in two of them rewrote the code the reviewer had read; the
    stand-in review objected.  Of 2149 recorded research entries with a gate, those three say so, and all three
    are removals.  The follow-up with the same reviewer exists for this."""
    if not (CLOSED_RE.search(text) or DEVELOPED_RE.search(text)):
        return
    gate = html.unescape(strip_tags(report_paragraph(text, 'Verification gate')))
    found = UNREAD_CORRECTIONS.search(gate)
    if found:
        raise ValueError(f'This entry removes a queue item and its Verification gate says the reviewer '
                         f'"{found.group(0)}": send the corrected draft and code to the same reviewer in a '
                         'follow-up and report its answer, or keep the item Continuing (AGENTS.md, one focused '
                         'correctness review)')


def validate_developed_removals(text):
    """A Developed follow-up removes its item as a Closed one does, and accounts for it the same way.

    On 11 October 2026 three drafts in two blocks removed queue items as Developed, where the paragraphs of a
    closure were not asked: one after four lines of the queuing entry had been read, one dropping parts the
    item's previous entry had listed as not examined, one whose queued case was unresolved; a reviewer refused
    each.  So an entry with a Developed follow-up says, after <strong>Not examined.</strong>, what the item names
    that it did not examine, and after <strong>Owed attempt.</strong>, what became of the attempt its last
    follow-up named, and links the reviewer's record."""
    if not DEVELOPED_RE.search(text):
        return
    for label, what in (('Not examined', 'what the item\'s own statement and its previous entry\'s list name that '
                         'this entry did not examine, and why the removal stands without each, or that nothing '
                         'is left'),
                        ('Owed attempt', 'which attempt the item\'s latest follow-up named and that it was made, '
                         'with its outcome, or that none was named')):
        found = re.search(rf'<strong>{label}\.</strong>((?:(?!</p>)(?!</li>).)*)', text, re.S)
        plain = html.unescape(strip_tags(found.group(1))).strip() if found else ''
        if len(plain) < 40:
            raise ValueError(f'An entry that removes a queue item as Developed says, after <strong>{label}.</strong> '
                             f'and in at least 40 characters, {what}; an item with a named part unexamined or a '
                             'named attempt unmade is Continuing (AGENTS.md)')
    if not re.search(r'href="[^"]*review[^"/]*\.txt"', text):
        raise ValueError('An entry that removes a queue item as Developed links the reviewer\'s record '
                         '(review.txt): the reviewer reads every removal (AGENTS.md)')


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
        if not READING_ASK_RE.search(html.unescape(strip_tags(asked))):
            continue
        item = asked + outcome
        read = re.search(r'<strong>Sources read\.</strong>((?:(?!<strong>Follow-up\.</strong>).)*)', item, re.S)
        if not read:                      # also accepted after the follow-up, inside the same item
            read = re.search(r'<strong>Sources read\.</strong>(.*)', outcome, re.S)
        plain = html.unescape(strip_tags(read.group(1))).strip() if read else ''
        if len(plain) < 40:
            raise ValueError('A sub-idea that asks for a reading is marked Developed: say in that list item, after '
                             '<strong>Sources read.</strong> and in at least 40 characters, which statement was '
                             'read in its text (AGENTS.md; a check was marked resolved on memory, 11 October 2026)')
        if UNREAD_RE.search(plain):
            raise ValueError('A reading check may not be Developed on memory, an abstract or a report: read the '
                             'statement in its text, or keep the sub-idea Continuing (AGENTS.md)')


def validate_structural_reason(text, statuses=(), claims=()):
    """An entry reporting a counterexample or a refutation of a hypothesis says why it works.

    AGENTS.md asks that an exclusion's structural reason be extracted and tried on the other candidates.  Two
    entries of 11 October 2026 reported counterexamples to a hypothesis without it, and the reason, that 1 was
    a constant-coefficient combination of the rows, was drawn only by a reviewer two entries later.  The
    trigger is the word counterexample in the title or the New mathematics paragraph, or a claim registered as
    a refutation, or a claim whose identifier is an obstruction's (obs:); "refutation" alone is not one, being
    the name of a proof in this subject."""
    title = re.search(r'<h3\b[^>]*>(.*?)</h3>', text, re.S)
    told = (title.group(1) if title else '') + ' ' + report_paragraph(text, 'New mathematics')
    obstruction = any(str(cid).startswith('obs:') for cid in claims)
    if 'refutation' not in statuses and not obstruction and not re.search(r'\bcounterexamples?\b', told, re.I):
        return
    given = re.search(r'<strong>Structural reason\.</strong>((?:(?!</p>)(?!</li>).)*)', text, re.S)
    plain = html.unescape(strip_tags(given.group(1))).strip() if given else ''
    if len(plain) < 60:
        raise ValueError('This entry reports a counterexample or registers a refutation: say, after '
                         '<strong>Structural reason.</strong> and in at least 60 characters, why it works and to '
                         'which other candidates or hypotheses the reason applies (AGENTS.md)')


def logged_searches(root, since):
    """The registry searches tools/search-claims.py logged at or after `since` (unix seconds)."""
    path = Path(root) / 'research/logs/claim-searches.jsonl'
    found = []
    for line in path.read_text().splitlines() if path.exists() else ():
        try:
            row = json.loads(line)
        except ValueError:
            continue
        if row.get('unix_s', 0) >= since:
            found.append(row.get('query', ''))
    return found


def validate_searches_run(entry, queries):
    """An entry that reports a record search was written in a session that ran one.

    An entry of 11 October 2026 said the registry had been searched for a family and held nothing on it; no
    such search had been run, and the registry held a ceiling for that family.  The check cannot tell whether
    the searches run are the ones the paragraph reports: it returns them, for the finisher to print."""
    if '<strong>Record search.</strong>' in entry and not queries:
        raise ValueError('This entry has a <strong>Record search.</strong> paragraph, and tools/search-claims.py '
                         'was not run in its session: run the searches the paragraph reports, and correct the '
                         'paragraph by what they return (AGENTS.md)')
    return queries


# The words that name an attempt: long enough to carry content, and not the paragraph's own frame.
ATTEMPT_FRAME = {'attempt', 'search', 'searches', 'searched', 'returned', 'record', 'registry', 'which', 'their',
                 'there', 'these', 'those', 'where', 'whose', 'about', 'after', 'before', 'nothing', 'stating',
                 'states', 'statement', 'entry', 'next', 'first'}


def attempt_words(text):
    """The content words of `text`, lower case, of five letters or more, without the frame words."""
    return {word for word in re.findall(r'[a-z][a-z-]{4,}', text.lower()) if word not in ATTEMPT_FRAME}


def validate_next_attempt_search(entry, queries):
    """An entry whose Record search says what was searched for its next attempt ran a search for it.

    Twice on 16 October 2026 a Record search paragraph said a search for the next attempt had returned
    nothing before any such search had run; validate_searches_run passed, as other searches had. The sentence
    naming the next attempt must share two content words with one search logged in the session."""
    found = re.search(r'<strong>Record search\.</strong>(.*?)</p>', entry, re.S)
    if not found:
        return
    plain = html.unescape(strip_tags(found.group(1)))
    for sentence in re.split(r'(?<=[.;])\s+', plain):
        if 'next attempt' not in sentence.lower():
            continue
        wanted = attempt_words(sentence)
        if wanted and not any(len(wanted & attempt_words(query)) >= 2 for query in queries):
            raise ValueError('The Record search names a next attempt that no search of this session matches: '
                             f'"{" ".join(sentence.split())[:200]}". Run tools/search-claims.py with words of that '
                             'attempt, and report what it returned (AGENTS.md)')


def count_listing_report(entry, queries):
    """A line for the finisher to print, or None: the entry holds sentences with a count and the draft tool,
    which lists them for reading beside their sources, logged no run on it in the session.

    It reports and does not refuse: a refusal would be met by running the tool without reading its listing, and
    the line makes the omission visible in the finisher's output, where the session reviewer reads it.  It cannot
    tell whether a listing that was printed was read."""
    ident = re.search(r'<article\b[^>]*\bid="([^"]+)"', entry)
    if not ident:
        return None
    try:
        import draft_claim_sentences
    except ImportError:      # a checkout without the draft tool has no listing to report on
        return None
    found = len(draft_claim_sentences.counts(entry + '</article>'))
    runs = [query.split() for query in queries if query.startswith('draft_counts ')]
    listed = [int(words[2]) for words in runs if words[1:2] == [ident.group(1)] and words[2:3] and words[2].isdigit()]
    if not found or (listed and listed[-1] >= found):
        return None
    if listed:      # run on an earlier draft: the gate and the assessments, with their counts, came after
        return (f'Count listing: tools/draft_claim_sentences.py last listed {listed[-1]} sentences with a count for '
                f'this entry and it now holds {found}; run it again and read the new ones beside their saved '
                'sources (AGENTS.md).')
    return (f'Count listing: tools/draft_claim_sentences.py logged no run on this entry in its session, and {found} '
            'of its sentences hold a count; run it on the entry and read each beside its saved source (AGENTS.md).')


TEST_PARTS = ('Prediction', 'Power', 'Attempt')
CLAIM_ID_RE = re.compile(r'\b(?:lem|thm|prop|cor|conj|obs|imp|ex|audit|check|ctx|def|criterion|q|rem|open|'
                         r'third-party):[A-Za-z0-9]+(?:-[A-Za-z0-9]+)*')


def cited_summaries(index, claims):
    """{claim: summary} for the named claims, read from the registry's text without parsing all of it (parsing
    the whole registry took 0.3 s at 4938 claims, a third of the start guidance's budget).

    It relies on the registry's layout: the claim objects come before the relationships, so an id's first
    occurrence is its claim, and that object's "summary" comes before the next object's "id"; checked against a
    full parse for all 4938 claims on 16 October 2026."""
    raw = index.read_text() if index.exists() else ''
    decoder, found = json.JSONDecoder(), {}
    for claim in claims:
        at = raw.find(f'"id": "{claim}"')
        start = raw.find('"summary": ', at) if at >= 0 else -1
        following = raw.find('"id": "', at + 1)
        if start >= 0 and (following < 0 or start < following):    # the summary of this object, not the next
            found[claim] = decoder.raw_decode(raw, start + len('"summary": '))[0]
    return found


DRAFT_ASSESSMENT = re.compile(r'^\s*(?:PENDING|TODO|TBD|PLACEHOLDER)\b', re.I)


def validate_assessments_filled(index, claims):
    """The entry's declared claims carry a filled assessment in the registry, not a draft placeholder.

    On 16 October 2026 a route review found three working-proof claims registered that day still assessed
    "PENDING": the specs were registered before their reviews, and the finisher checked the status only."""
    raw = index.read_text() if index.exists() else ''
    decoder, drafts = json.JSONDecoder(), []
    for claim in claims:
        at = raw.find(f'"id": "{claim}"')
        start = raw.find('"assessment": ', at) if at >= 0 else -1
        following = raw.find('"id": "', at + 1)
        if start >= 0 and (following < 0 or start < following):
            if DRAFT_ASSESSMENT.match(decoder.raw_decode(raw, start + len('"assessment": '))[0]):
                drafts.append(claim)
    if drafts:
        raise ValueError('Claims of this entry still carry a draft assessment in the registry: ' + ', '.join(drafts)
                         + '. Write the assessment from the review record in the spec and rebuild with '
                         'tools/claim_refresh.py (AGENTS.md, index maintenance)')


def next_attempt_neighbours(body, entry, index, last=10, least=4, shown=3):
    """Lines naming the claims of the notebook's last `last` entries whose registered summaries share at least
    `least` content words with the entry's next attempt, nearest first, to read before the attempt is kept.

    Twice on 16 October 2026 an entry named a next attempt that a lemma registered earlier the same day already
    decided; the record search for it had run and returned other claims, and the deciding lemma was the
    session's own. It reports and does not refuse: whether a claim answers an attempt needs reading."""
    follow = re.findall(r'<strong>Follow-up\.</strong>((?:(?!</p>).)*)', entry, re.S)
    plain = html.unescape(strip_tags(follow[-1])) if follow else ''
    at = plain.lower().find('next attempt')
    if at < 0:
        return []
    wanted = attempt_words(plain[at:])
    tags = re.findall(r'<article\b[^>]*>', body[:body.rfind('<article')])[-last:]
    claims = [c for tag in tags for c in (re.search(r'\bdata-claims="([^"]*)"', tag) or [None, ''])[1].split()
              if c != 'none']
    scored = sorted(((len(wanted & attempt_words(summary)), claim)
                     for claim, summary in cited_summaries(index, claims).items()), reverse=True)
    near = [f'{claim} ({score} words)' for score, claim in scored if score >= least][:shown]
    return ([f'Next attempt: recent claims nearest to it, to read before keeping it (one may already decide it): '
             f'{", ".join(near)}.'] if near else [])


def review_test_context(body, target, summaries=None, width=400):
    """Lines giving what a review already decided about the test it poses: its Decision paragraph, the
    Prediction, Power and Attempt of its Decisive test, and the registered statements of the claims those cite.

    On 16 October 2026 one draft listed as open a case the linked review's Power paragraph decides, and another
    rediscovered a lemma the review's Decision paragraph names; both quoted only the Prediction."""
    at = body.find(f'<article id="{target}"')         # a plain search: a regex over the whole record took 0.3 s
    end = body.find('</article>', at) if at >= 0 else -1
    if end < 0:
        return []
    text = body[at:end]
    plain = lambda fragment: re.sub(r'\s+', ' ', html.unescape(strip_tags(fragment))).strip()
    parts = [('Decision', report_paragraph(text, 'Decision'))]
    test = report_paragraph(text, 'Decisive test')
    for label in TEST_PARTS:
        part = re.search(r'<strong>' + label + r'\.</strong>(.*?)(?=<strong>[A-Z][\w ]*\.</strong>|$)', test, re.S)
        parts.append((label, part.group(1) if part else ''))
    lines = [f'What #{target} already says about its test (read before treating a case as open):']
    for label, fragment in parts:
        if fragment:
            lines.append(f'  {label}. {plain(fragment)}')
        elif test or label == 'Decision':     # a review without a Decisive test has none of its parts
            lines.append(f'  {label}: not found in #{target} under that label; read the review itself.')
    cited = dict.fromkeys(CLAIM_ID_RE.findall(plain(parts[0][1]) + ' ' + plain(dict(parts)['Power'])))
    if summaries is None and cited:
        summaries = cited_summaries(ROOT / 'research/claims/index.json', cited)
    for claim in cited:
        if claim in summaries:
            statement = summaries[claim]
            lines.append(f'  {claim}: {statement if len(statement) <= width else statement[:width] + "…"}')
    return lines if len(lines) > 1 else []


def architecture_context_report(body, entry):
    """Lines for the finisher to print: the context of each review the entry's Architecture test links."""
    evidence = report_paragraph(entry + '</article>', 'Architecture test')
    lines = []
    for target in dict.fromkeys(re.findall(r'href=["\']#([^"\']+)["\']', evidence)):
        at = body.find(f'<article id="{target}"')
        if at >= 0 and 'data-kind="review"' in body[at:body.find('>', at)]:     # linked research entries: none
            lines += review_test_context(body, target)
    return lines


def decided_report(entry):
    """Lines for the finisher to print, or none: the entry reports its Architecture test Decided and its body
    has sentences that hedge (in outline, not verified, not checked and the like).

    On 11 October 2026 a draft reported a test decided on an outline whose later steps it called unverified,
    and the reviewer caught it.  The words cannot tell whether a hedge is about the decided matter, so this
    prints the two side by side and refuses nothing.  Measured with tools/outcome_ahead.py --decided on one
    notebook: one recorded entry of 62 and two first drafts of 64 are flagged, that draft among them."""
    try:
        import outcome_ahead
    except ImportError:      # a checkout without the listing has nothing to print
        return []
    lines = outcome_ahead.report(entry + '</article>', status_line=False)
    return (['Decided and hedged: this entry reports its Architecture test Decided and hedges elsewhere; read '
             'each hedge beside the report and say in the entry which matter it is about:'] + lines) if lines else []


def absence_report(entry):
    """Lines for the finisher to print, or none: the sentences of an entry that closes or develops its item
    which say something is not kept, not recorded or gone (tools/absence_claims.py).

    The words cannot tell a statement about the repository from one about mathematics, so this prints and
    refuses nothing.  The figures of its measurement on one notebook are in the entry that built it
    (11 October 2026); of four statements about the tree checked there, one was false."""
    try:
        import absence_claims
    except ImportError:      # a checkout without the listing has nothing to print
        return []
    lines = absence_claims.report(entry)
    return (['Absence claims: this entry removes its item and says something is not kept, not recorded or '
             'gone; check each that is about the repository against the tree and the session transcript:']
            + lines) if lines else []


def hook_notice_lines(root, since):
    """Lines for the finisher to print, or none: the post-commit hook's notices at or after `since` that no
    answer followed (tools/hook_notices.py).  It prints and refuses nothing, and a failure to read the log
    prints nothing rather than stopping the checkpoint.  With --next the session starts before the commit of
    the entry it follows, so that commit's notice is in its window; without --next it is in no window."""
    try:
        import hook_notices
        return hook_notices.report(root, since)
    except Exception:
        return []


def validate_resemblance_run(entry, queries):
    """An entry that declares claims was written in a session that ran tools/claim_resemblance.py on each.

    An entry of 11 October 2026 presented a corollary as what a comparison added; a registered claim had it
    in a weaker form, found by the reviewer, and the tool had been run only after the review.  The check
    cannot tell when in the session the tool was run, nor whether its output was read."""
    declared = re.search(r'<article\b[^>]*\bdata-claims="([^"]*)"', entry)
    idents = [] if not declared or declared.group(1).strip() == 'none' else declared.group(1).split()
    compared = {word for query in queries if query.startswith('claim_resemblance ') for word in query.split()[1:]}
    missing = [ident for ident in idents if ident not in compared]
    if missing:
        raise ValueError('This entry declares claims that tools/claim_resemblance.py was not run on in its '
                         'session: ' + ', '.join(missing) + '. Run it on the draft spec, read the nearest '
                         'registered claims, and correct what the entry says is new (AGENTS.md)')


PROVED = {'working_proof', 'conditional'}


def validate_degenerate_cases(text, statuses=()):
    """An entry registering a proved statement says what the statement gives on degenerate inputs.

    Two theorems of 11 October 2026 were false as first drafted for want of a hypothesis, unsatisfiability in
    one and multilinear blocks in the other; each fails on the first degenerate input one writes down, and a
    reviewer found both.  The paragraph is asked of the author before the review."""
    if not PROVED & set(statuses):
        return
    given = re.search(r'<strong>Degenerate cases\.</strong>((?:(?!</p>)(?!</li>).)*)', text, re.S)
    plain = html.unescape(strip_tags(given.group(1))).strip() if given else ''
    if len(plain) < 60:
        raise ValueError('This entry registers a proved statement: say, after <strong>Degenerate cases.</strong> '
                         'and in at least 60 characters, what the statement gives on a satisfiable system, an '
                         'empty one and an input outside its stated form, or which hypothesis excludes each '
                         '(AGENTS.md)')


SMALLEST_FROM = '2026-10-16'


def validate_smallest_case(text):
    """An entry whose Continuing follow-up names a next attempt says what that attempt gives on its smallest case.

    On 16 October 2026 four entries in a row named a next attempt that their reviewer, or the next entry,
    decided in a few lines at its smallest instance; the rule to try it first was written and not applied."""
    dated = re.search(r'\bid="entry-(\d{4}-\d{2}-\d{2})', text)
    if not dated or dated.group(1) < SMALLEST_FROM:
        return
    follow = re.search(r'<strong>Follow-up\.</strong>((?:(?!</p>).)*)', text, re.S)
    plain = html.unescape(strip_tags(follow.group(1))) if follow else ''
    if not re.match(r'\s*Continuing', plain) or not re.search(r'\bnext attempt\b', plain, re.I):
        return
    given = re.search(r'<strong>Smallest case\.</strong>((?:(?!</p>)(?!</li>).)*)', text, re.S)
    said = html.unescape(strip_tags(given.group(1))).strip() if given else ''
    if len(said) < 40:
        raise ValueError('This entry names a next attempt: say, after <strong>Smallest case.</strong> and in at '
                         'least 40 characters, what the attempt gives on its smallest nontrivial instance, tried '
                         'before naming it, or why that instance does not decide it (AGENTS.md, next attempts)')


BASELINE_FROM = '2026-10-16'


def validate_baseline(text, statuses=()):
    """An entry registering a proved statement compares it with the construction or bound that needs no idea.

    A lemma of 16 October 2026 compared an exact degree with Pang's criterion and called the criterion's miss a
    calibration; the reviewer found that the obvious multiplier, the indicator of the origin, already survived
    for every choice, so what the lemma added was a saving of t degrees, not the existence the draft implied."""
    if not PROVED & set(statuses):
        return
    dated = re.search(r'\bid="entry-(\d{4}-\d{2}-\d{2})', text)
    if not dated or dated.group(1) < BASELINE_FROM:
        return
    given = re.search(r'<strong>Baseline\.</strong>((?:(?!</p>)(?!</li>).)*)', text, re.S)
    plain = html.unescape(strip_tags(given.group(1))).strip() if given else ''
    if len(plain) < 40:
        raise ValueError('This entry registers a proved statement: say, after <strong>Baseline.</strong> and in '
                         'at least 40 characters, the trivial construction or bound the statement improves on '
                         '(the witness or estimate that needs no idea) and what it adds over it, or why none '
                         'exists (AGENTS.md)')


DRAFT_PROOF = re.compile(r'<strong>(?![^<]*\b(?:sketch|attempt)\b)[^<]{0,40}\b[Pp]roof\b[^<]{0,40}\.</strong>')
NOT_PROVED_STATUS = re.compile(r'<p class="entry-meta">\s*(?:Refutation|Finite check|Conjecture)', re.I)


def draft_statuses(text, known=None):
    """The statuses a draft's claims stand for at drafting, before registration: the registered statuses of
    its declared claims where they are registered (`known`, a map from claim id), and otherwise
    {'working_proof'} when it has a proof paragraph ("Proof.", "Proof of (b).", "Full proof.", not a sketch or
    an attempt), unless it declares data-claims="none" or its status line opens with Refutation, Finite check or
    Conjecture, which the finisher's registry path would not count as proved. The append path omits `known`,
    registration waiting for the finisher."""
    declared = re.search(r'\bdata-claims="([^"]*)"', text)
    ids = declared.group(1).split() if declared else []
    # The append path does not read the registry (registration waits for the finisher), so finite checks are
    # told by their declared prefixes, as cases_only does.
    if ids == ['none'] or NOT_PROVED_STATUS.search(text) or (ids and all(i.startswith(FINITE_PREFIXES) for i in ids)):
        return set()
    registered = {known[cid] for cid in ids if known and cid in known}
    if registered:
        return registered
    return {'working_proof'} if DRAFT_PROOF.search(text) else set()


def validate_drafted_proofs(text, drafted):
    """The checks of proved statements that the registry path runs, run on a draft with `drafted` statuses."""
    validate_plainest(text, drafted)
    if drafted & PROVED:
        validate_degenerate_cases(text, drafted)
        validate_hypothesis_steps(text, drafted)
        validate_baseline(text, drafted)


PLAINEST_FROM = '2026-10-16'
TRIED_FROM = '2026-10-16'
UNDECIDED = re.compile(r'\b(?:none applies|no recorded result|neither decides|nothing applies|no plain bound)\b', re.I)
PLAINEST_RE = re.compile(r'<strong>Plainest bound\.</strong>((?:(?!</p>)(?!</li>).)*)', re.S)


def validate_plainest(text, statuses=()):
    """A next attempt's smallest case, and a registered proof's witness, are checked against the plainest bound.

    On 16 October 2026 a review's computation, a lemma's witness and a next attempt (entropy chaining) each
    concerned instances that a bare count already decided: per-cell point counts settled the bands the chaining
    was to bound, and the witness was elementary; rules and a reviewer audit caught them only afterwards.  Each
    paragraph says, after <strong>Plainest bound.</strong>, what the plainest available bound (a bare count, a
    one-dimensional estimate, the record's oldest lemma) gives on its instance, or why none applies."""
    dated = re.search(r'\bid="entry-(\d{4}-\d{2}-\d{2})', text)
    if not dated or dated.group(1) < PLAINEST_FROM:
        return
    for label, required in (('Smallest case', True), ('Nonvacuity', bool(PROVED & set(statuses)))):
        # to the paragraph's end, past any list inside it (16 October 2026: a list hid the label twice)
        given = re.search(rf'<strong>{label}\.</strong>((?:(?!</p>).)*)', text, re.S)
        if not (given and required):
            continue
        said = re.search(r'<strong>Plainest bound\.</strong>((?:(?!</p>).)*)', given.group(0), re.S)
        if not said or len(html.unescape(strip_tags(said.group(1))).strip()) < 30:
            raise ValueError(f'The {label} paragraph needs, after <strong>Plainest bound.</strong> and in at least '
                             '30 characters, what the plainest available bound (a bare count, a one-dimensional '
                             'estimate, the record\'s oldest applicable lemma) gives on its instance, or why none '
                             'applies: an instance the plain bound decides tests nothing (AGENTS.md)')
        if dated.group(1) >= TRIED_FROM and UNDECIDED.search(html.unescape(strip_tags(said.group(1)))) \
                and '<strong>Tried.</strong>' not in said.group(1):
            # 16 October 2026: a Plainest bound said "no recorded result gives" one, beside no attempt; the entry's
            # own substitution step with a recorded tradeoff gave a stronger bound than its theorem.
            raise ValueError(f'The {label} paragraph\'s Plainest bound says none decides or applies: say after '
                             '<strong>Tried.</strong> which plain bounds were tried on the instance, the entry\'s '
                             'own proof steps used alone among them, and what each gave (AGENTS.md: "None applies" '
                             'is written only after the plainest bound was tried)')
    # 16 October 2026: three named next attempts in a row were decided by the naming entry's own statements,
    # found by its reviewer.  The Smallest case says what those statements give on the attempt.
    whole = re.search(r'<strong>Smallest case\.</strong>(.*?)</p>', text, re.S)
    if whole and dated.group(1) >= OWN_FROM:
        own = re.search(r'<strong>Own statements\.</strong>(.*)', whole.group(1), re.S)
        if not own or len(html.unescape(strip_tags(own.group(1))).strip()) < 30:
            raise ValueError('The Smallest case paragraph needs, after <strong>Own statements.</strong> and in at '
                             'least 30 characters, what this entry\'s own statements (its lemmas applied variable by '
                             'variable, coordinate by coordinate, at the attempt\'s parameters) give on the named '
                             'attempt: an attempt they decide is the next lemma, not a next attempt (AGENTS.md)')


OWN_FROM = '2026-10-17'


N_UPPER_RE = re.compile(r'\\log\\log N\s*\\le\s*\d|\\log N\s*\\le\s*\d|(?<![\w\\])N\s*\\le\s*\d')


def validate_unbounded_witness(text):
    """A Nonvacuity paragraph does not bound N from above: its witness must work at every large N.

    On 16 October 2026 a witness's cost was at most 2 only "for N with 4 log log N <= 4096", which the draft's
    recheck passed and its reviewer caught: a statement about all large N needs a witness at unbounded N.  On
    the record's 376 Nonvacuity paragraphs of that day the pattern matched none."""
    given = re.search(r'<strong>Nonvacuity\.</strong>((?:(?!</p>)(?!</li>).)*)', text, re.S)
    found = N_UPPER_RE.search(given.group(1)) if given else None
    if found:
        raise ValueError(f'The Nonvacuity paragraph bounds N from above ("{found.group(0)}"): a witness of a '
                         'statement about all large N must satisfy the hypotheses at unbounded N; choose its '
                         'parameters so that every constraint holds as N grows (AGENTS.md)')


def validate_proved_instance(text, statuses=()):
    """An entry registering a proved statement exhibits an input that satisfies its hypotheses.

    A proposition of 11 October 2026 went to review stated for a class with no member (fewer right vertices
    than left ones, with right degrees bounded by the left degree); writing one instance down shows it."""
    if not PROVED & set(statuses):
        return
    given = re.search(r'<strong>Nonvacuity\.</strong>((?:(?!</p>)(?!</li>).)*)', text, re.S)
    plain = html.unescape(strip_tags(given.group(1))).strip() if given else ''
    if len(plain) < 60:
        raise ValueError('This entry registers a proved statement: exhibit, after <strong>Nonvacuity.</strong> '
                         'and in at least 60 characters, an input that satisfies all its hypotheses, with its '
                         'parameters, or say that the statement has no hypotheses to satisfy (AGENTS.md)')


def validate_hypothesis_steps(text, statuses=()):
    """An entry registering a proved statement names, for each hypothesis, the step of the proof that uses it.

    AGENTS.md asked for this from 16 October 2026 with no check; the same day two entries stated conclusions for
    a wider class than their proofs covered (every idempotent where the proof used span generators, every field
    where it used 0/1-valued killers), which naming each hypothesis's step would have shown."""
    if not PROVED & set(statuses):
        return
    given = re.search(r'<strong>Hypotheses, each with its step\.</strong>((?:(?!</p>)(?!</li>).)*)', text, re.S)
    plain = html.unescape(strip_tags(given.group(1))).strip() if given else ''
    # A paragraph holding a list continues past its first item, which may be short.
    opened = re.search(r'<strong>Hypotheses, each with its step\.</strong>\s*<ul>(.*?)</ul>', text, re.S)
    if opened:
        plain = html.unescape(strip_tags(opened.group(1))).strip()
    if len(plain) < 60:
        raise ValueError('This entry registers a proved statement: name, after <strong>Hypotheses, each with its '
                         'step.</strong> and in at least 60 characters, the step of the proof that uses each '
                         'hypothesis and the weakest form that step needs, and the class each conclusion holds '
                         'for (AGENTS.md)')
    # 16 October 2026: a part added to a Statement after review kept hypotheses copied from its instance and
    # was missing from this paragraph.  Each lettered part of the Statement is named here.
    dated = re.search(r'\bid="entry-(\d{4}-\d{2}-\d{2})', text)
    statement = re.search(r'<strong>Statement\.</strong>((?:(?!</p>).)*)', text, re.S)
    if dated and dated.group(1) >= PARTS_FROM and statement:
        parts = dict.fromkeys(re.findall(r'(?<![\w\\])\(([a-h])\)\s', html.unescape(strip_tags(statement.group(1)))))
        # the whole paragraph, list items included (16 October 2026: a list hid parts named after its first item)
        whole = re.search(r'<strong>Hypotheses, each with its step\.</strong>(.*?)</p>', text, re.S)
        named = html.unescape(strip_tags(whole.group(1))) if whole else plain
        missing = [p for p in parts if f'({p})' not in named and f'Part ({p})' not in named]
        if len(parts) >= 2 and missing:
            raise ValueError('The Statement has parts ' + ', '.join(f'({p})' for p in parts) + ' and the Hypotheses '
                             'paragraph names none of ' + ', '.join(f'({p})' for p in missing) + ': say which '
                             'hypotheses each part uses, read off its proof, not copied from an instance '
                             '(AGENTS.md)')


    # 16 October 2026: a bullet "m > N: the system of Theorem 2.9" named a source's setting where a proof step
    # belonged, and the hypothesis, used by no step, stayed in the lemma.  A bullet's step is a step.
    whole = re.search(r'<strong>Hypotheses, each with its step\.</strong>\s*<ul>(.*?)</ul>', text, re.S)
    if dated and dated.group(1) >= PARTS_FROM and whole:
        for item in re.findall(r'<li>(.*?)</li>', whole.group(1), re.S):
            said = html.unescape(strip_tags(item))
            step = said.split(':', 1)[1] if ':' in said else ''
            if SOURCE_SETTING.match(step):
                raise ValueError('A Hypotheses bullet names a source\'s setting, not a step of this proof: "'
                                 + said.strip()[:120] + '". Name the step that uses the hypothesis and the weakest '
                                 'form it needs, or say no step uses it and drop it (AGENTS.md)')


# a hypothesis "justified" by where it came from rather than by a step that uses it
SOURCE_SETTING = re.compile(r'\s*(?:it is |as in )?(?:the )?(?:system|setting|statement|hypothes[ie]s|assumptions?|'
                            r'standing assumptions?) (?:of|in|from) ', re.I)
PARTS_FROM = '2026-10-16'
INSTANCE_CHECK_FROM = '2026-10-16'
# a relation between two numbers, in TeX or plain text: "3\le4", "2 < 3", "4=4"
NUMERIC_RELATION = re.compile(r'\d\s*(?:\\le|\\ge|\\leq|\\geq|\\lt|\\gt|<|>|=|≤|≥)\s*\d')


SCOPE_VERB = re.compile(r'\b(?:weaken(?:ed|s|ing)?|narrow(?:ed|s|ing)?|strengthen(?:ed|s|ing)?|restrict(?:ed|s)?)\b',
                        re.I)
SCOPE_DIRECTION = re.compile(r'\bmore general\b|\bless general\b|\bgeneraliz|\bnarrower\b|\bwider\b|\bassumes? less\b|'
                             r'\bassumes? more\b|\bsame scope\b|\bbecause (?:it was |they were )?false\b', re.I)


def validate_scope_direction(text):
    """A Verification gate that reports hypotheses or statements weakened, narrowed or strengthened says which
    way the statement's scope moved.  On 16 October 2026 'soundness and killing weakened' meant weaker
    hypotheses, a more general lemma, and the user read it as a free generalization thrown away."""
    dated = re.search(r'\bid="entry-(\d{4}-\d{2}-\d{2})', text)
    if not dated or dated.group(1) < '2026-10-16':
        return
    gate = report_paragraph(text, 'Verification gate')
    plain = html.unescape(strip_tags(gate))
    for sentence in re.split(r'(?<=[.;])\s+', plain):
        if SCOPE_VERB.search(sentence) and not SCOPE_DIRECTION.search(sentence):
            raise ValueError('The Verification gate reports a change of scope ("' + SCOPE_VERB.search(sentence).group(0)
                             + '") without its direction: say whether the statement became more general, less '
                             'general (and the step that needs it), or was false; ' + sentence[:120] + ' (AGENTS.md)')


# Work of a later turn reported as done: "is built in the framework turn that follows", "are fixed in the next
# turn" (16 October 2026: two queued builds stated as built in a draft's Review and Prevention, caught only by its
# reviewer). "To be built", "planned for" and "will be" forms are not matched.
LATER_TURN_DONE = re.compile(
    # Present tense only: "was fixed in the next turn" can be true history (the builds' reviewer, 17 October 2026),
    # and "cycle" and "session" are the record's other words for a turn.
    r"\b(?:is|are|gets?)\s+(?:now\s+)?(?:built|closed|done|fixed|added|committed|answered|made|run)\s+"
    r"(?:in\s+(?:the|a)\s+(?:(?:[\w-]+\s+){0,3}?(?:turn|cycle|session)\s+(?:(?:right|just|planned|immediately)\s+)?"
    r"(?:after|following|that\s+follows|to\s+come)\b|(?:next|later|following|coming|subsequent)\s+"
    r"(?:[\w-]+\s+){0,2}?(?:turn|cycle|session)\b)|(?:right|just|immediately)\s+after\s+this\s+(?:review|entry)\b)",
    re.I)


def living_titles(body, section, item):
    """{id: plain title} of a living section's list items (`item` the attribute holding the id): the Open
    statements by li id, the remaining route by data-route-item; a title ends at its em dash or period."""
    found = re.search(rf'<section id="{section}">(.*?)</section>', body, re.S)
    titles = {}
    for m in re.finditer(rf'<li {item}="([^"]+)"><strong>(.*?)</strong>', found.group(1) if found else '', re.S):
        title = ' '.join(html.unescape(strip_tags(m.group(2))).split())
        titles[m.group(1)] = re.split(r'\s+—\s+|\.\s*$', title)[0].strip()
    return titles


def reduced_names(titles):
    """Forms of each Open statements title with one qualifier dropped (a word, or the prefix of a hyphenated
    token such as a MathJax qualifier before "-Frege"), at least three words long and found in no full title."""
    forms = {}
    for ident, title in titles.items():
        words = title.split()
        for i, word in enumerate(words):
            shorter = words[:i] + words[i + 1:]
            variants = [shorter] if len(shorter) >= 3 else []
            if '-' in word and not word.startswith('-'):
                variants.append(words[:i] + [word.rsplit('-', 1)[1]] + words[i + 1:])
            for variant in variants:
                form = ' '.join(variant)
                if len(variant) >= 3 and not any(form.lower() in t.lower() for t in titles.values()):
                    forms.setdefault(form, ident)
    return forms


def reduced_mentions(plain, titles):
    """(form, passage) for each place `plain` names an Open statements item by a reduced form of its title."""
    found = []
    lower = plain.lower()
    full = [m.span() for t in titles.values() for m in re.finditer(re.escape(t.lower()), lower)]
    for form in reduced_names(titles):
        for m in re.finditer(r'(?<![\w\\])' + re.escape(form.lower()) + r'(?!\w)', lower):
            if not any(a <= m.start() and m.end() <= b for a, b in full):
                found.append((form, plain[max(0, m.start() - 60):m.end() + 30]))
    return found


# A block of the route rotation named in an entry: capitalized words before "block" ("Repair Pang block").
# The record's forms (17 October 2026, from its own sentences): "X block, third turn", "X block's first turn",
# "turn 2 of the X block", "the third X research turn", "the first of the four X turns", "counted as an X turn".
# "The next X turn" names a later entry and is left out.
# Also "Third Pang turn", "Turn N of M of the X block" and "X turn N of M" (the builds' reviewer, 17 October 2026).
NAME = r'((?:[A-Z][\w-]*\s+){1,3})'
ORDINAL = r'(?i:first|second|third|fourth|fifth|sixth|last|\d+(?:st|nd|rd|th))'
BLOCK_FORMS = [re.compile(p) for p in (
    NAME + r'block(?:,|\'s)\s+(?:[\w-]+\s+){0,2}?turn\b',
    r'\b[Tt]urn\s+(?:\d+\s+(?:of\s+\d+\s+)?)?of\s+the\s+' + NAME + r'block\b',
    r'\b' + ORDINAL + r'\s+(?:of\s+(?:the\s+)?(?:two|three|four|five|six|\d+)\s+)?' + NAME + r'(?:research\s+)?turns?\b',
    r'\b(?:is|as)\s+an?\s+' + NAME + r'(?:research\s+)?turn\b',
    NAME + r'turn\s+\d+\s+of\s+\d+\b')]
# A block named as the one coming next is not counted: "the first IPS turn comes next", "before the first IPS turn"
# (the builds' reviewer found these refused on a Pang entry).
# "follows" only at its clause's end or as "follows next": "the third IPS turn follows from the lemma" counts a turn
# (the builds' reviewer's probe, 17 October 2026).
COMING_AFTER = re.compile(r'^[^.;,]*?\b(?:comes?\s+next|follows?(?=\s*(?:[.;,:]|$|next\b))|is\s+next|starts?\s+next|'
                          r'begins?\s+next)')
COMING_BEFORE = re.compile(r'\b(?:before|until|ahead\s+of)\s+(?:the\s+)?$', re.I)
BLOCK_SKIP = {'the', 'this', 'that', 'its', 'first', 'second', 'third', 'fourth', 'fifth', 'next', 'route', 'a'}


def block_routes(text, routes):
    """(name, slug) for each rotation block an entry's status line or Chosen paragraph names, with the route
    item whose title holds all of the name's words, when exactly one does."""
    meta = re.search(r'<p class="entry-meta">(.*?)</p>', text, re.S)
    chosen = report_paragraph(text, 'Chosen') if '<strong>Chosen.</strong>' in text else ''
    found = []
    for part in (meta.group(1) if meta else '', chosen):
        plain = ' '.join(html.unescape(strip_tags(part)).split())
        # Only a sentence that counts a turn toward the block: a review naming the block that comes next does not.
        counting = ' '.join(s for s in re.split(r'(?<=[.;:])\s+', plain) if re.search(r'\bturns?\b', s, re.I))
        for form in BLOCK_FORMS:
            for m in form.finditer(counting):
                if COMING_AFTER.search(counting[m.end():]) or COMING_BEFORE.search(counting[max(0, m.start() - 20):
                                                                                            m.start()]):
                    continue
                words = [w.lower() for w in m.group(1).split() if w.lower() not in BLOCK_SKIP]
                hits = [slug for slug, title in routes.items()
                        if words and all(re.search(r'\b' + re.escape(w) + r'\b', title.lower()) for w in words)]
                if len(hits) == 1:
                    found.append((m.group(1).strip(), hits[0]))
    return found


# A route title may hold lowercase words ("Use IPS directly"): after a capitalized first word any words count.
NEXT_STEP_BLOCK = re.compile(r'\b((?:[A-Z][\w-]*\s+)(?:[\w-]+\s+){0,4}?)block,?\s+on\s+([a-z][a-z-]+)\b')


def validate_next_step_blocks(body):
    """The Proposed next step names each block with the route it runs on ("the fourth Use IPS directly block, on
    ips-direct"): a block whose name belongs to another route item than the one named is refused (the item
    block-count-route-check asks the Proposed next step to be read too)."""
    section = re.search(r'<section id="proposed-next-step">(.*?)</section>', body, re.S)
    if not section:
        return
    routes = living_titles(body, 'remaining-route', 'data-route-item')
    plain = ' '.join(html.unescape(strip_tags(section.group(1))).split())
    wrong = []
    for m in NEXT_STEP_BLOCK.finditer(plain):
        if m.group(2) not in routes:
            continue
        words = [w.lower() for w in m.group(1).split() if w.lower() not in BLOCK_SKIP]
        hits = [slug for slug, title in routes.items()
                if words and all(re.search(r'\b' + re.escape(w) + r'\b', title.lower()) for w in words)]
        if len(hits) == 1 and hits[0] != m.group(2):
            wrong.append(f'"{m.group(1).strip()} block" is route {hits[0]}, not {m.group(2)}')
    if wrong:
        raise ValueError('The Proposed next step names a block with another route: ' + '; '.join(wrong))


def validate_statement_names(text, body):
    """An entry names an Open statements item by its full title, or by a reduced form beside the item's
    identifier (16 October 2026: a review dropped the qualifier of a title and it was fixed by hand)."""
    dated = re.search(r'\bid="entry-(\d{4}-\d{2}-\d{2})', text)
    if not dated or dated.group(1) < '2026-10-17':
        return
    titles = living_titles(body, 'open-statements', 'id')
    plain = ' '.join(html.unescape(strip_tags(text)).split())
    forms = reduced_names(titles)
    found = [(form, passage) for form, passage in reduced_mentions(plain, titles) if forms[form] not in passage]
    if found:
        raise ValueError('The entry names an Open statements item by a reduced form of its title: '
                         + '; '.join(f'"{form}" (full title: "{titles[forms[form]]}") in "...{passage}..."'
                                     for form, passage in found)
                         + '. Write the full title, or name the item\'s identifier beside it')


def validate_block_route(text, body, article):
    """A research entry counts a turn only toward the rotation block of its own route (16 October 2026: a draft
    counted a depth-prime-recurrence entry as a turn of the IPS block; only its reviewer saw it)."""
    dated = re.search(r'\bid="entry-(\d{4}-\d{2}-\d{2})', text)
    if not dated or dated.group(1) < '2026-10-17':
        return
    route = article_attribute(body, article, 'data-route-item')
    wrong = [(name, slug) for name, slug in block_routes(text, living_titles(body, 'remaining-route',
                                                                          'data-route-item')) if slug != route]
    if wrong:
        raise ValueError('The entry counts a turn toward the block of another route: '
                         + '; '.join(f'"{name} block" is route {slug}' for name, slug in wrong)
                         + f', while the entry\'s route is {route}. Count it toward its own route\'s block, or '
                         'toward none')


def validate_planned_tense(text):
    """Work a later turn is to do is written as planned, with its date, never as done."""
    dated = re.search(r'\bid="entry-(\d{4}-\d{2}-\d{2})', text)
    if not dated or dated.group(1) < '2026-10-17':
        return
    plain = ' '.join(html.unescape(strip_tags(text)).split())
    found = LATER_TURN_DONE.search(plain)
    if found:
        raise ValueError(f'The entry reports work of a later turn as done ("{found.group(0)}"): write it as '
                         'planned, with its date ("planned, as of DATE, for the framework turn after this entry") '
                         '(AGENTS.md: a message reports a result and not an intent)')


def validate_process_audit(text):
    """A reviewed entry reports the reviewer's audit of how the work was done (user, 10 October 2026: the
    agent should find its own mistakes without the user's hand-holding)."""
    gate = report_paragraph(text, 'Verification gate')
    if not re.search(r'href="[^"]*review[^"/]*\.txt"', gate):
        return
    found = re.search(r'<strong>Process audit\.</strong>(.*)', gate, re.S)
    plain = html.unescape(strip_tags(found.group(1))).strip() if found else ''
    if len(plain) < 40:
        raise ValueError('This entry links a reviewer record: report in its Verification gate, after '
                         '<strong>Process audit.</strong>, what the reviewer found about how the work was done '
                         'and what was changed, or that it found nothing (AGENTS.md, framework maintenance)')
    # Titles and status lines wider than their bodies were corrected in five of six entries of one block (review
    # of 11 October 2026), each prevention saying the reviewer had caught it.  The audit now says what the
    # reviewer found of the title, so the comparison is asked for and reported in every reviewed entry.
    if not re.search(r'\btitle', plain, re.I):
        raise ValueError('The Process audit does not speak of the title: say what the reviewer found of the '
                         "title and status line against the body, or that they claim no more than it, and "
                         'write both after the review (AGENTS.md, framework maintenance)')


DERIVES =re.compile(r'\bextrapolat|\bwhat-if\b|\bderived relation', re.I)


QUOTED_ONLY = re.compile(r'\bevery displayed (?:relation|formula) is quoted\b', re.I)


def validate_unreviewed_derivations(text, claims=None):
    """A research entry that derives relations of its own goes to the cycle's reviewer.

    Three reading entries of 11 October 2026 registered no claim, so their gates said no reviewer was used,
    while they extrapolated a source's formulas and evaluated a what-if; one conclusion took a fixed constant
    for an inherited bound and steered a route review before a reviewer saw it.  An entry whose gate says no
    reviewer was used may quote a source, and may not extrapolate from it."""
    gate = html.unescape(strip_tags(report_paragraph(text, 'Verification gate')))
    if not re.search(r'\bno reviewer\b', gate, re.I):
        return
    body = html.unescape(strip_tags(text.replace(report_paragraph(text, 'Verification gate'), '')))
    found = DERIVES.search(body)
    if not found and claims is not None and not claims and '\\[' in text and not QUOTED_ONLY.search(gate):
        # Measured on 11 October 2026 on every notebook: of 142 research entries whose gate says no reviewer,
        # six register no claim and display a formula; three are the readings this check was written for, two
        # of which the words above miss, and the other three are readings and attempts of the same kind.
        raise ValueError('This entry registers no claim, its Verification gate says no reviewer was used, and it '
                         'displays formulas: give them to the cycle\'s reviewer and report the verdict in the '
                         'gate, or say in the gate that every displayed relation is quoted from a source, naming '
                         'it (AGENTS.md, one focused correctness review)')
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
    plain = html.unescape(strip_tags(found.group(1))).strip() if found else ''
    if len(plain) < 40:
        raise ValueError('End the Process assessment with <strong>Prevention.</strong> and at least 40 '
                         'characters: the committed check or rule for each mistake it reports, or why none '
                         'applies (AGENTS.md, framework maintenance)')
    # A Process assessment that reports no mistake while the review required corrections was written before the
    # review (17 October 2026: "No mistake of mine is found" stood beside a gate listing nine corrections).
    gate = html.unescape(strip_tags(report_paragraph(text, 'Verification gate')))
    # A sentence describing a check that refuses such an assessment is not one (17 October 2026: the entry that
    # built this check described it in its own Prevention).
    said = ' '.join(s for s in re.split(r'(?<=[.!?])\s+', html.unescape(strip_tags(assessment)))
                    if not re.search(r'\brefus', s, re.I))
    if NO_MISTAKE.search(said) and REVIEW_CORRECTED.search(gate):
        raise ValueError(f'The Process assessment says "{NO_MISTAKE.search(said).group(0)}" while the Verification '
                         'gate reports corrections the reviewer required: write the assessment after the review, '
                         'naming each mistake the corrections show (AGENTS.md, framework maintenance)')


# Tried, before its commit, against rewordings of the exposing sentence ("I found no error", "No mistakes in this
# cycle", "went without mistakes", "None of mine", "I made no mistake"): the first form let five of six through.
NO_MISTAKE = re.compile(r"\b(?:no|without) (?:mistakes?|errors?)\b|\bnothing went wrong\b|\bnone of mine\b", re.I)
REVIEW_CORRECTED = re.compile(r"\b(?:it|the reviewer|the review) (?:required|asked for|found(?! no\b| nothing\b))\b|"
                              r"\bcorrections?\b"
                              r"[^.]{0,40}\b(?:made|adopted|applied|required)\b|\bAll are (?:made|corrected)\b", re.I)


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
    text = body[article:body.find('</article>', article)]
    answer = report_paragraph(text, 'Review')
    if len(html.unescape(strip_tags(answer)).strip()) < 40:
        raise ValueError(f'The stand-in review in {owed} is unanswered: check each of its objections against the '
                         'record, then say in a paragraph of the entry starting <strong>Review.</strong> what became '
                         'of each: fixed, queued, or wrong and why (AGENTS.md, framework maintenance)')
    # The meta-question for the objections that were right: why the stand-in, not the agent, found them (AGENTS.md;
    # ported from another branch's checkpoint, 16 October 2026).
    if len(html.unescape(strip_tags(report_paragraph(text, 'Meta'))).strip()) < 40:
        raise ValueError(f'The stand-in review in {owed} is answered without its meta-question: add a paragraph '
                         'starting <strong>Meta.</strong> saying, for its right objections, what way of working '
                         'produced them, where else it shows, and the change in how the work is done that ends it, '
                         'named by the file that holds it; where none was right, say so (AGENTS.md)')
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


def stopped_short(root, turn, entry=None):
    """Lines for the finisher to print, or none: theorem-like statements of TeX and Lean files that begin,
    unread, within 100 lines after a range the session read in this turn; the unread parts of files the
    entry names, with their headings; and the entry's sentences that say what such a file says
    (tools/session_reads.py).  A reading of 11 October 2026 stopped fifty lines short of the proposition that
    decided its test; an entry of 12 October said what a record reports from its first 225 lines of 277, and
    the rest said the opposite.  It prints and refuses nothing: a refusal of such sentences was built and
    withdrawn at its review, its match of the verbs and of files by name refusing wrongly.  A turn not started
    by the finisher's --next, and an agent without a transcript, print nothing."""
    stand_in_review = reviewer()
    try:
        import session_reads
        transcript = stand_in_review.session_transcript(root)
        lines = session_reads.turn_lines(Path(transcript).read_text(errors='replace').splitlines(), turn, entry)
    except Exception:      # a listing is never the finisher's failure
        return []
    return (['Readings: statements that begin just past a range of a source this turn read, sources that could '
             'not be checked, the unread parts of files the entry names, and its sentences on what a partly '
             'read file says; say in the entry whether each was read or why it does not matter:']
            + lines) if lines else []


BEARING_AFTER = 2      # earlier research entries in a row, on the route, reporting unchanged goal progress
BEARING_MIN = 60
NOT_COVERED_MIN = 40
NO_BEARING_RUN = 3     # earlier research entries in a row, on the route, declaring no bearing


PROCEDURAL_REASON_RE = re.compile(r'\b(?:the|a|its|last) review (?:decided|asked|named|gave|said|listed)\b|'
                                  r'\bleft (?:this|it|the attempt|an attempt) owed\b|\bwithout an entry\b|'
                                  r'\bhad been queued\b|\bhad waited\b', re.I)


UNCHECKED_RE = re.compile(r'\b(?:did not|have not|had not|not yet|was not|were not|are not|is not)\s+'
                          r'(?:\w+\s+){0,3}?(?:check|checked|verify|verified)\b|\bunchecked\b|\bunverified\b', re.I)


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
    plain = html.unescape(strip_tags(found.group(1))).strip() if found else ''
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
    # A review of 11 October 2026 ruled out, as the reason a cycle without bearing was spent, that the item's
    # last entry or a review had asked for it; three entries of the next block gave that reason again, the rule
    # restated in prose not having been enough.  The reason is what the result could have given.
    if declared.group(1) == 'none':
        procedural = PROCEDURAL_REASON_RE.search(plain)
        if procedural:
            raise ValueError(f'The Bearing paragraph gives a procedural reason for the cycle ("{procedural.group(0)}"): '
                             'say what the entry\'s result could have given at the goal\'s own parameters; that a '
                             'review or an earlier entry asked for the work, or that the item had waited, is not '
                             'a reason (AGENTS.md, goal progress)')
    # Two blocks of six entries each declared no bearing while a queue was served one leftover check at a time
    # (reviews of 11 October 2026).  After three such entries in a row the next one says, before its work, what
    # its best outcome would give at the goal's own parameters; the start guidance already asked and was not
    # enough.
    if text is not None:
        without = 0
        for earlier in reversed(re.findall(r'<article\b[^>]*>', body[:article])):
            if f'data-route="{route}"' not in earlier or 'data-kind="research"' not in earlier:
                continue
            if 'data-bearing="none"' not in earlier:
                break
            without += 1
        if without >= NO_BEARING_RUN:
            best = re.search(r'<strong>Best outcome\.</strong>((?:(?!</p>).)*)', text, re.S)
            plain = html.unescape(strip_tags(best.group(1))).strip() if best else ''
            if len(plain) < BEARING_MIN:
                raise ValueError(f'{without} research entries in a row on {route} declared no bearing: state, '
                                 f'after <strong>Best outcome.</strong> and in at least {BEARING_MIN} characters, '
                                 "what this entry's best outcome would give at the goal's own parameters, "
                                 'written before the work; if nothing, the entry closes a queue item and says so '
                                 '(AGENTS.md, goal progress)')
            # On 16 October 2026 an entry spent its cycle on a question its own record had settled a cycle
            # before: its Best outcome named what a success would give, not the recorded bound a success must
            # beat, and nothing made it look.
            if not re.search(r'\b(?:lem|thm|prop|cor|check|ex|conj):[\w-]+', plain):
                raise ValueError(f'{without} research entries in a row on {route} declared no bearing: name in the '
                                 'Best outcome, by its claim ID, the recorded result or bound its best outcome must '
                                 'beat, and check that the record does not already decide the question (AGENTS.md, '
                                 'goal progress)')
            # An entry in such a run opened with "nothing at the goal's parameters" as its best outcome and
            # closed no item; its reviewer could only say afterwards that it should have been refused
            # (review of 11 October 2026).
            if NOTHING_BEST_RE.search(plain) and not CLOSED_FOLLOW_UP_RE.search(text):
                raise ValueError(f'{without} research entries in a row on {route} declared no bearing, and this '
                                 "entry's Best outcome says it gives nothing at the goal's parameters while it "
                                 'closes no queue item: take an attempt whose best outcome bears on the goal, or '
                                 'close the item (AGENTS.md, goal progress)')
    # A bearing that claims something was closed, in two entries in a row, with a summary sentence wider
    # than the proof (reviews of 10 October 2026): it ends with what the result does not cover.
    if declared.group(1) == 'some':
        uncovered = re.search(r'<strong>Not covered\.</strong>(.*)', found.group(1), re.S)
        plain = html.unescape(strip_tags(uncovered.group(1))).strip() if uncovered else ''
        if len(plain) < NOT_COVERED_MIN:
            raise ValueError('This entry declares data-bearing="some": end its Bearing statement with '
                             f'"<strong>Not covered.</strong>" and at least {NOT_COVERED_MIN} characters '
                             'listing the cases its result does not reach, with no summary after the list '
                             '(AGENTS.md, goal progress)')
        # A reviewer of 11 October 2026 refused a bearing whose own text said the hypotheses of the
        # statement it rested on had not been checked.
        whole = html.unescape(strip_tags(found.group(1)))
        if UNCHECKED_RE.search(whole):
            raise ValueError('This entry declares data-bearing="some" and its Bearing statement says that '
                             'something it relies on was not checked: check it, or declare "none" '
                             '(AGENTS.md, goal progress)')
    item = re.search(r'data-(?:check|lead|bridge|idea|build)="([^"]+)"', tag)
    if item is None:
        return
    earlier = [t for t in re.findall(r'<article\b[^>]*>', body[:article])
               if f'data-route="{route}"' in t and 'data-kind="research"' in t][-2:]
    same = [t for t in earlier if re.search(r'data-(?:check|lead|bridge|idea|build)="' + re.escape(item.group(1)) + '"', t)
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
    validate_bearing_ledger(text)
    validate_prevention(text)
    validate_process_audit(text)
    validate_planned_tense(text)
    validate_statement_names(text, body)
    if tags['kind'] == 'research':
        validate_block_route(text, body, article)
    if re.search(r'\bid="entry-2026-10-(?:1[7-9]|[23]\d)|\bid="entry-2026-1[12]-|\bid="entry-202[7-9]-', text):
        validate_next_step_blocks(body)
    if any(cid.startswith('ex:') for cid in entry_claims(body, article)):
        validate_nonvacuity(text)
    if tags['kind'] == 'research':      # queue items are developed, and so closed, in research entries
        validate_unreviewed_derivations(text, entry_claims(body, article))
        validate_closures(text)
        validate_developed_removals(text)
        validate_corrections_read(text)
        validate_developed_readings(text)
        validate_smallest_case(text)
        validate_scope_direction(text)
        if check_registered_claims:
            known = registered_status()
            statuses = {known.get(cid) for cid in entry_claims(body, article)}
            validate_structural_reason(text, statuses, entry_claims(body, article))
            validate_degenerate_cases(text, statuses)
            validate_proved_instance(text, statuses)
            validate_hypothesis_steps(text, statuses)
            validate_baseline(text, statuses)
            validate_plainest(text, statuses)
            validate_unbounded_witness(text)
        else:
            # A draft's claims are not registered yet: a Proof paragraph stands for a proved status, so the
            # checks of proved statements run at drafting (16 October 2026: a Nonvacuity without its Plainest
            # bound passed the skeleton check twice and was refused only at the finisher, after the append).
            validate_drafted_proofs(text, draft_statuses(text))
            validate_structural_reason(text, claims=entry_claims(body, article))
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
                plain = html.unescape(strip_tags(down.group(1))).strip() if down else ''
                if len(plain) < 60 or not re.search(r'\b(?:thm|cor|prop|lem):[\w-]+', plain):
                    raise ValueError('Necessary target must end with "<strong>Downstream.</strong>": the target '
                                     'evaluated through the proved downstream statements, citing their claim '
                                     'IDs, with the explicit consequence and whether it is the goal or weaker '
                                     '(AGENTS.md, Necessary target)')
            if label == 'Decisive test':
                validate_test_disposition(body, article, value)
                searched = re.search(r'<strong>Record search\.</strong>(.*)', value, re.S)
                plain = html.unescape(strip_tags(searched.group(1))).strip() if searched else ''
                if len(plain) < 40:
                    raise ValueError('Decisive test must end with "<strong>Record search.</strong>" naming the '
                                     'registry searches made for the test and what they returned: a test the '
                                     'record already answers decides nothing (AGENTS.md, Decisive test)')
                power = re.search(r'<strong>Power\.</strong>(.*?)(?=<strong>Record search\.</strong>|$)', value, re.S)
                plain = html.unescape(strip_tags(power.group(1))).strip() if power else ''
                if len(plain) < 40:
                    raise ValueError('Decisive test must state "<strong>Power.</strong>" before its Record search: '
                                     'what the recorded ceilings and method limits give on the test\'s object, '
                                     'and, for a computation, the sizes reachable and why its outcomes differ '
                                     'there; a test whose every outcome fits every answer decides nothing '
                                     '(AGENTS.md, Decisive test)')
                # A review of 16 October 2026 posed a test on an instance outside the goal's parameter window
                # without saying so; its reviewer found it. Power says where the instance stands.
                stamped = re.search(r'\bid="entry-(\d{4}-\d{2}-\d{2})', text)
                if (stamped and stamped.group(1) >= WINDOW_FROM
                        and not re.search(r"\bwindow\b|goal's (?:own )?parameters|goal-parameter", plain, re.I)):
                    raise ValueError('Decisive test\'s Power must say whether the test\'s instance lies within the '
                                     'goal\'s parameter window and, if not, what its outcome bears on (AGENTS.md, '
                                     'Decisive test)')
                attempt = re.search(r'<strong>Attempt\.</strong>(.*?)(?=<strong>|$)', value, re.S)
                plain = html.unescape(strip_tags(attempt.group(1))).strip() if attempt else ''
                if len(plain) < 40:
                    # A review of 11 October 2026 posed a test twice that its cited statements answered in a
                    # few lines; the attempt to answer it had not been made before posing it.
                    raise ValueError('Decisive test must state "<strong>Attempt.</strong>": what was tried, before '
                                     'posing the test, to answer it from the statements it cites, and where that '
                                     'stopped; a test those statements answer in a few lines is a lemma, not a '
                                     'test (AGENTS.md, Decisive test)')
                # Four reviews in a row posed a test their reviewer then closed in a few lines: the gate of a
                # review says what the reviewer found when it tried the step at which the Attempt stops.
                dated = re.search(r'\bid="entry-(\d{4}-\d{2}-\d{2})', text)
                if dated and dated.group(1) >= OWED_FROM and not attempt_checked(text):
                    raise ValueError('A review\'s Verification gate must say, after "<strong>Attempt checked.'
                                     '</strong>", what its reviewer found on trying to close the step at which '
                                     'the Decisive test\'s Attempt stops: ask for that in the second-stage brief '
                                     '(AGENTS.md, Decisive test)')
                trivial = re.search(r'<strong>Trivial cases\.</strong>(.*?)(?=<strong>Power\.</strong>|$)', value, re.S)
                plain = html.unescape(strip_tags(trivial.group(1))).strip() if trivial else ''
                if len(plain) < 40:
                    # A block of 11 October 2026 was given to a comparison with a quantity that changes when
                    # implied rows are added to a system while its degree does not: the question had a trivial yes.
                    raise ValueError('Decisive test must state "<strong>Trivial cases.</strong>" before its Power: '
                                     'how each quantity the test compares behaves under the object\'s trivial '
                                     'transformations (implied or duplicated rows, another presentation), and '
                                     'the trivial instance, if any, that would give each outcome; a question '
                                     'with a trivial answer decides nothing (AGENTS.md, Decisive test)')
                # Three reviews of 16 October 2026 posed a test whose instance their own Trivial cases or Power
                # decided; the third called its room tight where its numbers gave 2 < 3.  The inequalities are
                # evaluated with the instance's numbers in writing.
                if dated and dated.group(1) >= INSTANCE_CHECK_FROM:
                    check = re.search(r'<strong>Instance check\.</strong>(.*?)(?=<strong>[A-Z][a-z ]*\.</strong>|$)',
                                      value, re.S)
                    plain = html.unescape(strip_tags(check.group(1))) if check else ''
                    if not NUMERIC_RELATION.search(plain):
                        raise ValueError('Decisive test must state "<strong>Instance check.</strong>": each '
                                         'inequality its Trivial cases and Power use, evaluated with the '
                                         'instance\'s numbers (for example \\(2+1=3\\le3\\)), so that an instance '
                                         'they already decide is seen before it is posed (AGENTS.md, Decisive '
                                         'test)')
    else:
        target = pending_architecture_test(body, article).get(tags['route'])
        if target and article_attribute(body, article, 'data-picked') != 'user':
            evidence = require_report(text, 'Architecture test')
            if not re.search(r'href=["\']#' + re.escape(target) + r'["\']', evidence):
                raise ValueError(f'Architecture test must report the outcome of the scheduled decision '
                                 f'and link #{target}; a further local lemma is not a substitute')
            if not VERDICT_RE.search(evidence):
                raise ValueError('Architecture test must say <strong>Decided.</strong> or <strong>Not '
                                 'decided.</strong> and which of the review\'s outcomes occurred: a test left '
                                 'unanswered is reported as not decided, not as a changed question (AGENTS.md)')


def entry_claims(body, article):
    tag = body[article:body.index('>', article) + 1]
    return [c for c in (re.search(r'data-claims="([^"]*)"', tag) or [None, ''])[1].split() if c != 'none']


FINITE_PREFIXES = ('ex:', 'check:')


@functools.cache
def registered_status():
    """Claim ID to mathematical status, parsed once per process: nothing here writes the registry,
    and validating it belongs to the claim checks, not to a status lookup."""
    registry = ROOT / 'research/claims/index.json'
    return {c['id']: c.get('mathematical_status') for c in registry_data(registry)['claims']} if registry.exists() else {}


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
    return strip_tags_tight(body[meta:body.find('</p>', meta)]).split('Produced by')[0]


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
        if not found or len(strip_tags(found.group(1)).strip()) < 40:
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
                or len(strip_tags(found.group(1)).strip()) < 20]
        if bare:
            raise ValueError(f"Reviewer's suggestions item(s) {bare} lack \"<strong>Record.</strong>\" with the "
                             'outcome of a record search (tools/search-claims.py and the notebook): the claim '
                             'IDs or anchors that bear on the suggestion, or the words searched without a '
                             'match (AGENTS.md)')


FOLLOW_UP_TEXT_RE = re.compile(r'<strong>Follow-up\.</strong>(.*?)(?=</p>|</li>)', re.S)   # paragraphs and list items
ATTEMPT_PHRASE_RE = re.compile(r'\b(?:next attempt|still owed|stays? owed)\b', re.I)
SENTENCE_END_RE = re.compile(r'(?<=[.!?])\s+(?=[A-Z\\(])')        # "cf. the list" does not end a sentence
REVIEWERS_IDEA_RE = re.compile(r"\breviewer(?:'s|’s) (?:candidate|suggestion|remark|proposal|idea|"
                               r'construction|count|argument)\b', re.I)
SET_ASIDE_RE = re.compile(r'\b(?:dropped|withdrawn|not taken|not named|set aside)\b', re.I)
CHECKED_RE = re.compile(r'<p><strong>Suggestion checked\.</strong>((?:(?!</p>).)*)</p>', re.S)
CHECKED_LEAST = 60     # plain characters; the paragraph is a prompt to check, which no tool can verify
SUGGESTION_QUOTE = 8   # consecutive words of a listed suggestion
# the heading with any attributes, and whatever lists follow it, nested ones included
SUGGESTION_LIST_RE = re.compile(r"<h4\b[^>]*>\s*Reviewer(?:'s|&#39;s|’s)? suggestions[^<]*</h4>(.*?)"
                                r'(?=<h4\b|<p>|<p\s|$)', re.S)


def unverified_attempts(entry, next_html=None):
    """What an entry plans on a suggestion nobody has checked: [(where, reason)].

    Read: each Follow-up, in a paragraph or a list item, from the sentence that names a next attempt to its end;
    and the next step.  Found: a sentence there that calls what it names unverified, or speaks of the reviewer's
    candidate, suggestion or remark, unless the sentence sets it aside; eight consecutive words of an item of
    the entry's list of reviewer's suggestions, its Record note excepted; and, for a follow-up, an item of that
    list that points back with "as in the follow-up".

    On 12 October 2026 a follow-up named as its next attempt "the reviewer's candidate, unverified", with a best
    outcome built on it; one line of the next entry refuted the candidate's count, and that entry named "the
    reviewer's remark" as its next attempt in turn.  The rule that a suggestion is verified before it is named
    as a next step (AGENTS.md) had no check.  These are signals of wording: an attempt put in the author's own
    words, without the label, is not seen ("the construction the reviewer proposed"), and a different attempt on
    an object a suggestion names is, as is "the reviewer's count, proved above".  A sentence that sets one thing
    aside is skipped whole, so a plan in the same sentence passes; and sentences are split only before a capital
    or a formula.  A follow-up that is Closed, Developed or Promoted is not read."""
    def plain(text):
        return re.sub(r'\s+', ' ', html.unescape(strip_tags(text))).strip()

    def words(text):
        return [w for w in (re.sub(r'^\W+|\W+$', '', t).lower() for t in plain(text).split()) if w]

    items = [RECORD_RE.split(item)[0] for section in SUGGESTION_LIST_RE.finditer(entry)
             for item in re.findall(r'<li\b[^>]*>(.*?)</li>', section.group(1), re.S)]
    runs = {tuple(given[i:i + SUGGESTION_QUOTE]) for given in map(words, items)
            for i in range(len(given) - SUGGESTION_QUOTE + 1)}
    points_back = any(re.search(r'\bas in the follow-up\b', plain(item), re.I) for item in items)
    plans = []
    for follow in FOLLOW_UP_TEXT_RE.findall(entry):
        if re.match(r'\s*(?:Closed|Developed|Promoted)\b', plain(follow)):
            continue                                    # it removes its item and plans nothing
        sentences = SENTENCE_END_RE.split(plain(follow))
        first = next((i for i, s in enumerate(sentences) if ATTEMPT_PHRASE_RE.search(s)), None)
        if first is not None:
            plans.append(('follow-up', sentences[first:]))
    if next_html is not None:
        plans.append(('next step', SENTENCE_END_RE.split(plain(next_html))))
    found = []
    for where, sentences in plans:
        live = [s for s in sentences if not SET_ASIDE_RE.search(s)]
        have = words(' '.join(live))
        if any(re.search(r'\bunverified\b', s, re.I) for s in live):
            found.append((where, 'calls what it names unverified'))
        elif any(REVIEWERS_IDEA_RE.search(s) for s in live):
            found.append((where, "names the reviewer's candidate, suggestion or remark"))
        elif any(tuple(have[i:i + SUGGESTION_QUOTE]) in runs for i in range(len(have) - SUGGESTION_QUOTE + 1)):
            found.append((where, f"quotes {SUGGESTION_QUOTE} consecutive words of an item of the entry's list of "
                                 "reviewer's suggestions"))
        elif where == 'follow-up' and points_back:
            found.append((where, "is what an item of the entry's list of reviewer's suggestions points to "
                                 '("as in the follow-up")'))
    return found


SUGGESTED_RE = re.compile(r'\bsuggest(?:ed|ion|ions|s)?\b', re.I)


def refuse_unlisted_suggestions(entry):
    """A gate that reports a reviewer's suggestion needs the entry's list of them, which the check below reads.

    On 16 October 2026 an entry adopted a reviewer's suggestion as its next attempt in its own words, with no
    list of suggestions, so unverified_attempts saw nothing; the suggestion was false at every case."""
    dated = re.search(r'\bid="entry-(\d{4}-\d{2}-\d{2})', entry)
    if not dated or dated.group(1) < '2026-10-16':
        return
    gate = re.search(r'<strong>Verification gate\.</strong>((?:(?!</p>).)*)', entry, re.S)
    if gate and SUGGESTED_RE.search(strip_tags(gate.group(1))) and not SUGGESTION_LIST_RE.search(entry):
        raise ValueError("The Verification gate reports a reviewer's suggestion and the entry has no <h4>Reviewer's "
                         'suggestions, unverified</h4> list: list each suggestion there, with its Record note, so '
                         'that a next attempt drawn from one is checked (AGENTS.md)')


def refuse_unverified_attempt(entry, next_html=None):
    """Refuse such a plan unless the entry says, after a fixed label, what was checked of the suggestion."""
    refuse_unlisted_suggestions(entry)
    found = unverified_attempts(entry, next_html)
    checked = CHECKED_RE.search(entry)
    said = len(strip_tags(checked.group(1)).strip()) if checked else 0
    if found and said < CHECKED_LEAST:
        where, reason = found[0]
        raise ValueError(f"The {where} {reason}: a reviewer's suggestion is an unverified lead, verified before it "
                         'is named as a next step (AGENTS.md). Say in a <p><strong>Suggestion checked.</strong> '
                         f'paragraph of the entry, in at least {CHECKED_LEAST} characters, what of it was checked '
                         'and how, or name another attempt')


def claimless_build(body, article):
    """An entry on a build item that declares no claims: a framework build has no all-parameter claim.

    Such entries met the General statement check by citing an unrelated registered claim and saying so
    (11 October 2026, a reviewer's finding); their paragraph may now say that no claim applies."""
    tag = body[article:body.index('>', article) + 1]
    return bool(re.search(r'\bdata-build="[^"]+"', tag) and re.search(r'\bdata-claims="none"', tag))


def validate_general(body, article, close, *, registered=True):
    """AGENTS.md: restricted examples must test a named general statement; enforce it mechanically.
    Every research entry states its general claim for all parameters, and two finite-check entries
    in a row on one route (neither with a proof or refutation) are rejected. With `registered=False`, for a
    draft whose claims are not registered yet, a cited claim ID need not be in the registry."""
    if not re.search(r'data-route-item="', body):     # active once the notebook declares route items
        return
    tags = entry_tags(body, article)
    if tags['kind'] != 'research':
        return
    found = GENERAL_RE.search(body, article, close)
    text = strip_tags(found.group(1)).strip() if found else ''
    if len(text) < 40:
        raise ValueError('A research entry needs a <p><strong>General statement.</strong> ...</p> '
                         'paragraph: the claim this cycle tests or proves, for all parameters, with '
                         'its conjectured bound as a formula (AGENTS.md, restricted examples)')
    ids = GENERAL_ID.findall(found.group(1))
    if registered and (ROOT / 'research/claims/index.json').exists():
        ids = [i for i in ids if i in registered_status()]
    if not ids and not claimless_build(body, article):
        raise ValueError('The General statement must cite the registered claim ID (conj:, lem:, thm:, '
                         'prop: or cor:) that states it for all parameters; register a conjecture if '
                         'it is not proved')
    # The General statement carries the conditions of the claim it cites (17 October 2026: a General statement
    # dropped both degree windows its claim's summary states); the commit message's condition check, applied here.
    if ids and (ROOT / 'research/claims/index.json').exists():
        from commit_message_checks import dropped_conditions
        summaries = {c['id']: c.get('summary', '') for c in read_json(ROOT / 'research/claims/index.json')['claims']
                     if c['id'] in ids}
        dropped = dropped_conditions(html.unescape(found.group(1)), list(summaries.items()), windows_only=True)
        if dropped:
            raise ValueError('The General statement drops conditions of the claim it cites: '
                             + '; '.join(f'{i}: "{c}"' for i, c in dropped) + '. State each, or the range it '
                             'is stated for (AGENTS.md: summaries keep their source\'s qualifiers)')
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
    deferred = third_deferral_line(body, article, close)    # printed even when a check below refuses
    if deferred:
        print(deferred)
    for _, check in entry_checks(body, article, close, draining, before=position):
        check()


def validate_status_line(body, article, before):
    meta = body.find('<p class="entry-meta">', article, before)
    if meta < 0 or body.find('</p>', meta, before) < 0:
        raise ValueError('The entry needs a <p class="entry-meta"> status line before its timing marker')
    status = strip_tags_tight(body[meta:body.find('</p>', meta)]).split('Produced by')[0]
    if len(status.strip()) > STATUS_LIMIT:
        raise ValueError(f'The status line has {len(status.strip())} characters; keep it under '
                         f'{STATUS_LIMIT}: the status and one clause of scope, details in the entry')


def entry_checks(body, article, close, draining=None, *, registered=True, before=None):
    """The finisher's checks of one entry, as (name, call) pairs in the order validate_marker runs them, so that
    notebook-append.py --check runs the same list on a draft; `registered=False` leaves out the parts that read
    claims registered for the entry, which a draft does not have yet. The status line is looked for before
    `before` (the timing marker), by default anywhere in the entry."""
    return [
        ('status line', lambda: validate_status_line(body, article, close if before is None else before)),
        ('route', lambda: validate_route(body, article)),
        ('general statement', lambda: validate_general(body, article, close, registered=registered)),
        ('required paragraphs', lambda: validate_paragraphs(body, article, close)),
        ('reviewer suggestions', lambda: validate_suggestions(body, article, close)),
        # the entry as it stands at the end, edits after appending included
        ('unverified attempt', lambda: refuse_unverified_attempt(body[article:close])),
        ('leads and follow-ups', lambda: validate_leads(body, article, close, draining=draining)),
        ('convergence', lambda: validate_convergence(body, article, close)),
        ('review builds', lambda: validate_review_builds(body, article, close)),
        ('owed attempt', lambda: validate_owed_unmade(body, article, close)),
        ('bridges', lambda: validate_bridges(body, article, close)),
        ('progress and bearing',
         lambda: validate_progress(body, article, close, check_registered_claims=registered)),
        ('characters and names', lambda: validate_characters(body[article:close])),
    ]


def validate_characters(entry):
    if '$' in entry:
        # MathJax treats a dollar sign as an inline-math delimiter; the notebook uses \( \).
        raise ValueError('The entry contains a dollar sign, which MathJax reads as a math delimiter; '
                         'write mathematics with \\( \\) and currency as "USD 5"')
    coded = letter_code_labels(entry)
    if coded:
        raise ValueError('The entry names results by letter codes ' + ', '.join(coded) + ': cite them '
                         'by descriptive names (CLAUDE.md, Naming results), e.g. "the constant-row clamp" '
                         'rather than "Lemma K"; the claim ID usually gives the name')
    control = sorted({c for c in entry if ord(c) < 32 and c != '\n'})
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


def stale_review_hint(errors):
    """How to refresh reviews made stale by an entry edited after its claims were built (16 October 2026: the
    message named the stale fields only, and author build refuses to overwrite its own outputs)."""
    if not any(error.endswith(' is stale') for error in errors):
        return ''
    return ('\nA stale review hashes evidence that changed after registration, usually the entry edited after '
            'author build. Rebuild in one step, with that build\'s paths: ./compute.sh --threads 1 --category '
            'local_processing python3 tools/claim_refresh.py SPEC --out OUT --proposal PROPOSAL --report REPORT '
            '(it restores the registry from HEAD, deletes the old outputs, reruns author build, copies the '
            'proposal and renders; keep PROPOSAL in scratch). Add --summaries-checked once the spec\'s '
            'summaries have been compared with the edited entry\'s statements, which author build prints.')


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
    from lead_queue import check, extended_again, is_draining, SECTION_RE
    relative = notebook.resolve().relative_to(root.resolve()).as_posix()
    head = subprocess.run(['git', 'show', f'HEAD:{relative}'], cwd=root, capture_output=True, text=True)
    body = notebook.read_text()
    check(head.stdout if head.returncode == 0 else None, body, notebook, root)
    again = extended_again(head.stdout if head.returncode == 0 else None, body)
    if again:
        raise ValueError('The text of a queued build was extended again (' + ', '.join(again) + '): its text '
                         'already carried an addition. Build it in this turn, or queue what is new as an item of '
                         'its own with tools/lead_queue.py add; a prevention is not a longer queue item (AGENTS.md)')
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
    whole = notebook.read_text()
    entry = whole[whole.rfind('<article', 0, whole.index(marker)):whole.index(marker)]
    logged = logged_searches(root, first.get('unix_s', 0))
    # As for the resemblance check below: a checkout that has never searched has no log to read runs from.
    unread = (count_listing_report(entry, logged)
              if (root / 'research/logs/claim-searches.jsonl').exists() else None)
    if unread:
        print(unread)
    declared = re.search(r'\bdata-claims="([^"]*)"', entry[:entry.find('>') + 1])
    validate_assessments_filled(root / 'research/claims/index.json',
                                [c for c in (declared.group(1).split() if declared else []) if c != 'none'])
    for line in (decided_report(entry) + absence_report(entry) + architecture_context_report(whole, entry)
                 + next_attempt_neighbours(whole, entry, root / 'research/claims/index.json')):
        print(line)
    for line in hook_notice_lines(root, first.get('unix_s', 0)):
        print(line)
    searches = validate_searches_run(entry, [query for query in logged if not query.startswith('draft_counts ')])
    validate_next_attempt_search(entry, searches)
    if (root / 'research/logs/claim-searches.jsonl').exists():   # a checkout that has never searched has no log
        validate_resemblance_run(entry, searches)
    if '<strong>Record search.</strong>' in entry:
        print('Registry searches run in this session, to compare with the entry\'s Record search: '
              + '; '.join(searches))
    owed = validate_review_answer(root, notebook.read_text(), marker)
    check_context(root, item["name"])  # Fail before stopping timing, archiving, or changing the notebook.
    validate_append_only(root)
    if (root / 'research/claims/index.json').exists():
        claims = load_claims(root / 'research/claims/index.json')
        if (root / 'research/CLAIM_INDEX.md').read_text() != render_claims(claims):
            raise ValueError('Generated claim index is stale; run tools/claim-index.py render')
        contract = check_revision(claims, root=root)
        if not contract['passed']:
            raise ValueError('Changed-claim metadata incomplete:\n' + '\n'.join(contract['errors'])
                             + stale_review_hint(contract['errors']))
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
        validate_marker(current, marker, draining=draining)
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
    for line in stopped_short(root, turn, entry) + stand_in(root, owed):
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
