import importlib.util
from pathlib import Path
import unittest

TOOLS = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('merge_claim_registry', TOOLS / 'merge-claim-registry.py')
mcr = importlib.util.module_from_spec(spec); spec.loader.exec_module(mcr)


def reg(*claims, rels=(), version=2):
    return {'version': version, 'claims': [dict(id=c, v=v) for c, v in claims], 'relationships': list(rels)}


class MergeClaimRegistryTest(unittest.TestCase):
    def test_one_sided_changes_and_additions_combine(self):
        base = reg(('a', 0), ('b', 0))
        ours = reg(('a', 1), ('b', 0), ('c', 0), rels=[{'id': 'r1'}])
        theirs = reg(('a', 0), ('b', 2), ('d', 0), rels=[{'id': 'r2'}])
        merged, conflicts = mcr.merge(base, ours, theirs)
        self.assertEqual(conflicts, [])
        self.assertEqual(merged['claims'], [dict(id='a', v=1), dict(id='b', v=2),
                                            dict(id='c', v=0), dict(id='d', v=0)])
        self.assertEqual([r['id'] for r in merged['relationships']], ['r1', 'r2'])

    def test_same_change_on_both_sides_is_not_a_conflict(self):
        base = reg(('a', 0)); both = reg(('a', 5))
        merged, conflicts = mcr.merge(base, both, both)
        self.assertEqual((merged['claims'], conflicts), ([dict(id='a', v=5)], []))

    def test_different_changes_conflict(self):
        _, conflicts = mcr.merge(reg(('a', 0)), reg(('a', 1)), reg(('a', 2)))
        self.assertEqual(len(conflicts), 1)
        self.assertIn('changed on both sides', conflicts[0])

    def test_deletion_applies_only_to_unchanged_records(self):
        merged, conflicts = mcr.merge(reg(('a', 0), ('b', 0)), reg(('a', 0), ('b', 0)), reg(('b', 0)))
        self.assertEqual((merged['claims'], conflicts), ([dict(id='b', v=0)], []))
        _, conflicts = mcr.merge(reg(('a', 0)), reg(('a', 1)), reg())
        self.assertIn('deleted by the replayed side', conflicts[0])
        _, conflicts = mcr.merge(reg(('a', 0)), reg(), reg(('a', 1)))
        self.assertIn('deleted upstream', conflicts[0])

    def test_top_level_scalars(self):
        merged, conflicts = mcr.merge(reg(), reg(version=3), reg())
        self.assertEqual((merged['version'], conflicts), (3, []))
        _, conflicts = mcr.merge(reg(), reg(version=3), reg(version=4))
        self.assertIn('top-level version', conflicts[0])


if __name__ == '__main__':
    unittest.main()
