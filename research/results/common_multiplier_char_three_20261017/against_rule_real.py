"""Run the finisher's no-bearing backstop on the real common-multiplier record for work already done.

No statement tested: the timed run on real data of the "Against the rule." checkpoint path in tools/finish-turn.py,
on the record before the characteristic-three entry, with that entry stripped of its user pick: bare, with the
paragraph, and with the paragraph and a spell extension.
"""
import importlib.util
import re
import subprocess
import sys
import time

sys.path.insert(0, 'tools')
spec = importlib.util.spec_from_file_location('FT', 'tools/finish-turn.py')
FT = importlib.util.module_from_spec(spec)
spec.loader.exec_module(FT)
body = subprocess.run(['git', 'show', 'HEAD~1:research/branches/common-multiplier/notebook.html'],
                      capture_output=True, text=True, check=True).stdout
entry = open('research/results/common_multiplier_char_three_20261017/entry.html').read()
entry = entry.replace(' data-picked="user"', '')
progress = re.search(r'<p><strong>Goal progress\.</strong>.*?</p>', entry, re.S).group(0)
against = ('<p><strong>Against the rule.</strong> The work began before compute.sh start named the item; '
           'that stage should have stopped it.</p>')
t = time.time()
for label, text in (('bare', entry), ('with Against the rule', entry.replace('</article>', against + '</article>')),
                    ('with it and a spell extension', entry.replace('</article>', against + '</article>')
                     .replace('<article ', '<article data-spell-extend="2" ', 1))):
    full = body + text
    try:
        FT.validate_bearing(full, full.rindex('<article'), progress, text)
        print(f'{label}: passed')
    except ValueError as e:
        print(f'{label}: refused: {str(e)[:120]}')
print(f'{len(body) / 1e6:.1f} MB record, {time.time() - t:.2f} s')
