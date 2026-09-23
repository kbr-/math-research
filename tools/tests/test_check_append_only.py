import importlib.util
import unittest
from pathlib import Path

SPEC = importlib.util.spec_from_file_location('check_append_only', Path(__file__).resolve().parents[1] / 'check-append-only.py')
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def body(cell):
    return f'<section id="research-record"><article id="e1"><table><tr><td>{cell}</td></tr></table></article></section>'


class AppendOnlyTest(unittest.TestCase):
    def test_non_breaking_space_is_presentation(self):
        self.assertEqual(MODULE.violations(body('38 / 527'), body('38&nbsp;/&nbsp;527')), ([], []))
        self.assertEqual(MODULE.violations(body('38 / 527'), body('38 / 527')), ([], []))

    def test_link_repair_is_allowed(self):
        self.assertEqual(MODULE.violations(body('see x'), body('see <a href="#y">x</a>')), ([], []))

    def test_text_change_is_rejected(self):
        self.assertEqual(MODULE.violations(body('38 / 527'), body('38 / 528')), ([], ['e1']))


if __name__ == '__main__':
    unittest.main()
