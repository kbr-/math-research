import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('outcome_ahead', ROOT / 'tools' / 'outcome_ahead.py')
tool = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tool)


def entry(status, body, kind='research', ident='e'):
    return f'<article id="entry-{ident}" data-kind="{kind}"><h3>T</h3><p class="entry-meta">{status}</p>{body}'


class OutcomeAheadTest(unittest.TestCase):
    HEDGED = '<p>The first step is checked. The removal is an outline; its second step is not verified.</p>'

    def test_a_firm_status_is_listed_beside_the_sentences_that_hedge(self):
        lines = tool.report(entry('Working proof of a lemma. Label.', self.HEDGED))
        self.assertEqual(lines, ['  firm: Working proof of a lemma. Label.', '  hedge: The removal is an outline;',
                                 '  hedge: its second step is not verified.'])
        # A test reported Decided is firm whatever the status line says.
        decided = ('<p><strong>Architecture test.</strong> The review\'s test, with a link: '
                   '<strong>Decided.</strong> The first outcome.</p>')
        lines = tool.report(entry('Conditional result. Label.', decided + self.HEDGED))
        self.assertEqual(lines[0], "  firm: Architecture test. The review's test, with a link: Decided. The first "
                                   'outcome.')
        # The narrow report keeps that flag and drops the one by the status line alone.
        self.assertEqual(tool.report(entry('Conditional result. Label.', decided + self.HEDGED), status_line=False),
                         lines)
        self.assertEqual(tool.report(entry('Working proof of a lemma. Label.', self.HEDGED), status_line=False), [])

    def test_nothing_firm_nothing_hedged_other_kinds_and_the_suggestions_give_no_lines(self):
        suggestions = "<h4>Reviewer's suggestions, unverified</h4><ul><li>An unverified lead.</li></ul>"
        undecided = ('<p><strong>Architecture test.</strong> <strong>Not decided.</strong> Something here is '
                     'an outline.</p>')
        for quiet in (entry('Conditional result. Label.', self.HEDGED), entry('Working proof. Label.', '<p>Shown.</p>'),
                      entry('Working proof. Label.', self.HEDGED, kind='review'),
                      entry('Working proof. Label.', suggestions), entry('A reading. Label.', undecided)):
            self.assertEqual(tool.report(quiet), [])

    def test_the_words_do_not_see_a_negation(self):
        # Recorded as a limit: "no statement proved" counts as firm.
        self.assertTrue(tool.report(entry('An attempt, no statement proved. Label.', self.HEDGED)))

    def test_a_transcript_gives_the_first_written_version_of_each_entry(self):
        def written(text, name='Write'):
            return json.dumps({'message': {'content': [{'type': 'text', 'text': 'x'}, {
                'type': 'tool_use', 'name': name, 'input': {'file_path': '/tmp/e.html', 'content': text}}]}})
        draft = entry('Working proof. Label.', '<p>The step is not verified.</p>', ident='a') + '</article>'
        final = entry('Conditional result. Label.', '<p>The step is not verified.</p>', ident='a') + '</article>'
        lines = [written(draft), 'not json', json.dumps({'message': {'content': 'plain'}}), written(final),
                 written('<p>Route item: a next step.</p>'), written(final.replace('entry-a', 'entry-b'), name='Edit')]
        text = tool.first_drafts(lines)
        self.assertEqual(text, draft)
        self.assertEqual([ident for ident, _ in tool.flags(text)[0]], ['entry-a'])

    def test_the_listing_counts_entries_and_names_the_flagged_ones(self):
        text = (entry('Working proof. Label.', '<p>The second step is not verified.</p>', ident='a') + '</article>'
                + entry('Working proof. Label.', '<p>All shown.</p>', ident='b') + '</article>'
                + entry('Working proof. Label.', '<p>Not verified.</p>', kind='review', ident='c') + '</article>')
        found, entries, research = tool.flags(text)
        self.assertEqual((entries, research), (3, 2))
        self.assertEqual([ident for ident, _ in found], ['entry-a'])


if __name__ == '__main__':
    unittest.main()
