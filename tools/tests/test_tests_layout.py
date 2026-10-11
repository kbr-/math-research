"""Every framework test file keeps its main guard last: a test class appended after the guard is run by the
suite's runner and never by a direct run of the file, as ten files had it on 11 October 2026."""
import re
import unittest
from pathlib import Path

TESTS = Path(__file__).resolve().parent
GUARD = re.compile(r'^if __name__\s*==\s*[\'"]__main__[\'"]\s*:', re.M)
DEFINITION = re.compile(r'^(?:class|def|async def) \w+', re.M)


def after_guard(source):
    """The names of the classes and functions defined after the file's last main guard."""
    guards = list(GUARD.finditer(source))
    return DEFINITION.findall(source[guards[-1].end():]) if guards else []


class TestsLayoutTest(unittest.TestCase):
    def test_nothing_is_defined_after_a_test_file_s_main_guard(self):
        late = {path.name: after_guard(path.read_text()) for path in sorted(TESTS.glob('test_*.py'))}
        self.assertEqual({name: found for name, found in late.items() if found}, {})

    def test_the_check_sees_a_class_after_the_guard(self):
        source = "class A: pass\n\nif __name__ == '__main__':\n    unittest.main()\n\nclass Late: pass\n"
        self.assertEqual(after_guard(source), ['class Late'])
        self.assertEqual(after_guard(source.split('class Late')[0]), [])
        self.assertEqual(after_guard('class A: pass\n'), [])


if __name__ == '__main__':
    unittest.main()
