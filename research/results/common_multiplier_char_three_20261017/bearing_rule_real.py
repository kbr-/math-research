"""Run the finisher's same-item bearing rule on the common-multiplier record with this cycle's draft entry after it.

No statement tested: the timed run on real data of the item_root change to tools/finish-turn.py, printing the
verdict, the size read and each of the last four entries' resolved item.
"""
import importlib.util, re, time
spec = importlib.util.spec_from_file_location('FT', 'tools/finish-turn.py')
FT = importlib.util.module_from_spec(spec)
spec.loader.exec_module(FT)
body = open('research/branches/common-multiplier/notebook.html').read()
entry = open('research/results/common_multiplier_char_three_20261017/entry.html').read()
full = body + entry
progress = re.search(r'<p><strong>Goal progress\.</strong>.*?</p>', entry, re.S).group(0)
t = time.time()
try:
    FT.validate_bearing(full, full.rindex('<article'), progress, entry)
    print('passed')
except ValueError as e:
    print('refused:', e)
print(f'{len(full) / 1e6:.1f} MB in {time.time() - t:.2f} s')
for tag in re.findall(r'<article\b[^>]*>', full)[-4:]:
    m = re.search(FT.ITEM_TAG, tag)
    print(re.search(r'id="([^"]+)"', tag).group(1), m and FT.item_root(full, m.group(1)))
