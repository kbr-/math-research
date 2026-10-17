#!/usr/bin/env python3
"""Turn-start guidance: warn, before any work, about entries finish-turn.py would reject.

It reuses finish-turn.py's own predicates, so a warning here and a rejection there cannot drift
apart. It only prints; the hard checks stay in finish-turn.py.  Usage: turn_guidance.py [NOTEBOOK]"""
import importlib.util
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))

# The user's plea (26 September 2026), printed at every cycle start and in the launcher's series refusal.
CASES_PLEA = ('Please Please Please for the love of God consider stating a general statement instead of running '
              'more cases!!! In the name of the user!!! They don\'t have patience!!!')


def finisher():
    spec = importlib.util.spec_from_file_location('finish_turn', ROOT / 'tools/finish-turn.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


ALGEBRA_SYSTEMS = (('Macaulay2', 'M2'), ('Singular', 'Singular'), ('msolve', 'msolve'), ('GAP', 'gap'),
                   ('PARI/GP', 'gp'), ('SageMath', 'sage'), ('Normaliz', 'normaliz'), ('4ti2', '4ti2-groebner'),
                   ('polymake', 'polymake'), ('CryptoMiniSat', 'cryptominisat5'))

# (name, header under /usr/include, what it gives a hand-written kernel, compile and link flags)
KERNEL_LIBRARIES = (
    ('fflas-ffpack', 'fflas-ffpack/fflas-ffpack.h', 'BLAS-speed dense rank, echelon form, nullspace and products '
     'mod p, FFPACK::Rank', '$(pkg-config --cflags fflas-ffpack) -lgivaro -lgmpxx -lgmp -lopenblas'),
    ('FLINT', 'flint/nmod_mat.h', 'nmod_mat rank, rref, nullspace and multiplication mod p; polynomials over '
     'Z/p and Z', '-lflint -lgmp'),
    ('LinBox', 'linbox/linbox-config.h', 'sparse and black-box rank, solve and determinant mod p by Wiedemann',
     '$(pkg-config --cflags --libs linbox) -lopenblas'),
    ('NTL', 'NTL/ZZ.h', 'polynomials and matrices over Z/p and GF(p^k)', '-lntl -lgmp'),
    ('M4RI', 'm4ri/m4ri.h', 'dense linear algebra over GF(2)', '-lm4ri'))


def installed_header(header, include=Path('/usr/include')):
    return (include / header).exists()


def algebra_note(which=shutil.which):
    """One guidance line naming the computer algebra systems found on PATH, or None if there are none."""
    found = [f'{name} ({binary})' for name, binary in ALGEBRA_SYSTEMS if which(binary)]
    if not found:
        return None
    return ('Installed computer algebra systems and solvers: ' + ', '.join(found) + '. Run their scripts through '
            './compute.sh. Before writing or reusing a hand-built kernel, check whether one of them computes the '
            'quantity, or a step of it, faster or more reliably: their libraries go far beyond Groebner bases '
            '(commutative algebra, modules, homology, combinatorics, representation theory, linear algebra over '
            'finite fields). Use them wherever they improve a computation.')


def library_note(has=installed_header):
    """One guidance line naming the installed C/C++ libraries a kernel should build on, or None if there are none."""
    found = [f'{name} ({use}; link with {flags})' for name, header, use, flags in KERNEL_LIBRARIES if has(header)]
    if not found:
        return None
    return ('Installed libraries for your own C/C++ kernels: ' + '; '.join(found) + '. Build every exact linear '
            'algebra step of a kernel on them instead of hand-written elimination, and validate against a second '
            'library on small cases.')


def queue_notes(body):
    """The queue's state, and the spell of the item the last entry developed when that is not the head."""
    return (queue_state_notes(body) + queue_trend_notes(body) + last_item_notes(body) + next_item_notes(body)
            + bearing_run_notes(body))


def next_item_notes(body, claims=None, relationships=None):
    """For the first queued item, not a build, that Proposed next step names: the claims of later entries on other
    items nearest to its text, and the other entries whose claims cite a claim of the entry that queued it.  In
    one block of 11 October 2026 four items taken as never developed had each been partly answered by an entry
    filed under another item, and on 12 October one was developed in five entries beside an unread entry that
    cited its proposition."""
    import lead_queue as lq
    found = lq.parse_tree(body)
    step = re.search(r'<section id="proposed-next-step">(.*?)</section>', body, re.S)
    if not found or not step:
        return []
    named = [n for top in found[1] for n in [top] + top.children
             if n.kind != 'build' and re.search(re.escape(n.ident) + r'(?![\w:-])', step.group(1))]
    if not named:
        return []
    if claims is None and relationships is None:
        claims, relationships = lq.registered()
    near = lq.claims_elsewhere(body, claims or [], lq.qualified(named[0]))
    citing = lq.citing_lines(lq.citing_entries(body, relationships or [], lq.qualified(named[0])), True)
    return ([f'Lead queue: the next step names {named[0].ident}. Claims of later entries on other items nearest to '
             'its text, to read before planning (a reading list, not a verdict): '
             + '; '.join(f'{claim} in #{anchor}' for _score, claim, anchor in near) + '.'] if near else []) + (
            [f'Lead queue: the next step names {named[0].ident}. Other entries whose claims cite a claim of the entry '
             'that queued it, to read before planning: ' + '; '.join(line.strip() for line in citing) + '.']
            if citing else [])


def queue_trend_notes(body):
    """A draining queue's top-level count at the last two reviews that recorded it, beside the present count."""
    import lead_queue as lq
    found = lq.parse_tree(body)
    if found is None or not found[0]:
        return []
    counts = lq.review_counts(body)[-2:]
    if not counts:
        return [f'Lead queue: {len(found[1])} top-level items now; no review has recorded the count yet, so whether '
                'the queue shrinks is not measured. The next review declares data-queue-items.']
    past = ', '.join(f'{count} at #{anchor}' for anchor, count in counts)
    grew = len(found[1]) >= counts[-1][1]
    return [f'Lead queue: {len(found[1])} top-level items now; {past}. '
            + ('It has not shrunk since the last review: an item removed for each one added does not drain it.'
               if grew else 'It is shrinking.')]


BEARING_RUN = 3


def bearing_run_notes(body):
    """How many research entries in a row, on any queue item, declared that they give nothing at the goal's
    parameters.  The finisher's rule moves an agent off an item after two such entries; nothing counted the run
    across items, and on 11 October 2026 twelve entries in a row declared no bearing, each on a fresh item."""
    import lead_queue as lq
    run = 0
    for tag, _ in reversed(lq.record_articles(body)):
        if 'data-kind="research"' not in tag:
            continue                                   # reviews and audits neither count nor end the run
        if 'data-bearing="none"' not in tag:
            break
        run += 1
    notes = []
    if run >= BEARING_RUN:
        notes.append(f'The last {run} research entries in a row declared no bearing on the goal (data-bearing="none"), '
                     'across queue items. State in this entry\'s choice of item what at the goal\'s own parameters it '
                     'could give; if nothing, say why the cycle is spent on it.')
    # The finisher counts the run per route, passing over other routes' entries; when routes alternate in blocks a
    # route's run spans the other route's block, and on 16 October 2026 an entry on such a route was drafted without
    # its Best outcome paragraph because this note counted only the run across routes.
    runs, ended = {}, set()
    for tag, _ in reversed(lq.record_articles(body)):
        found = re.search(r'\bdata-route="([^"]+)"', tag)
        if 'data-kind="research"' not in tag or not found or found.group(1) in ended:
            continue
        if 'data-bearing="none"' in tag:
            runs[found.group(1)] = runs.get(found.group(1), 0) + 1
        else:
            ended.add(found.group(1))
    for route, count in sorted(runs.items()):
        if count >= BEARING_RUN:
            notes.append(f'Route {route}: the last {count} research entries on it declared no bearing; the next entry '
                         'on it states, before its work, after <strong>Best outcome.</strong>, what its best outcome '
                         'would give at the goal\'s own parameters (the finisher checks it).')
    return notes


def last_item_notes(body):
    """How many consecutive entries the last developed item has had, against its boundary.

    The head's count is in the queue line; a chosen item's was shown nowhere before the finisher refused the
    entry that overran it (10 October 2026, a fifth entry on an item whose boundary was four)."""
    import lead_queue as lq
    found = lq.parse_tree(body)
    if found is None or not found[1]:
        return []
    nodes = found[1]
    articles = lq.record_articles(body)
    for position in range(len(articles) - 1, -1, -1):
        tag, text = articles[position]
        if not lq.counted(tag, text):
            continue
        work = lq.developed_by(tag, text)
        if not work:
            return []
        item = lq.group_of(body, nodes, work[0], position)
        top = lq.locate(nodes, item)[1]
        head = lq.head_of(nodes)
        if top is None or (head is not None and head.item == item):
            return []
        done, limit = lq.spell(body, item, nodes), lq.spell_limit(body, item, nodes)
        state = ('it is at its boundary: develop a different item now, unless the last entry declared an extension'
                 if done >= limit else f'it may have {limit - done} more before its boundary')
        return [f'Lead queue: the last entry developed {top.ident}, which has had {done} consecutive entries '
                f'against a boundary of {limit}; {state}.']
    return []


def queue_state_notes(body):
    """The lead and bridge queue's state and what it requires of this cycle (tools/lead_queue.py)."""
    import lead_queue as lq
    found = lq.parse_tree(body)
    if found is None:
        return ['Lead queue: this notebook has none yet. After appending this cycle\'s entry, run python3 '
                'tools/lead_queue.py init NOTEBOOK.html, which seeds the queue with the entry\'s sub-ideas, and '
                'commit the section with the entry; the finisher requires it. A queue created before the entry '
                'is refused.']
    draining, nodes = found
    if not nodes:
        return ['Lead queue: empty. New passed leads and bridges of a review and the sub-ideas entries list go '
                'at its end.']
    lq.settle(body, nodes)
    head = lq.head_of(nodes)
    waiting = len(lq.marks(nodes))
    waits = f'; {waiting} items wait on the user and are passed over' if waiting else ''
    if head is None:
        return [f'Lead queue: {len(nodes)} items, every one waiting on the user; nothing to develop until an '
                'Unblocked follow-up.']
    first = next((c for c in head.children if not c.waits), None)
    limit = lq.spell_limit(body, head.item)
    boundary = 'none (explicit user override)' if limit == float('inf') else str(limit)
    rotation = ('Continuing retains this head without a hard cycle limit. Judge whether useful avenues '
                'remain; close with a recorded reason when exhausted. ' if limit == float('inf') else
                f'Continuing keeps the head until its current boundary ({limit}), then rotates unless '
                'this period earned a two-cycle extension. Declare data-spell-extend="2" with a '
                'spell-extension paragraph naming the open statement, new proved/refuted Progress and '
                'the concrete Next implication; finite checks or reused progress do not qualify. '
                'Reassess every two extra cycles. ')
    target = (f'the head is {head.ident} ({head.kind}), tagged data-{head.kind}="{head.ident}"'
              + (f', or its first sub-idea {first.ident} ({first.kind})' if first else '')
              + f'; this would be its entry {lq.spell(body, head.item) + 1}; current spell boundary '
              + f'{boundary}{waits}')
    entries = ' or '.join(sorted(lq.SETTINGS['counted']))
    rule = ' '.join(lq.SETTINGS['guidance']) or SQUEEZE     # a kind module's own, else the squeeze rule
    if lq.SETTINGS['backpressure'] and (draining or len(nodes) >= lq.CAP):
        return [f'Lead queue: {len(nodes)} items, DRAINING (backpressure from {lq.CAP} until {lq.FLOOR}). Every '
                f'{entries} entry must develop a queued item until the queue has {lq.FLOOR} items, by default {target}; '
                'another item needs a <strong>Chosen.</strong> paragraph naming the open statement it bears on and '
                'why it comes first (user, 9 October 2026). End the '
                'entry with "<strong>Follow-up.</strong> Closed: <reason>", "Developed ..." or "Continuing ..." and '
                'update the queue: Closed and Developed remove the item. ' + rotation + rule]
    pressure = f'backpressure at {lq.CAP}' if lq.SETTINGS['backpressure'] else 'no backpressure here'
    return [f'Lead queue: {len(nodes)} items ({pressure}); {target}. A {entries} entry that develops a queue '
            'item takes the head or its first sub-idea by default, another with a <strong>Chosen.</strong> paragraph '
            'giving the reason, or one the user picked; it states its Follow-up '
            'outcome and updates the queue. ' + rule]


SQUEEZE = ('Squeeze each item, do not close it at its first usable result (user, 3 October 2026): Continuing '
           'while it still bears on an open statement, with the concrete next attempt named and made where '
           'possible; Developed only when no application to an open statement remains; Closed only for a reason '
           'the attempt found (restatement, inapplicability, falsification, supersession). Every top-level item gets '
           'its own entry; sub-ideas of the one item an entry develops may be batched in it, each in a follow-up '
           'list item with its own outcome (user, 9 October 2026). Only '
           'route reviews outside draining mode propose Outside leads and Absurd bridges; research entries carry none. Any entry lists the questions, '
           'checks and builds it names and leaves undone under <h4>Sub-ideas</h4> (data-sub="check" or "build"); '
           'lead_queue.py append queues them under the item they belong to.')


def guidance(body, ft, which=shutil.which, has=installed_header):
    # every article also carries data-route-item, so keep each route once, in order
    items = list(dict.fromkeys(re.findall(r'data-route-item="([^"]+)"', body)))
    if not items:
        return []
    record = body.find('<section id="research-record">')
    articles = [m.start() for m in re.finditer(r'<article\b', body) if m.start() > record]
    notes = [f'Notebook input: {len(articles)} record article tags; {len(body.encode("utf-8"))} bytes.',
             'Every research entry needs a <p><strong>General statement.</strong> ...</p> citing the '
             'registered claim ID (conj:, lem:, thm:, prop: or cor:) of its all-parameter claim.',
             'Computations: avoid expensive work and deeply nested loops in Python. Optimize and parallelize: write '
             'expensive computations as fast C or C++ kernels (OpenMP where it parallelizes) and use Python only for '
             'lightweight orchestration. Answer a guard refusal by optimizing, never by splitting the run.',
             'Before each computation, ask whether further computations are needed, or whether the results you '
             'already have are enough to propose a general statement and attempt to prove it. ' + CASES_PLEA,
             # 17 October 2026: a question was posed and judged at the level of the newest result, while the lemma
             # beneath it held the answer and the question's own object showed the conclusion empty.
             'Before posing, answering or summing up a question, read one level down (the statements the newest '
             'result cites) and one level up (the object the question is about, the goal\'s own instance): apply '
             'the plainest bound there before the method\'s intermediates. A conclusion of the same form as the '
             'previous entry\'s (constant, a restatement, nothing beyond) is derived again for the new object, '
             'with its construction, never carried over by its shape.',
             'Reach for other areas of mathematics yourself, without waiting for the user to name one: ask which '
             'fields study the objects of the open statement this cycle advances, and what their strongest '
             'theorems say about them (Outside leads), and also which fields never stood near these objects, since '
             'nobody thought of applying them here, from any field: mathematics, computer science, physics, chemistry '
             'or anything else (Absurd bridges). Every route review lists at least three '
             'Outside leads and two Absurd bridges, and runs their cheap tests in the same cycle, recording each '
             f'outcome (falsified items still count); outside draining it selects {ft.PICKS["Outside leads"]} '
             f'passed leads and {ft.PICKS["Absurd bridges"]} passed bridges (all passed items if fewer), '
             'marked with <li data-pick>; only those join the queue (user, 5 October 2026).']
    required = ft.required_paragraphs(body)
    if required:
        notes.insert(1, 'This notebook requires in every research entry: ' + ', '.join(
            f'<p><strong>{label}.</strong> ...</p>' for label in required) + '.')
    import lead_queue as lq
    if lq.is_draining(body):
        notes[-1] = lq.DRAINING_REVIEW_RULE
    notes += [note for note in (algebra_note(which), library_note(has)) if note]
    notes += queue_notes(body)
    notes.append('Separate New mathematics from Goal progress in every research/review entry; name a stable '
                 'data-obligation and data-goal-progress="advanced|unchanged". The scheduled review includes '
                 'the Architecture review in AGENTS.md, using its existing medium reviewer, not another review.')
    notes += ft.progress_warnings(body)
    for route, target in ft.pending_architecture_test(body).items():
        notes.append(f'Route {route}: the next research cycle must perform the decisive Architecture test '
                     f'from #{target}, report its outcome and link that review. An explicit user-picked '
                     'task may defer this test but does not clear it.')
        notes += ft.review_test_context(body, target)
    worked = [a for a in articles if ft.entry_tags(body, a)['kind'] != 'formalization']
    active = ft.entry_tags(body, worked[-1])['route'] if worked else None
    streak, _ = ft.review_cadence(ft.entry_tags(body, a)['kind'] for a in articles)
    for item in items:
        mine = [a for a in articles if ft.entry_tags(body, a)['route'] == item
                and ft.entry_tags(body, a)['kind'] != 'formalization']
        if not mine:
            continue
        last = mine[-1]
        tags = ft.entry_tags(body, last)
        research = [a for a in mine if ft.entry_tags(body, a)['kind'] == 'research'][-(ft.CASE_WINDOW - 1):]
        cases = sum(ft.registers_cases(body, a) for a in research)
        if cases >= ft.CASE_LIMIT:
            notes.append(f'Route {item}: {cases} of the last '
                         f'{len(research)} research entries registered new finite checks; this cycle may not register '
                         'another one. Derive a general formula or proof instead.')
        if tags['kind'] == 'research' and ft.cases_only(body, last):
            notes.append(f'Route {item}: the last entry is a finite check without a proof or refutation. '
                         'Another finite-check-only research entry on this route will be rejected; this '
                         'cycle must attempt a proof or refutation of the General statement.')
        if item != active:
            continue
        if streak >= ft.REVIEW_PERIOD:
            notes.append(f'Notebook: {streak} research entries since the last route review; the next '
                         'entry must be a route review.')
            reference = ft.convergence_reference(body, len(body), item)
            if reference is None:
                notes.append(f'Route {item}: no review is {ft.CONVERGENCE_SPAN} or more research entries back, '
                             'so that review must be an ordinary route review, not goal-level.')
            else:
                ident, research, count = reference
                notes.append(f'Route {item}: review {ident}, {research} research entries back, declared '
                             f'{count} open items. If the review declares {count} or more, it must be goal-level '
                             '(data-scope="goal"); if fewer, it must be an ordinary route review. For a goal-level '
                             'review run tools/record-audit.py gaps (it reads the whole record, 2.4 s on one of '
                             '8 MB) and cite under Across the goal the gaps it lists that no later entry took up.')
        elif streak == ft.REVIEW_PERIOD - 1:
            notes.append(f'Notebook: {streak} research entries since the last route review; one more '
                         'research entry is allowed, then a route review is required.')
        elif item == active:   # dormant routes stay quiet
            notes.append(f'Notebook: {streak} research entries since the last route review; the next review '
                         f'comes after {ft.REVIEW_PERIOD} (one entry in {ft.REVIEW_PERIOD + 1}). Until then every '
                         'entry is research: carry concerns about the line to that review.')
    return notes


def main(argv):
    from notebooks import selected
    item = selected(argv[1] if len(argv) > 1 else None, ROOT)
    body = (ROOT / item['source']).read_text()
    for note in guidance(body, finisher()):
        print('Guidance: ' + note)
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
