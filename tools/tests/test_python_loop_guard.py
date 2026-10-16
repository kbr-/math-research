import tempfile
import unittest
from importlib.machinery import SourceFileLoader
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CS = SourceFileLoader('compute_sh', str(ROOT / 'compute.sh')).load_module()


class PythonLoopGuardTest(unittest.TestCase):
    def scan(self, files, entry='main.py'):
        with tempfile.TemporaryDirectory() as d:
            for name, text in files.items():
                (Path(d) / name).write_text(text)
            return [(Path(f).name, line, depth) for f, line, depth in CS.python_loop_offenders(Path(d) / entry, root=d)]

    def test_three_nested_loops_are_refused(self):
        src = 'def f(a):\n    for i in a:\n        for j in a:\n            for k in a:\n                pass\nf([1])\n'
        self.assertEqual(self.scan({'main.py': src}), [('main.py', 4, 3)])

    def test_comprehension_generators_count(self):
        self.assertEqual(self.scan({'main.py': 'a = [1]\nx = [(i, j, k) for i in a for j in a for k in a]\n'}), [('main.py', 2, 3)])

    def test_literal_bounded_loops_are_exempt(self):
        self.assertEqual(self.scan({'main.py': 'x = [(i, j, k) for i in range(3) for j in (1, 2) for k in range(4)]\n'}), [])

    def test_used_import_is_scanned_and_unused_is_not(self):
        lib = ('def slow(a):\n    for i in a:\n        for j in a:\n            for k in a:\n                pass\n'
               'def fast(a):\n    return len(a)\n')
        self.assertEqual(self.scan({'main.py': 'from lib import fast\nfast([1])\n', 'lib.py': lib}), [])
        self.assertEqual(self.scan({'main.py': 'from lib import slow\nslow([1])\n', 'lib.py': lib}), [('lib.py', 4, 3)])



class SeriesGuardTest(unittest.TestCase):
    def ev(self, *argsets, category='computation', prog='scan.py', exe='/usr/bin/python3', timeout=100):
        return [{'event': 'run_start', 'category': category, 'timeout_s': timeout, 'command': [exe, prog, *a]}
                for a in argsets]

    def six(self, **kw):
        return self.ev(*[[str(i)] for i in range(CS.MAX_SERIES_ARGSETS)], **kw)

    def test_further_new_argument_list_is_refused(self):
        self.assertIsNotNone(CS.series_error(self.six(), ['python3', 'scan.py', 'new'], 100))
        self.assertIsNotNone(CS.series_error(self.six(), ['python3', 'scan.py', 'new'], 600))    # long runs count
        self.assertIn('stating a general statement instead of running more cases',
                      CS.series_error(self.six(), ['python3', 'scan.py', 'new'], 100))
        self.assertIsNotNone(CS.series_error(self.six(exe='research/tmp/kernel', prog='x'),     # compiled programs count
                                             ['research/tmp/kernel', 'new'], 100))

    def test_repeats_and_small_series_are_allowed(self):
        self.assertIsNone(CS.series_error(self.six(), ['python3', 'scan.py', '2'], 100))
        self.assertIsNone(CS.series_error(self.ev(*[[str(i)] for i in range(CS.MAX_SERIES_ARGSETS - 1)]),
                                          ['python3', 'scan.py', 'new'], 100))

    def test_other_programs_and_categories_do_not_count(self):
        events = self.six(prog='other.py') + self.six(category='local_processing')
        self.assertIsNone(CS.series_error(events, ['python3', 'scan.py', 'new'], 100))

class LoopRefusalMemoryTest(unittest.TestCase):
    def test_a_refused_script_is_remembered_until_it_changes(self):
        # 16 October 2026: a refused script was rerun under the threshold instead of being optimized.
        with tempfile.TemporaryDirectory() as d:
            script, record = Path(d) / 's.py', Path(d) / 'refusals.txt'
            old = CS.LOOP_REFUSALS
            CS.LOOP_REFUSALS = record
            try:
                self.assertEqual(CS.loop_refusals(), set())
                record.write_text(f'{script.resolve()}\n')
                self.assertIn(str(script.resolve()), CS.loop_refusals())
                # the refusal lasts while the loops do, whatever else changes, and lifts when they go
                script.write_text('a = [1]\nfor i in a:\n    for j in a:\n        for k in a:\n            pass\n# x\n')
                self.assertTrue(CS.python_loop_offenders(script))
                script.write_text('import numpy\n')
                self.assertFalse(CS.python_loop_offenders(script))
            finally:
                CS.LOOP_REFUSALS = old


if __name__ == '__main__':
    unittest.main()
