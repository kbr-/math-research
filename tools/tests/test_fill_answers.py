import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import fill_answers as tool  # noqa: E402

TEXT = ('0cf05f56 [New mathematics] The lemma holds.\n  rests on:\n'
        '7df76219 [Follow-up] Plainest bound. The count decides nothing.\n  rests on:\n'
        '431f69b5 [Follow-up] Record search. Three searches.\n  rests on:\n')


class FillAnswersTest(unittest.TestCase):
    def test_answers_go_to_their_own_sentences_whatever_the_order(self):
        # 16 October 2026: filling in file order put two answers on the wrong sentences once a sentence was added.
        text, unanswered = tool.fill(TEXT, {'431f69b5': 'none: the searches', '0cf05f56': 'the lemma, \\(a\\)'})
        self.assertIn('431f69b5 [Follow-up] Record search. Three searches.\n  rests on: none: the searches', text)
        self.assertIn('0cf05f56 [New mathematics] The lemma holds.\n  rests on: the lemma, \\(a\\)', text)
        self.assertEqual(unanswered, ['7df76219'])

    def test_an_unknown_id_a_line_break_and_a_repeated_id_are_refused(self):
        with self.assertRaisesRegex(ValueError, 'deadbeef'):
            tool.fill(TEXT, {'deadbeef': 'x'})
        with self.assertRaisesRegex(ValueError, 'line break'):
            tool.fill(TEXT, {'0cf05f56': 'one\ntwo'})
        import tempfile
        with tempfile.NamedTemporaryFile('w', suffix='.txt', delete=False) as handle:
            handle.write(TEXT)
        self.addCleanup(pathlib.Path(handle.name).unlink)
        self.assertEqual(tool.main([handle.name, '0cf05f56', 'a', '0cf05f56', 'b']), 1)
        self.assertEqual(pathlib.Path(handle.name).read_text(), TEXT)


if __name__ == '__main__':
    unittest.main()
