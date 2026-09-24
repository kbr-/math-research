import unittest
from importlib.machinery import SourceFileLoader
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FT = SourceFileLoader('finish_turn', str(ROOT / 'tools/finish-turn.py')).load_module()


class NextCycleGuidanceTest(unittest.TestCase):
    def test_notes_after_the_session_path_are_kept(self):
        out = ('research/logs/next.jsonl\n'
               'Route r: 6 research entries since the last route review; the next entry on this route must be a '
               'route review.\n')
        self.assertEqual(FT.next_cycle_guidance(out),
                         ['Route r: 6 research entries since the last route review; the next entry on this route '
                          'must be a route review.'])

    def test_no_notes(self):
        self.assertEqual(FT.next_cycle_guidance('research/logs/next.jsonl\n'), [])


if __name__ == '__main__':
    unittest.main()
