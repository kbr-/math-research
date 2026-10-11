"""A branch's own additions to the shared framework tools.

The tools in this directory are the same on every branch of the repository. A branch that needs more of one
of them (a further check at a turn's end, further files whose records are checked) keeps that in a module of
its own, tools/branch_own.py, which the shared tools load through this file where it exists. A tool asks for
one name and does what it does on every branch where the module, or the name, is absent:

  branch_extension.ask('STOP_CHECK_NAMES', ())

So a shared tool holds nothing that only one branch uses, and a branch's own module never has to be merged
with another's.
"""
import importlib.util
from pathlib import Path

NAME = 'branch_own'
_loaded = {}


def own(tools=None):
    """The branch's own module in the tools directory `tools` (this file's by default), or None."""
    path = Path(tools or Path(__file__).resolve().parent) / f'{NAME}.py'
    if path not in _loaded:
        module = None
        if path.is_file():
            spec = importlib.util.spec_from_file_location(NAME, path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
        _loaded[path] = module
    return _loaded[path]


def ask(name, default=None, tools=None):
    """What the branch's own module calls `name`, or `default` where it has no module or no such name."""
    return getattr(own(tools), name, default)
