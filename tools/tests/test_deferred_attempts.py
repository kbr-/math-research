import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('deferred_attempts', ROOT / 'tools' / 'deferred_attempts.py')
tool = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tool)

MADE = 'The reading the last entry named is made here, with the outcome below.'
LATER = MADE + ' The attempt on the twist is again not made, since the question of room comes before it; it stays owed.'
NONE = 'The item has no earlier entry, and no attempt was named for it; none is unmade.'
DROP = 'The attempt on the twist is not made and is dropped: the proof it would audit is no longer used.'


def entry(ident, item, owed, kind='idea'):
    return (f'<article id="entry-{ident}" data-kind="research" data-{kind}="{item}">'
            f'<p><strong>Owed attempt.</strong> {owed}</p><p>Body.</p></article>')


def record(*entries):
    return '<section id="lead-queue"></section><section id="research-record">' + ''.join(entries) + '</section>'


class DeferredAttemptsTest(unittest.TestCase):
    def test_what_counts_as_deferring(self):
        for owed, expected in ((MADE, False), (LATER, True), (NONE, False), (DROP, False),
                               ('It is not reached in this entry because the lemma came first.', True)):
            with self.subTest(owed=owed):
                self.assertEqual(tool.defers(entry('x', 'i', owed)), expected)
        self.assertFalse(tool.defers('<article id="entry-y" data-idea="i"><p>No such paragraph.</p></article>'))

    def test_the_known_misreadings_of_the_words(self):
        # Recorded as limits, which is why the finisher prints and does not refuse.
        self.assertTrue(tool.defers(entry('x', 'i', 'The attempt deferred twice is made here, with its outcome.')))
        self.assertFalse(tool.defers(entry('x', 'i', 'The review dropped another item. This attempt is not made.')))
        self.assertFalse(tool.defers(entry('x', 'i', 'Nothing was read of it and the proof is not made and stays owed.')))

    def test_the_third_deferral_in_a_row_on_one_item_is_found(self):
        text = record(entry('a', 'one', LATER), entry('b', 'two', LATER, kind='build'), entry('c', 'one', LATER),
                      entry('d', 'one', LATER), entry('e', 'one', DROP), entry('f', 'one', LATER))
        rows = tool.survey(text)
        self.assertEqual([(ident, refused) for ident, _, _, refused in rows],
                         [('entry-a', False), ('entry-b', False), ('entry-c', False), ('entry-d', True),
                          ('entry-e', False), ('entry-f', False)])
        entries = tool.ARTICLE.findall(text)
        self.assertEqual(tool.third_deferral(entries[:3], *entries[3]), ['entry-a', 'entry-c'])
        # Made in between, the run is broken; an entry on no item is not judged.
        broken = record(entry('a', 'one', LATER), entry('b', 'one', MADE), entry('c', 'one', LATER),
                        entry('d', 'one', LATER))
        self.assertEqual([refused for *_, refused in tool.survey(broken)], [False, False, False, False])
        self.assertIsNone(tool.third_deferral(entries[:3], ' id="entry-z" data-kind="research"', 'x'))


if __name__ == '__main__':
    unittest.main()
