"""Statement tested: on every notebook of the repository (main and each side notebook), living_and_toc gives the
same living prefix, contents table and omitted count as the full parse.
Refuted by: any notebook printed with a False or with unequal omitted counts.
Possible because: the regex scan could count an article tag the HTML parser does not see as an article."""
import importlib.util, sys, time
from pathlib import Path
root = Path('/home/kbr/dev/math-auxiliary')
sys.path.insert(0, str(root / 'tools'))
spec = importlib.util.spec_from_file_location('ex', root / 'tools/notebook-excerpt.py')
ex = importlib.util.module_from_spec(spec); spec.loader.exec_module(ex)
paths = [root / 'notebook.html'] + sorted((root / 'research/branches').glob('*/notebook.html'))
bad = 0
for path in paths:
    source = path.read_text()
    t0 = time.perf_counter(); book = ex.Notebook(source)
    full = (source[:book.anchor('research-record')['start']],) + book.toc(tail=10); t1 = time.perf_counter()
    fast = ex.living_and_toc(source, 10); t2 = time.perf_counter()
    same = full == fast
    bad += not same
    print(f'{path.relative_to(root)}: bytes {len(source)} prefix {full[0] == fast[0]} toc {full[1] == fast[1]} '
          f'omitted {full[2]} {fast[2]} full {t1 - t0:.2f} s tail {t2 - t1:.2f} s')
print(f'{len(paths)} notebooks, {bad} differing')
