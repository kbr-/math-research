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
