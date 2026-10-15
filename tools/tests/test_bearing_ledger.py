"""A claimed application ties its witness to the budget it actually verifies."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import bearing_ledger as ledger


def link(name='selection', target='#selection'):
    return f'<a data-ledger="{name}" href="{target}">{name}</a>'


def entry(bearing=None, witness=None, declared='some', after=''):
    bearing = link() if bearing is None else bearing
    witness = link() if witness is None else witness
    return (f'<article data-bearing="{declared}">'
            f'<p><strong>Goal progress.</strong> Unchanged. <strong>Bearing.</strong> {bearing}'
            f'<strong>Not covered.</strong> Other cases. {after}</p>'
            f'<p><strong>Nonvacuity.</strong> The example verifies {witness}.</p></article>')


class BearingLedgerTest(unittest.TestCase):
    def test_application_needs_an_explicit_ledger_inside_bearing(self):
        ledger.validate(entry())
        ledger.validate(entry(bearing='<a href="#other">context</a>' + link()))
        ledger.validate(entry().replace('Bearing.</strong> ', 'Bearing.</strong>'))
        ledger.validate(entry(bearing=link() + ' See Bearing. for the budget.'))
        ledger.validate(entry().replace('<strong>Not covered.</strong> Other cases. ', ''))
        ledger.validate(entry().replace('Unchanged.', link() + ' Unchanged.'))
        ledger.validate(entry().replace('Unchanged.', 'Unchanged; see Not covered. below.'))
        for bearing in ('If the degree inequality holds, the theorem applies.',
                        '<a href="#selection">a conditional statement</a>'):
            with self.assertRaisesRegex(ValueError, 'matched parameter ledger'):
                ledger.validate(entry(bearing=bearing))
        with self.assertRaisesRegex(ValueError, 'matched parameter ledger'):
            ledger.validate(entry(bearing='No reference here.', after=link()))
        with self.assertRaisesRegex(ValueError, 'matched parameter ledger'):
            ledger.validate(entry(bearing='No reference here.', after=link() + ' Not covered.'))
        before = entry(bearing='No reference here.').replace('Unchanged.', link() + ' Unchanged.')
        with self.assertRaisesRegex(ValueError, 'matched parameter ledger'):
            ledger.validate(before)
        near = entry(bearing='No reference here.').replace('<strong>Bearing.</strong>',
            '<a data-ledger="selection" href="#selection">s</a><strong>Bearing.</strong>')
        with self.assertRaisesRegex(ValueError, 'matched parameter ledger'):
            ledger.validate(near)
        at_boundary = entry(bearing='No reference here.').replace(
            '<strong>Not covered.</strong>',
            '<a data-ledger="selection" href="#selection"><strong>Not covered.</strong></a>')
        with self.assertRaisesRegex(ValueError, 'matched parameter ledger'):
            ledger.validate(at_boundary)
        with self.assertRaisesRegex(ValueError, 'Bearing statement'):
            ledger.validate('<article data-bearing="some"><p>Unchanged.</p></article>')

    def test_witness_names_the_specific_supported_budget(self):
        both = link() + ' and ' + link('replay', '#replay')
        ledger.validate(entry(bearing=both))  # selection-only witness; replay is not claimed for it
        for witness in ('the example with D=p+1', link('replay', '#other'),
                        link('different', '#selection')):
            with self.assertRaisesRegex(ValueError, 'particular data-ledger'):
                ledger.validate(entry(bearing=both, witness=witness))
        with self.assertRaisesRegex(ValueError, 'separately named'):
            ledger.validate(entry(bearing=both, witness='Both ledgers: ' + link()))
        ledger.validate(entry(bearing=both, witness='both ledgers: ' + both))
        with self.assertRaisesRegex(ValueError, 'separately named'):
            ledger.validate(entry(bearing='all budgets: ' + link()))
        indented_bad = entry(witness='an unsupported example').replace(
            '<p><strong>Nonvacuity.', '<p>\n <strong>Nonvacuity.')
        with self.assertRaisesRegex(ValueError, 'particular data-ledger'):
            ledger.validate(indented_bad)

    def test_references_are_valid_and_scope_is_only_some(self):
        for bad in (link('', '#selection'), link('selection', ''), link('selection', '#'),
                    link('selection budget', '#selection'), '<a data-ledger="selection">missing</a>'):
            with self.assertRaisesRegex(ValueError, 'descriptive budget'):
                ledger.validate(entry(bearing=bad))
        ledger.validate(entry(bearing='no application', witness='no witness', declared='none'))
        ledger.validate(entry(bearing='no declaration', witness='no witness', declared=''))
        ledger.validate(entry().replace('"', "'"))  # normal HTML quoting is accepted
        ledger.validate(entry().replace('Nonvacuity.', 'Imported example.'))
        ledger.validate('\n' + entry().replace('<p>', '<p>\n ').replace('</p>', '</p>\n')
                        + '<a href="#other">Outside any paragraph</a>')
        whole_witness = entry(witness='the selected budget').replace('<p><strong>Nonvacuity.', (
            '<p><a data-ledger="selection" href="#selection"><strong>Nonvacuity.')).replace(
                '.</p></article>', '.</a></p></article>')
        ledger.validate(whole_witness)


if __name__ == '__main__':
    unittest.main()
