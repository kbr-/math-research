#!/usr/bin/env python3
"""Export timing, archive evidence, and fill one notebook timing placeholder."""
import argparse
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

ROOT = Path(__file__).resolve().parents[1]


def session_name(value):
    if not re.fullmatch(r'[A-Za-z0-9_.-]+', value) or value in ('.', '..'):
        raise argparse.ArgumentTypeError('Use a simple session name, not a path')
    return value


REVIEW_PERIOD = 6    # research entries allowed in a row before a route review is required
STATUS_LIMIT = 300   # characters of status-line text, before the producer credit
KINDS = ('research', 'review', 'formalization')


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
        raise ValueError('Tag the entry: <article ... data-kind="research|review|formalization" '
                         'data-route="ITEM">, ITEM a data-route-item of The remaining route or side-...')
    if tags['kind'] == 'formalization':
        return
    if tags['route'] not in items and not (tags['route'] or '').startswith('side-'):
        raise ValueError(f'data-route must be one of {sorted(items)} or start with side-; '
                         'name the top-level route item, not a sub-gap of the current line')
    record = body.find('<section id="research-record">')
    earlier = [m.start() for m in re.finditer(r'<article\b', body[:article]) if m.start() > record]
    streak, after_review = 0, False
    for position in reversed(earlier):
        kind = entry_tags(body, position)['kind']
        if kind == 'formalization':
            continue
        if kind != 'research':   # a review, or an entry from before the tags existed
            after_review = kind == 'review'
            break
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


LEADS_RE = re.compile(r'<h4>Outside leads</h4>\s*<ul>(.*?)</ul>', re.S)
BRIDGES_RE = re.compile(r'<h4>Absurd bridges</h4>\s*<ul>(.*?)</ul>', re.S)
LEADS_MIN, BRIDGES_MIN = 3, 2
TEST_RE = re.compile(r'<strong>Test\.</strong>\s*(Passed|Falsified|Not run)\b')
OBSTACLE_RE = re.compile(r'<h4>Obstacle</h4>\s*<p>(.*?)</p>', re.S)
OBSTACLE_MIN = 80


def validate_leads(body, article, close):
    """AGENTS.md: a route review reaches outside the record's toolkit (user instructions, 25 September
    2026, after classical tools were proposed only once the user named their fields).  It lists Outside
    leads, from fields that study the open statement's objects, and Absurd bridges, from fields that never
    stood near them.  Each item records the outcome of its cheap test, run in the review cycle (user
    instruction, 25 September 2026): passed, falsified, or not run with the reason. Falsified items stay
    listed and count."""
    if not re.search(r'data-route-item="', body) or entry_tags(body, article)['kind'] != 'review':
        return
    # Leads and bridges exist to answer the line's current obstacle, not as items of their own (user,
    # 26 September 2026): the review states the obstacle, and every item says how it would resolve it.
    obstacle = OBSTACLE_RE.search(body, article, close)
    if obstacle is None or len(re.sub(r'<[^>]+>', '', obstacle.group(1)).strip()) < OBSTACLE_MIN:
        raise ValueError('A route review needs an <h4>Obstacle</h4> section, placed before its Outside leads, '
                         'whose paragraph states precisely the obstacle the line is stuck on (at least '
                         f'{OBSTACLE_MIN} characters). Choose the Outside leads and Absurd bridges to answer it (AGENTS.md)')
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
            return (ident, research, int(earlier.group(1))) if earlier else None
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
FOLLOWUP_OUTCOME = re.compile(r'<strong>Follow-up\.</strong>\s*(Developed|Continuing|Closed)\b')
BRIDGE_WINDOW = 3    # research entries after a review before a reminder to develop an open passed item

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


def open_bridges(body, articles):
    return open_items(body, articles)


def validate_bridges(body, article, close):
    """Passed Absurd bridges and passed Outside leads must be developed, not only listed (user, 26 September
    2026: six bridges had passed their smallest tests and none was explored further; later "Both should have
    followups").  A route review reports, under Bridge follow-up and Lead follow-up, the work done in its
    cycle on every passed item of earlier reviews on its route that no follow-up has closed.  After
    BRIDGE_WINDOW research entries since a review with none developing an open passed item (tagged
    data-bridge or data-lead="REVIEW-ANCHOR:N"), it prints a reminder."""
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
    status_of = registered_status() if status_of is None else status_of
    reports_cases = 'finite check' in entry_status(body, article).lower() or any(c.startswith(FINITE_PREFIXES) for c in claims)
    return (reports_cases and all(c.startswith(FINITE_PREFIXES) for c in claims)
            and not any(status_of.get(c) == 'refutation' for c in claims))


def registers_cases(body, article, status_of=None):
    """The entry registers a new finite check that is not a refutation (a decisive refutation is not
    case-list growth, so it is exempt)."""
    status_of = registered_status() if status_of is None else status_of
    return any(c.startswith(FINITE_PREFIXES) and status_of.get(c) != 'refutation' for c in entry_claims(body, article))


CASE_WINDOW, CASE_LIMIT = 5, 3


def entry_status(body, article):
    meta = body.find('<p class="entry-meta">', article)
    return re.sub(r'<[^>]*>', '', body[meta:body.find('</p>', meta)]).split('Produced by')[0]


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


def validate_marker(body, marker):
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
    validate_leads(body, article, close)
    validate_convergence(body, article, close)
    validate_bridges(body, article, close)
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
    from lead_queue import check
    relative = notebook.resolve().relative_to(root.resolve()).as_posix()
    head = subprocess.run(['git', 'show', f'HEAD:{relative}'], cwd=root, capture_output=True, text=True)
    check(head.stdout if head.returncode == 0 else None, notebook.read_text())


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
    pad = scratchpad(env, home)
    if pad is None:
        return
    files = [(p.stat().st_size, p) for p in pad.rglob('*') if p.is_file() and not p.is_symlink()]
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
    validate_marker(notebook.read_text(), marker)
    check_context(root, item["name"])  # Fail before stopping timing, archiving, or changing the notebook.
    validate_append_only(root)
    validate_queue(root, notebook)
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
