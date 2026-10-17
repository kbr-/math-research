"""Replay tools/route_judge.py's judge over the last eight research entries of the ultimate-matching notebook,
each read against today's living sections (a limitation: not the record as it stood when each was written)."""
import re
import sys
sys.path.insert(0, 'tools')
import route_judge

t = open('research/branches/ultimate-matching/notebook.html', encoding='utf-8').read()
arts = [m for m in re.finditer(r'<article id="([^"]+)"[^>]*data-kind="research"[^>]*>.*?</article>', t, re.S)][-8:]
print('Route judge replay, 17 October 2026: last 8 research entries against the current living sections.')
arts.append(re.search(r'(?s)<article id="(entry-x)".*?</article>', open(sys.argv[1]).read()))
for m in arts:
    try:
        v = route_judge.judge(m.group(0), t)
        print(m.group(1), v['verdict'], '|', v['reason'])
    except Exception as e:
        print(m.group(1), 'failed', e)
