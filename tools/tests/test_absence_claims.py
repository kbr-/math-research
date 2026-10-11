import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('absence_claims', ROOT / 'tools' / 'absence_claims.py')
tool = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tool)

CLOSED = '<p><strong>Follow-up.</strong> Closed: inapplicable.</p>'


def entry(ident, body, follow=CLOSED):
    return f'<article id="entry-{ident}" data-kind="research"><p>{body}</p>{follow}</article>'


class AbsenceClaimsTest(unittest.TestCase):
    def test_the_sentences_that_claim_an_absence_are_listed_for_closing_entries(self):
        claims = ('The record holds corrected texts. The drafts are not kept; so the check cannot be tried on '
                  'them. Nothing in the repository records which files a session read. The scratch file is gone.')
        self.assertEqual(tool.report(entry('a', claims)),
                         ['  absence: The drafts are not kept;',
                          '  absence: Nothing in the repository records which files a session read.',
                          '  absence: The scratch file is gone.'])
        # An entry that closes nothing, a closing entry without such a sentence, and the suggestions are quiet.
        self.assertEqual(tool.report(entry('b', claims, '<p><strong>Follow-up.</strong> Continuing: more.</p>')), [])
        self.assertEqual(tool.report(entry('c', 'The lemma is proved and the item has no part left.')), [])
        suggestions = ("<h4>Reviewer's suggestions, unverified</h4><ul><li>The source does not exist on arXiv."
                       '</li></ul>')
        self.assertEqual(tool.report(entry('d', 'Proved.') .replace('</article>', suggestions + '</article>')), [])

    def test_a_sub_idea_s_closing_a_registry_search_and_a_long_sentence(self):
        sub = '<ul><li data-check="s1">Done. <strong>Follow-up.</strong> Developed: shown.</li></ul>'
        continuing = '<p><strong>Follow-up.</strong> Continuing: more.</p>'
        self.assertEqual(tool.report(entry('f', 'The file is gone.', sub + continuing)), [])
        searched = ('Proved. <strong>Record search.</strong> Searched kernels: no record on these objects. '
                    '<strong>Limit.</strong> The run was not saved.')
        self.assertEqual(tool.report(entry('g', searched)), ['  absence: The run was not saved.'])
        long = 'word ' * 80 + 'and the order is not recorded anywhere ' + 'word ' * 80
        line, = tool.report(entry('h', long))
        self.assertIn('is not recorded', line)
        self.assertLessEqual(len(line), tool.WIDTH + 20)

    def test_the_words_do_not_tell_the_repository_from_mathematics(self):
        # Recorded as a limit: a statement of mathematics is listed like one about the tree.
        self.assertEqual(len(tool.report(entry('e', 'Such a kernel does not exist for windows shorter than one.'))), 1)

    def test_the_survey_counts_closing_entries(self):
        text = ('<section id="research-record">' + entry('a', 'The drafts are not kept.')
                + entry('b', 'All shown.') + entry('c', 'The file is gone.', '') + '</section>')
        found, closing = tool.survey(text)
        self.assertEqual(closing, 2)
        self.assertEqual([ident for ident, _ in found], ['entry-a'])


if __name__ == '__main__':
    unittest.main()
