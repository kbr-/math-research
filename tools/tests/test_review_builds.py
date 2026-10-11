"""finish-turn.py: a review whose period queued build items and built none says what becomes of each."""
import importlib.util
import sys
import unittest
from pathlib import Path

TOOLS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS))
spec = importlib.util.spec_from_file_location('ft_review_builds', TOOLS / 'finish-turn.py')
FT = importlib.util.module_from_spec(spec)
spec.loader.exec_module(FT)


def notebook(queue, articles):
    """A notebook with the given queue items and record articles (id, kind, inner HTML) on route r; the last
    article is the one checked."""
    record = ''.join(f'<article id="{ident}" data-kind="{kind}" data-route="r">{inner}</article>'
                     for ident, kind, inner in articles)
    body = (f'<section id="lead-queue"><ol>{queue}</ol></section>'
            f'<section id="research-record">{record}</section>')
    article = body.rindex('<article')
    return body, article, body.index('</article>', article)


def build(ident, source):
    return f'<li data-build="{ident}" data-source="{source}">A check. (<a href="#x">source</a>)</li>'


class ReviewBuildsTest(unittest.TestCase):
    def test_review_with_unbuilt_builds_of_its_period_is_refused(self):
        body, article, close = notebook(
            build('old-check', 'e0') + build('new-check', 'e2') + build('own-check', 'rev2'),
            [('e0', 'research', ''), ('rev1', 'review', ''), ('e2', 'research', ''), ('rev2', 'review', '')])
        with self.assertRaisesRegex(ValueError, 'new-check, own-check'):
            FT.validate_review_builds(body, article, close)

    def test_a_build_queued_before_the_previous_review_is_not_counted(self):
        body, article, close = notebook(
            build('old-check', 'e0'),
            [('e0', 'research', ''), ('rev1', 'review', ''), ('e2', 'research', ''), ('rev2', 'review', '')])
        FT.validate_review_builds(body, article, close)

    def test_builds_paragraph_naming_each_passes(self):
        inner = '<p><strong>Builds.</strong> new-check waits: 11 October, the suite is being diagnosed.</p>'
        body, article, close = notebook(
            build('new-check', 'e2'),
            [('rev1', 'review', ''), ('e2', 'research', ''), ('rev2', 'review', inner)])
        FT.validate_review_builds(body, article, close)
        partial = inner.replace('new-check', 'another')
        body, article, close = notebook(
            build('new-check', 'e2'),
            [('rev1', 'review', ''), ('e2', 'research', ''), ('rev2', 'review', partial)])
        with self.assertRaisesRegex(ValueError, 'new-check'):
            FT.validate_review_builds(body, article, close)

    def test_a_build_developed_in_the_period_lifts_the_demand(self):
        done = ('<ul><li data-build="other">Built. <strong>Follow-up.</strong> Developed: '
                '<a href="tools/x.py">tools/x.py</a>.</li></ul>')
        body, article, close = notebook(
            build('new-check', 'e2'),
            [('rev1', 'review', ''), ('e2', 'research', done), ('rev2', 'review', '')])
        FT.validate_review_builds(body, article, close)

    def test_research_entries_and_free_text_sources_are_left_alone(self):
        body, article, close = notebook(
            build('new-check', 'stand-in review, 11 October 2026'),
            [('rev1', 'review', ''), ('e2', 'research', ''), ('rev2', 'review', '')])
        FT.validate_review_builds(body, article, close)
        body, article, close = notebook(build('new-check', 'e2'), [('rev1', 'review', ''), ('e2', 'research', '')])
        FT.validate_review_builds(body, article, close)


if __name__ == '__main__':
    unittest.main()


class PeriodOfAnItemTest(unittest.TestCase):
    def test_an_item_is_of_the_period_by_its_source_s_entry_or_by_the_entry_it_was_added_after(self):
        idents = {'e2', 'rev2'}
        tag = lambda source, after='': f'<li data-build="x" data-source="{source}"{after}>'
        self.assertTrue(FT.queued_in(tag('e2'), idents))
        self.assertTrue(FT.queued_in(tag('e2, reviewer of 11 October 2026'), idents))    # an entry, then words
        self.assertFalse(FT.queued_in(tag('stand-in review, 11 October 2026'), idents))  # words only, undated
        self.assertTrue(FT.queued_in(tag('stand-in review, 11 October 2026', ' data-after="e2"'), idents))
        self.assertFalse(FT.queued_in(tag('stand-in review', ' data-after="e0"'), idents))
        self.assertFalse(FT.queued_in(tag('e20'), idents))                              # another entry's anchor

    def test_a_build_entry_of_the_period_counts_as_a_build(self):
        developed = ('<article id="e3" data-kind="research" data-route="r" data-build="some-check"><p><strong>'
                     'Follow-up.</strong> Developed: the build exists at tools/x.py.</p></article>')
        body = ('<section id="lead-queue"><ol>' + build('new-check', 'e2') + '</ol></section>'
                '<section id="research-record"><article id="rev1" data-kind="review" data-route="r"></article>'
                '<article id="e2" data-kind="research" data-route="r"></article>' + developed
                + '<article id="rev2" data-kind="review" data-route="r"></article></section>')
        article = body.rindex('<article')
        FT.validate_review_builds(body, article, body.index('</article>', article))     # one queued, one built
        with self.assertRaisesRegex(ValueError, 'new-check'):
            unbuilt = body.replace(developed, '')
            article = unbuilt.rindex('<article')
            FT.validate_review_builds(unbuilt, article, unbuilt.index('</article>', article))
        # One build among two queued does not excuse the review from naming them.
        two = body.replace(build('new-check', 'e2'), build('new-check', 'e2') + build('other-check', 'e2'))
        article = two.rindex('<article')
        with self.assertRaisesRegex(ValueError, 'new-check, other-check'):
            FT.validate_review_builds(two, article, two.index('</article>', article))
