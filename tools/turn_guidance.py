#!/usr/bin/env python3
"""Turn-start guidance: warn, before any work, about entries finish-turn.py would reject.

It reuses finish-turn.py's own predicates, so a warning here and a rejection there cannot drift
apart. It only prints; the hard checks stay in finish-turn.py.  Usage: turn_guidance.py [NOTEBOOK]"""
import importlib.util
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))


def finisher():
    spec = importlib.util.spec_from_file_location('finish_turn', ROOT / 'tools/finish-turn.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def guidance(body, ft):
    items = re.findall(r'data-route-item="([^"]+)"', body)
    if not items:
        return []
    record = body.find('<section id="research-record">')
    articles = [m.start() for m in re.finditer(r'<article\b', body) if m.start() > record]
    notes = ['Every research entry needs a <p><strong>General statement.</strong> ...</p> citing the '
             'registered claim ID (conj:, lem:, thm:, prop: or cor:) of its all-parameter claim.']
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
        elif streak == ft.REVIEW_PERIOD - 1:
            notes.append(f'Route {item}: {streak} research entries since the last route review; one more '
                         'research entry is allowed, then a route review is required.')
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
