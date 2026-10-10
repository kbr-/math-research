"""Zero-sum sets and the sharing property on rows small enough to check by hand."""
import importlib.util
import pathlib
import unittest

SPEC = importlib.util.spec_from_file_location(
    'paired_row_sharing', pathlib.Path(__file__).resolve().parents[1] / 'paired_row_sharing.py')
PRS = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(PRS)


class SharingTest(unittest.TestCase):
    def test_zero_sum_sets_by_hand(self):
        # weights 1, 2, 3 mod 7: 1 + 2 - 3 = 0 is the only signed zero-sum
        self.assertEqual(PRS.zero_sum_sets([1, 2, 3], 7), [0b111])
        # weights 1, 1 mod 5: 1 - 1 = 0
        self.assertEqual(PRS.zero_sum_sets([1, 1], 5), [0b11])
        self.assertEqual(PRS.zero_sum_sets([1, 2], 7), [])

    def test_a_single_set_is_pruned(self):
        result = PRS.analyse([1, 2, 3], 7)
        self.assertEqual((result['zero_sum_sets'], result['w'], result['sharing'], result['pruned_size']),
                         (1, 3, False, 0))

    def test_equal_weights_share(self):
        # weights 1, 1, 1, 1 mod 5: the zero-sum sets are the six pairs and the 4-set; w = 2, and every
        # single element of a member lies in another member
        result = PRS.analyse([1, 1, 1, 1], 5)
        self.assertEqual((result['zero_sum_sets'], result['w'], result['by_size']), (7, 2, {'2': 6, '4': 1}))
        self.assertTrue(result['sharing'])
        self.assertEqual(result['pruned_size'], 7)
        # at size w = 2: each pair lies in the 4-set, and each pair of the 4-set is itself another member
        self.assertTrue(result['sharing_at_w'])
        self.assertEqual(result['pruned_size_at_w'], 7)

    def test_pruning_can_leave_a_proper_nonempty_family(self):
        # the saved row (10, 1009): 30 zero-sum sets, w = 5; 11 remain at size w - 1 and none at size w
        # (both values reproduced by a reviewer's independent brute-force script, 10 October 2026)
        result = PRS.analyse([741, 240, 765, 844, 29, 779, 686, 982, 691, 642], 1009)
        self.assertEqual((result['zero_sum_sets'], result['w']), (30, 5))
        self.assertEqual((result['sharing'], result['pruned_size']), (False, 11))
        self.assertEqual((result['sharing_at_w'], result['pruned_size_at_w']), (False, 0))


if __name__ == '__main__':
    unittest.main()
