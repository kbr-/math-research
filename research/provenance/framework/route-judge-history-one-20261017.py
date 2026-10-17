"""No statement tested: one history replay of tools/route_judge.py, the conditional-push entry against the notebook
as committed just before the commit that added it."""
import re
import subprocess
import sys
sys.path.insert(0, 'tools')
import route_judge

NB = 'research/branches/ultimate-matching/notebook.html'
ANCHOR = 'entry-2026-10-17-conditional-push-obstruction'
commit = subprocess.run(['git', 'log', '--format=%H', '-S', f'id="{ANCHOR}"', '--reverse', '--', NB],
                        capture_output=True, text=True).stdout.split()[0]
before = subprocess.run(['git', 'show', f'{commit}^:{NB}'], capture_output=True, text=True).stdout
after = subprocess.run(['git', 'show', f'{commit}:{NB}'], capture_output=True, text=True).stdout
entry = re.search(rf'<article id="{ANCHOR}".*?</article>', after, re.S).group(0)
v = route_judge.judge(entry, before)
print(f'History replay, 17 October 2026: {ANCHOR} (added in {commit[:9]}) against the notebook at its parent:')
print(v['verdict'], '|', v['shortest'], '|', v['reason'])
