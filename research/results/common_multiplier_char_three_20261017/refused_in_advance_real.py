"""Run the no-bearing item rule at its three stages on the real common-multiplier record.

No statement tested: the timed run on real data of lead_queue.no_bearing_excluded as used by the start guidance
(tools/turn_guidance.py), the next-step check (tools/notebook-append.py) and the finisher (tools/finish-turn.py),
on the record before this cycle's entry, the previous cycle's next step, and this cycle's entry with and without
data-picked="user".
"""
import importlib.util
import re
import sys
import time

sys.path.insert(0, 'tools')


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


import lead_queue
guide = load('turn_guidance', 'tools/turn_guidance.py')
append = load('notebook_append', 'tools/notebook-append.py')
FT = load('FT', 'tools/finish-turn.py')
body = open('research/branches/common-multiplier/notebook.html').read()
t = time.time()
print(f'{len(body) / 1e6:.1f} MB record; excluded routes:', lead_queue.no_bearing_excluded(body))
print('start guidance:', [n for n in guide.bearing_run_notes(body) if 'REFUSED' in n])
nxt = open('research/results/common_multiplier_onto_weak_20261017/next.html').read()
try:
    append.refuse_excluded_item(body, nxt)
    print('previous next step: passed')
except ValueError as e:
    print('previous next step: refused:', e)
entry = open('research/results/common_multiplier_char_three_20261017/entry.html').read()
progress = re.search(r'<p><strong>Goal progress\.</strong>.*?</p>', entry, re.S).group(0)
for label, text in (('as drafted', entry.replace(' data-picked="user"', '')),
                    ('user-picked', entry if 'data-picked="user"' in entry
                     else entry.replace('<article ', '<article data-picked="user" ', 1))):
    full = body + text
    try:
        FT.validate_bearing(full, full.rindex('<article'), progress, text)
        print(f'finisher, {label}: passed')
    except ValueError as e:
        print(f'finisher, {label}: refused:', e)
print(f'{time.time() - t:.2f} s')
