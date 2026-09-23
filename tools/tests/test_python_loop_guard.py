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


if __name__ == '__main__':
    unittest.main()
