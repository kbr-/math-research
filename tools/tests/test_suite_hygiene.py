"""No test module holds a test class defined in another module.

unittest collects every TestCase in a module's namespace, so `from test_other import SomeTest` reruns all of
SomeTest's tests in the importing module: on 16 October 2026 tools/tests/test_side_workflow.py ran fifteen finisher
tests a second time this way, and a subclass of the same class ran them a third time, 12 s of the suite's CPU. Borrow
a fixture through the module instead (`import test_other as fixtures; setUp = fixtures.SomeTest.setUp`).
"""
import importlib
import inspect
import pathlib
import sys
import unittest

HERE = pathlib.Path(__file__).resolve().parent


def suite_module(name):
    """Whether `name` is a module of this suite; classes from tests/, which test_site imports deliberately so
    that they run at all (AGENTS.md), are not."""
    return (HERE / f'{name}.py').exists()


def foreign_tests(module, in_suite=suite_module):
    """Names of TestCase classes in `module`'s namespace that another module of this suite defines and that have
    tests, or that inherit tests such a module defines."""
    suite_module = in_suite
    found = []
    for name, value in vars(module).items():
        if not (inspect.isclass(value) and issubclass(value, unittest.TestCase)):
            continue
        tests = unittest.defaultTestLoader.getTestCaseNames(value)
        if not tests:
            continue
        if value.__module__ != module.__name__:
            if suite_module(value.__module__):
                found.append(f'{name} (imported from {value.__module__})')
            continue
        inherited = [t for t in tests if t not in vars(value)
                     and any(t in vars(base) and base.__module__ != module.__name__ and suite_module(base.__module__)
                             for base in value.__mro__[1:])]
        if inherited:
            found.append(f'{name} (inherits {len(inherited)} tests from another module)')
    return found


class SuiteHygiene(unittest.TestCase):
    def test_no_module_reruns_another_module_s_tests(self):
        sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE.parent))
        problems = {}
        for path in sorted(HERE.glob('test_*.py')):
            module = importlib.import_module(path.stem)
            if found := foreign_tests(module):
                problems[path.name] = found
        self.assertEqual(problems, {}, 'test classes collected outside their own module rerun their tests')

    def test_the_check_sees_an_imported_class_and_an_inherited_one(self):
        import types
        other = types.ModuleType('other_tests')
        class Borrowed(unittest.TestCase):
            def test_x(self): pass
        Borrowed.__module__ = 'other_tests'
        here = types.ModuleType('here_tests')
        class Child(Borrowed):
            def test_own(self): pass
        Child.__module__ = 'here_tests'
        class Clean(unittest.TestCase):
            setUp = Borrowed.setUp
            def test_own(self): pass
        Clean.__module__ = 'here_tests'
        here.Borrowed, here.Child, here.Clean = Borrowed, Child, Clean
        found = foreign_tests(here, in_suite=lambda name: name == 'other_tests')
        self.assertEqual(len(found), 2, found)
        self.assertTrue(any('imported' in f for f in found) and any('inherits 1' in f for f in found))


if __name__ == '__main__':
    unittest.main()
