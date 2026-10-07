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
    """The lead and bridge queue's state and what it requires of this cycle (tools/lead_queue.py)."""
    import lead_queue as lq
    found = lq.parse_tree(body)
    if found is None:
        return ['Lead queue: this notebook has none yet. Run python3 tools/lead_queue.py init NOTEBOOK.html and '
                'commit the section with this cycle\'s entry; the finisher requires it.']
    draining, nodes = found
    if not nodes:
        return ['Lead queue: empty. New passed leads and bridges of a review and the sub-ideas entries list go '
                'at its end.']
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
                f'{entries} entry must develop the head until the queue has {lq.FLOOR} items: {target}. End the '
                'entry with "<strong>Follow-up.</strong> Closed: <reason>", "Developed ..." or "Continuing ..." and '
                'update the queue: Closed and Developed remove the item. ' + rotation + rule]
    pressure = f'backpressure at {lq.CAP}' if lq.SETTINGS['backpressure'] else 'no backpressure here'
    return [f'Lead queue: {len(nodes)} items ({pressure}); {target}. A {entries} entry that develops a queue '
            'item takes the head or its first sub-idea, unless the user picked another, states its Follow-up '
            'outcome and updates the queue. ' + rule]


SQUEEZE = ('Squeeze each item, do not close it at its first usable result (user, 3 October 2026): Continuing '
           'while it still bears on an open statement, with the concrete next attempt named and made where '
           'possible; Developed only when no application to an open statement remains; Closed only for a reason '
           'the attempt found (restatement, inapplicability, falsification, supersession). Every item gets its own '
           'entry; batch triage is retired (user, 9 October 2026). Only '
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
    notes = ['Every research entry needs a <p><strong>General statement.</strong> ...</p> citing the '
             'registered claim ID (conj:, lem:, thm:, prop: or cor:) of its all-parameter claim.',
             'Computations: avoid expensive work and deeply nested loops in Python. Optimize and parallelize: write '
             'expensive computations as fast C or C++ kernels (OpenMP where it parallelizes) and use Python only for '
             'lightweight orchestration. Answer a guard refusal by optimizing, never by splitting the run.',
             'Before each computation, ask whether further computations are needed, or whether the results you '
             'already have are enough to propose a general statement and attempt to prove it. ' + CASES_PLEA,
             'Reach for other areas of mathematics yourself, without waiting for the user to name one: ask which '
             'fields study the objects of the open statement this cycle advances, and what their strongest '
             'theorems say about them (Outside leads), and also which fields never stood near these objects, since '
             'nobody thought of applying them here, from any field: mathematics, computer science, physics, chemistry '
             'or anything else (Absurd bridges). Every route review lists at least three '
             'Outside leads and two Absurd bridges, and runs their cheap tests in the same cycle, recording each '
             f'outcome (falsified items still count); outside draining it selects {ft.PICKS["Outside leads"]} '
             f'passed leads and {ft.PICKS["Absurd bridges"]} passed bridges (all passed items if fewer), '
             'marked with <li data-pick>; only those join the queue (user, 5 October 2026).']
    import lead_queue as lq
    if lq.is_draining(body):
        notes[-1] = lq.DRAINING_REVIEW_RULE
    notes += [note for note in (algebra_note(which), library_note(has)) if note]
    notes += queue_notes(body)
    worked = [a for a in articles if ft.entry_tags(body, a)['kind'] != 'formalization']
    active = ft.entry_tags(body, worked[-1])['route'] if worked else None
    for item in items:
        mine = [a for a in articles if ft.entry_tags(body, a)['route'] == item
                and ft.entry_tags(body, a)['kind'] != 'formalization']
        if not mine:
            continue
        last = mine[-1]
        tags = ft.entry_tags(body, last)
        research = [a for a in mine if ft.entry_tags(body, a)['kind'] == 'research'][-(ft.CASE_WINDOW - 1):]
        status_of = ft.registered_status(); cases = sum(ft.registers_cases(body, a, status_of) for a in research)
        if cases >= ft.CASE_LIMIT:
            notes.append(f'Route {item}: {cases} of the last '
                         f'{len(research)} research entries registered new finite checks; this cycle may not register '
                         'another one. Derive a general formula or proof instead.')
        if tags['kind'] == 'research' and ft.cases_only(body, last):
            notes.append(f'Route {item}: the last entry is a finite check without a proof or refutation. '
                         'Another finite-check-only research entry on this route will be rejected; this '
                         'cycle must attempt a proof or refutation of the General statement.')
        streak = 0
        for a in reversed(mine):
            kind = ft.entry_tags(body, a)['kind']
            if kind == 'review':
                break
            if kind == 'research':      # audits and other entries neither count nor end the scan, as in the finisher
                streak += 1
        if streak >= ft.REVIEW_PERIOD:
            notes.append(f'Route {item}: {streak} research entries since the last route review; the next '
                         'entry on this route must be a route review.')
            reference = ft.convergence_reference(body, len(body), item)
            if reference is None:
                notes.append(f'Route {item}: no review is {ft.CONVERGENCE_SPAN} or more research entries back, '
                             'so that review must be an ordinary route review, not goal-level.')
            else:
                ident, research, count = reference
                notes.append(f'Route {item}: review {ident}, {research} research entries back, declared '
                             f'{count} open items. If the review declares {count} or more, it must be goal-level '
                             '(data-scope="goal"); if fewer, it must be an ordinary route review.')
        elif streak == ft.REVIEW_PERIOD - 1:
            notes.append(f'Route {item}: {streak} research entries since the last route review; one more '
                         'research entry is allowed, then a route review is required.')
        elif item == active:   # dormant routes stay quiet
            notes.append(f'Route {item}: {streak} research entries since the last route review; the next review '
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
