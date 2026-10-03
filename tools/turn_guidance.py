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
    found = lq.parse(body)
    if found is None:
        return ['Lead queue: this notebook has none yet. Run python3 tools/lead_queue.py init NOTEBOOK.html and '
                'commit the section with this cycle\'s entry; the finisher requires it.']
    draining, queue = found
    if not queue:
        return ['Lead queue: empty. New passed leads and bridges of a review go at its end.']
    kind, ident = queue[0]
    head = (f'the head is {ident} ({kind}), tagged data-{kind}="{ident}"; this would be its entry '
            f'{lq.spell(body, queue[0]) + 1} of at most {lq.SPELL} in a row')
    if draining or len(queue) >= lq.CAP:
        return [f'Lead queue: {len(queue)} items, DRAINING (backpressure from {lq.CAP} until {lq.FLOOR}). Every '
                f'research entry must develop the head until the queue has {lq.FLOOR} items: {head}. End the '
                'entry with "<strong>Follow-up.</strong> Closed: <reason>", "Developed ..." or "Continuing ..." and '
                'update the queue: Closed and Developed remove the item; Continuing keeps the head until its '
                f'{lq.SPELL}th consecutive entry, then moves it to the tail. ' + SQUEEZE]
    return [f'Lead queue: {len(queue)} items (backpressure at {lq.CAP}); {head}. A research entry that develops '
            'a queue item must take the head, state its Follow-up outcome and update the queue. ' + SQUEEZE]


SQUEEZE = ('Squeeze each item, do not close it at its first usable result (user, 3 October 2026): Continuing '
           'while it still bears on an open statement, with the concrete next attempt named and made where '
           'possible; Developed only when no application to an open statement remains; Closed only for a reason '
           'the attempt found (restatement, inapplicability, falsification, supersession). Alternatively settle up '
           'to four head items in one entry under <h4>Queue triage</h4> (then lead_queue.py triage), each with the '
           'care it would get alone: 80+ words of what was checked, evidence cited, Closed or Developed only. A '
           'research entry may add one Outside lead and one Absurd bridge of its own.')


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
             'outcome (falsified items still count).']
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
            if ft.entry_tags(body, a)['kind'] != 'research':
                break
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
