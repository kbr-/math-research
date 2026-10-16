#!/usr/bin/env python3
"""Flag a new framework test that cannot fail: one that still passes when every tool function it calls is
replaced by a stub that returns a wrong value or refuses.

Usage: tools/test_can_fail.py [--staged | --base REV | --all] [FILE::Class.method ...]

For each test named, or each test function a commit adds (with --staged, the staged diff of
tools/tests/test_*.py against HEAD; with --base, the working tree against REV, every test of an untracked
test file counting as added), the tool finds the calls MODULE.FUNCTION( in the test's own source where MODULE
is a module object of the test file loaded from under tools/. It runs the test once with those functions
watched: a test failing as it stands is not judged; a function that returned a value gets two stubs, a
truthy and a falsy value equal to nothing; one that only returned None (a validator whose effect is to refuse
or not) gets a stub that raises. A test that passes under every stub of every such function does not depend
on what the tool does, and is flagged; a test that calls no tool function this way is not judged. Exit
status 1 when a test is flagged.

On 16 October 2026 a test of the skeleton check compared an immutable string with itself, so it could not
fail; only the reviewer caught it, before that commit, so the test is not in the history and the check's
own test rebuilds its shape. Not caught: tests that reach the tool through a subprocess, a class instance,
a name imported with "from TOOL import f" or a function the test file defines; tests whose assertions depend
on the tool only through side effects a stub does not change (a file the real function would have written);
a test that ignores one function's result while asserting on another's, since a flag needs every stubbed
function to survive. False flags possible: a test asserting only assertNotEqual on a result (the wrong value
is unequal to everything), or catching a broad exception around a validator (the raising stub's error).
In --staged mode the test files are read as staged (git show :PATH), the version whose lines the staged
diff numbers; the test itself is still loaded and run from the working tree, so the test judged can
differ from the staged one.
"""
import argparse
import ast
import importlib.util
import inspect
import io
import re
import subprocess
import sys
import types
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / 'tools'
CALL = re.compile(r'\b([A-Za-z_]\w*)\.([A-Za-z_]\w*)\(')
ADDED_TEST = re.compile(r'^\+\s*def (test_\w+)\(self', re.M)


class Wrong:
    """A value equal to nothing, so an assertion about the stubbed function's result fails; `truth` sets its
    truth value, and both are tried, since assertTrue and assertFalse each accept one of them (on the whole
    suite of 16 October 2026 a truthy one alone flagged four sound assertTrue tests)."""

    def __init__(self, truth):
        self.truth = truth

    def __eq__(self, other):
        return False

    def __bool__(self):
        return self.truth

    __hash__ = object.__hash__


def load(path):
    """The test module at `path`, loaded as the suite loads it, with tools/ and tools/hooks on the path."""
    for extra in (str(TOOLS / 'hooks'), str(TOOLS), str(Path(path).resolve().parent)):
        if extra not in sys.path:
            sys.path.insert(0, extra)
    spec = importlib.util.spec_from_file_location(Path(path).stem, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def tool_calls(test_module, method, tools=TOOLS):
    """[(module object, function name)] for the calls MODULE.FUNCTION( in `method`'s source where MODULE is a
    module of `test_module` loaded from under tools/ and FUNCTION one of its callables, each once."""
    source = inspect.getsource(method)
    found = []
    for name, function in dict.fromkeys(CALL.findall(source)):
        target = getattr(test_module, name, None)
        origin = getattr(target, '__file__', None) or ''
        if (isinstance(target, types.ModuleType) and Path(origin).resolve().is_relative_to(tools)
                and 'tests' not in Path(origin).resolve().relative_to(tools).parts
                and callable(getattr(target, function, None))):
            found.append((target, function))
    return found


def passes(case):
    result = unittest.TestResult()
    case.run(result)
    return result.wasSuccessful()


def check(path, test_name, tools=TOOLS):
    """(flagged, [function names stubbed]) for the test `Class.method` of the test file at `path`."""
    module = load(path)
    class_name, method_name = test_name.split('.', 1)
    cls = getattr(module, class_name)
    calls = tool_calls(module, getattr(cls, method_name), Path(tools).resolve())
    if not calls:
        return False, []
    # One run with the real functions watched: a test that fails as it stands is not judged, and a function that
    # only ever returns None (a validator whose effect is to refuse or not) is stubbed to refuse, the others to
    # return a wrong value. A test of a validator's passing path rightly ignores its return value and must still
    # fail when the validator refuses; a raising stub for every function would fail every test that calls one.
    valued = {}
    patches = []
    for target, function in calls:
        real = getattr(target, function)

        def watched(*args, _real=real, _key=(target, function), **kwargs):
            value = _real(*args, **kwargs)
            valued[_key] = valued.get(_key, False) or value is not None
            return value
        patches.append(mock.patch.object(target, function, watched))
    for patch in patches:
        patch.start()
    try:
        sound = passes(cls(method_name))
    finally:
        for patch in patches:
            patch.stop()
    if not sound:
        return False, []

    def raising(*args, **kwargs):
        raise RuntimeError('stubbed to refuse')

    survived = []
    for target, function in calls:
        stubs = ([lambda *a, **k: Wrong(True), lambda *a, **k: Wrong(False)] if valued.get((target, function))
                 else [raising])
        if all(_passes_with(target, function, stub, cls, method_name) for stub in stubs):
            survived.append(f'{target.__name__}.{function}')
    return len(survived) == len(calls), [f'{t.__name__}.{f}' for t, f in calls]


def _passes_with(target, function, stub, cls, method_name):
    with mock.patch.object(target, function, stub):
        return passes(cls(method_name))


def enclosing_tests(text):
    """{line: 'Class.method'} for every test method of the file text, by the line of its definition."""
    found = {}
    for node in ast.parse(text).body:
        if isinstance(node, ast.ClassDef):
            for item in node.body:
                if isinstance(item, ast.FunctionDef) and item.name.startswith('test_'):
                    found[item.lineno] = f'{node.name}.{item.name}'
    return found


def added_tests(staged=True, base='HEAD'):
    """['FILE::Class.method'] for the test functions the diff adds to tools/tests/test_*.py, each placed by the
    line its definition has in the new file, so two classes with a method of the same name are told apart."""
    command = ['git', 'diff', '-U0'] + (['--cached'] if staged else [base]) + ['--', 'tools/tests/']
    diff = subprocess.run(command, cwd=ROOT, capture_output=True, text=True).stdout
    found = []
    for part in re.split(r'^diff --git ', diff, flags=re.M)[1:]:
        file = re.search(r'^\+\+\+ b/(\S+)', part, re.M)
        if not file or not re.match(r'tools/tests/test_\w+\.py$', file.group(1)):
            continue
        path = ROOT / file.group(1)
        if staged:      # the staged version, whose lines the hunks number
            shown = subprocess.run(['git', 'show', f':{file.group(1)}'], cwd=ROOT, capture_output=True, text=True)
            tests = enclosing_tests(shown.stdout) if shown.returncode == 0 else {}
        else:
            tests = enclosing_tests(path.read_text()) if path.exists() else {}
        line = 0
        for row in part.splitlines():
            hunk = re.match(r'^@@ -\d+(?:,\d+)? \+(\d+)', row)
            if hunk:
                line = int(hunk.group(1))
                continue
            if row.startswith('+') and not row.startswith('+++'):
                if ADDED_TEST.match(row) and line in tests:
                    found.append(f'{file.group(1)}::{tests[line]}')
                line += 1
    if not staged:
        # A new test file not yet added: every test in it is new (a commit check runs before a chained git add).
        # One not meant for the commit is counted too, a limit of checking before the commit is staged.
        untracked = subprocess.run(['git', 'ls-files', '--others', '--exclude-standard', '--', 'tools/tests/'],
                                   cwd=ROOT, capture_output=True, text=True).stdout.split()
        for name in untracked:
            path = ROOT / name
            if re.match(r'tools/tests/test_\w+\.py$', name) and path.is_file():
                found += [f'{name}::{test}' for test in enclosing_tests(path.read_text()).values()]
    return found


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('tests', nargs='*', help='FILE::Class.method')
    parser.add_argument('--staged', action='store_true', help='the tests the staged diff adds')
    parser.add_argument('--base', help='the tests the working tree adds against this revision')
    parser.add_argument('--all', action='store_true', help='every test of tools/tests/test_*.py, to count the '
                        'flags on tests that are known to be sound and the time of the whole run')
    args = parser.parse_args(argv)
    tests = list(args.tests)
    if args.staged or args.base:
        tests += added_tests(staged=args.staged, base=args.base or 'HEAD')
    if args.all:
        for path in sorted((TOOLS / 'tests').glob('test_*.py')):
            tests += [f'{path.relative_to(ROOT)}::{test}' for test in enclosing_tests(path.read_text()).values()]
    flagged = 0
    for test in tests:
        path, name = test.split('::', 1)
        quiet = io.StringIO()
        try:
            stdout, stderr = sys.stdout, sys.stderr
            sys.stdout = sys.stderr = quiet
            bad, stubbed = check(ROOT / path if not Path(path).is_absolute() else Path(path), name)
        finally:
            sys.stdout, sys.stderr = stdout, stderr
        if bad:
            flagged += 1
            print(f'CANNOT FAIL {test}: it passes with each of {", ".join(stubbed)} returning a wrong value')
        else:
            print(f'ok {test}' + (f' (stubbed {", ".join(stubbed)})' if stubbed else ' (calls no tool function '
                                                                                         'directly; not judged)'))
    print(f'{len(tests)} tests checked, {flagged} flagged.')
    return 1 if flagged else 0


if __name__ == '__main__':
    sys.exit(main())
