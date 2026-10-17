"""No statement tested: replay of compute.sh's scripts_with_unquoted_escape over every script under research/results,
with its date filter off, listing each sentence it would refuse."""
import glob
from importlib.machinery import SourceFileLoader
CS = SourceFileLoader('compute_sh', 'compute.sh').load_module()
CS.UNQUOTED_ESCAPE_FROM = 0
paths = [p for p in glob.glob('research/results/**/*', recursive=True) if p.endswith(CS.REFUTATION_SUFFIXES)]
found = CS.scripts_with_unquoted_escape(['python3', *paths])
print(f'Replay, 17 October 2026: {len(paths)} scripts under research/results read, {len(found)} sentences matched, '
      f'in {len({a for a, _ in found})} scripts:')
for arg, sentence in found:
    print('-', arg, '|', sentence[:300])
