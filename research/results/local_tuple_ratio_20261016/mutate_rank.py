"""No statement tested: a mutation check that the excerpt tool's new test fails when the statement ranking is
replaced by source order."""
import importlib.util, sys, unittest
from pathlib import Path
root = Path('/home/kbr/dev/math-auxiliary/tools')
sys.path.insert(0, str(root)); sys.path.insert(0, str(root / 'tests'))
import test_notebook_excerpt as t
real = importlib.util.spec_from_file_location
def patched(name, path, *a, **k):
    spec = real(name, path, *a, **k)
    if str(path).endswith('notebook-excerpt.py'):
        loader = spec.loader
        orig = loader.exec_module
        def exec_module(module):
            orig(module)
            module.statement_rank = lambda plain, ident, summary: (0, 0)
        loader.exec_module = exec_module
    return spec
importlib.util.spec_from_file_location = patched
suite = unittest.TestSuite([t.RecordStatementTest('test_claims_sharing_an_entry_each_get_their_own_statement_first')])
result = unittest.TextTestRunner(verbosity=0).run(suite)
print('mutant killed' if result.failures or result.errors else 'MUTANT SURVIVED')
