import sys
import unittest
from pathlib import Path

TOOLS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS))
import record_search as search_record  # noqa: E402

NOTEBOOK = '''<section id="where-we-stand"><p>Planning appeals stand here too.</p></section>
<article class="research-entry" id="entry-a-planning"><h3>Householder planning appeals: too few a year</h3>
<p>Homeowners appealing a refused extension to the Planning Inspectorate.</p></article>
<article class="research-entry" id="entry-b-school"><h3>School admission appeals</h3>
<p>Parents appeal a refused school place to an independent panel.</p></article>
<article class="research-entry" id="entry-c-care"><h3>Care home contracts</h3>
<p>Families check a care home&#39;s contract against the CMA&#39;s advice.</p></article>
<article class="research-entry" id="entry-d-long"><h3>Task notes on a family check</h3>
<p>In England a refusal can go to appeal; planning the next step comes later.</p></article>
'''


class SearchRecordTest(unittest.TestCase):
    def test_other_phrasing_finds_the_entry(self):
        # The rediscovery this tool guards against: "planning refusal" missed "planning appeals".
        rows = search_record.search(NOTEBOOK, ['planning', 'refusal', 'appeals', 'England'])
        self.assertEqual(rows[0][1], 'entry-a-planning')
        self.assertIn('plann', rows[0][3])

    def test_title_words_outrank_words_in_passing(self):
        # entry-d mentions every query word in passing; entry-a names planning appeals in its title.
        rows = search_record.search(NOTEBOOK, ['planning', 'refusal', 'appeals', 'England'])
        anchors = [r[1] for r in rows]
        self.assertLess(anchors.index('entry-a-planning'), anchors.index('entry-d-long'))

    def test_a_body_match_below_the_shown_rows_is_listed_after_them(self):
        # A review that had falsified Entra secret expiry ranked about 144th for that job's words,
        # since its title is generic; the CLI now lists the best whole-text matches it did not show.
        import contextlib
        import importlib.util
        import io
        import tempfile
        spec = importlib.util.spec_from_file_location('search_record_cli', TOOLS / 'search-record.py')
        cli = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cli)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'notebook.html'
            path.write_text(NOTEBOOK)
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                cli.main(['-n', '1', '--notebook', str(path), 'planning', 'refusal', 'appeals', 'England'])
        shown, _, extra = out.getvalue().partition('Best whole-text matches not shown above:')
        self.assertIn('entry-a-planning', shown)
        self.assertIn('entry-d-long', extra, 'the long entry naming every word is listed after the shown row')
        self.assertNotIn('entry-a-planning', extra)

    def test_rare_words_outrank_common_ones(self):
        # "Inspectorate" occurs once and "appeal" three times, so the entry with both leads.
        rows = search_record.search(NOTEBOOK, ['appeal', 'Inspectorate'])
        self.assertEqual([r[1] for r in rows], ['entry-a-planning', 'entry-b-school', 'entry-d-long'])

    def test_a_phrase_is_found_whatever_its_case_and_spacing_and_counted_per_entry(self):
        hits = search_record.phrase_hits(NOTEBOOK.replace('refused extension', 'refused\n  Extension'), 'REFUSED extension')
        self.assertEqual([(a, c) for a, _, c in hits], [('entry-a-planning', 1)])
        self.assertEqual([a for a, _, _ in search_record.phrase_hits(NOTEBOOK, 'appeal')],
                         ['entry-a-planning', 'entry-b-school', 'entry-d-long'], 'record order, living sections skipped')

    def test_a_phrase_does_not_match_its_words_apart(self):
        # The ranked search finds entries sharing the words; the phrase check must not.
        self.assertEqual(search_record.phrase_hits(NOTEBOOK, 'planning refusal'), [])
        self.assertEqual(search_record.phrase_hits(NOTEBOOK, 'school place'),
                         [('entry-b-school', 'School admission appeals', 1)])

    def test_no_shared_word_no_row_and_living_sections_skipped(self):
        self.assertEqual(search_record.search(NOTEBOOK, ['robocall']), [])
        anchors = [r[1] for r in search_record.search(NOTEBOOK, ['stand'])]
        self.assertEqual(anchors, [])

    def test_short_stems_do_not_prefix_match(self):
        notebook = NOTEBOOK + '<article id="entry-e-app"><h3>An app store check</h3><p>app</p></article>'
        anchors = [r[1] for r in search_record.search(notebook, ['appeal'])]
        self.assertNotIn('entry-e-app', anchors)

    def test_entities_are_unescaped(self):
        rows = search_record.search(NOTEBOOK, ["CMA's"])
        self.assertEqual(rows[0][1], 'entry-c-care')


class CoverageTest(unittest.TestCase):
    def test_screened_rows_share_title_words_and_new_ground_does_not(self):
        rows = [('school', ['school', 'admission', 'appeal']), ('charity', ['charity', 'commission', 'appeal'])]
        (_, school), (_, charity) = search_record.coverage(NOTEBOOK, rows)
        self.assertEqual(school[0][:1], ('entry-b-school',))
        self.assertEqual(school[0][2:], (3, 3))
        # "appeal" alone ties the charity row to entries about other procedures.
        self.assertEqual(max(shared for _, _, shared, _ in charity), 1)


RECORD = '\n'.join(
    f'<article id="entry-{i}"><h3>1 October 2026 &mdash; Filler {i} about tea</h3><p>A routine cycle.</p></article>'
    for i in range(40)) + '''
<article id="entry-gao"><h3>Federal debriefings</h3><p>GAO took protests; Covington and Butzel
report relief for the protester in half.</p></article>
'''


class NearestUnlinkedTest(unittest.TestCase):
    NEW = ('<article id="entry-new"><h3>Revealed preference</h3><p>Protests reached GAO and the '
           'protester won relief, by Covington and Butzel. {body}</p></article>')

    def test_the_earlier_entry_on_the_same_thing_comes_first(self):
        # The case that prompted it: an entry repeated an earlier entry's GAO figures uncited.
        found = search_record.nearest_unlinked(RECORD, self.NEW.format(body=''))
        self.assertEqual([a for a, _, _, _ in found], ['entry-gao'])
        self.assertIn('butzel', found[0][3])

    def test_a_linked_entry_is_left_out(self):
        entry = self.NEW.format(body='<a href="#entry-gao">entry</a>')
        self.assertEqual(search_record.nearest_unlinked(RECORD, entry), [])

    def test_common_words_do_not_count(self):
        # Words in many entries ("routine", "cycle", the date) must not make entries close.
        entry = '<article id="entry-x"><h3>1 October 2026</h3><p>A routine cycle.</p></article>'
        self.assertEqual(search_record.nearest_unlinked(RECORD, entry), [])


REVIEW = '''<article class="research-entry" id="entry-z-review"><h3>Review</h3>
<h4>Outside leads</h4>
<ol>
  <li>The Open Contracting Data Standard on Contracts Finder: buyers' contracts. <strong>Answers.</strong> x</li>
  <li>Taleb, the Lindy effect, read through the Wayback Machine&#39;s captures. <strong>Answers.</strong> y</li>
</ol>
<h4>Absurd bridges</h4>
<ol><li>Acoustics, passive sonar: listen. <strong>Answers.</strong> Contracts Finder again.</li></ol>
<h4>Lead follow-up</h4>
<ol><li data-lead="x:1">Moore, Crossing the Chasm. Continuing.</li></ol>
</article>'''

EARLIER = '''<article class="research-entry" id="entry-y-built"><h3>Review built</h3>
<p>Contracts Finder, read as revealed willingness to pay: no location assessments.</p></article>
<article class="research-entry" id="entry-x-other"><h3>Other</h3><p>Crossing the Chasm and Ofsted.</p></article>
'''


class LeadNameTest(unittest.TestCase):
    def test_names_come_from_new_items_heads_only(self):
        names = search_record.lead_names(REVIEW)
        # A run joined by a particle is searched whole and in parts; possessives lose their "'s".
        for name in ('Open Contracting Data Standard', 'Contracts Finder', 'Taleb', 'Lindy',
                     'Wayback Machine', 'Acoustics'):
            self.assertIn(name, names)
        # Follow-up lists repeat earlier items by design, and text after the colon is not a name.
        self.assertNotIn('Crossing the Chasm', names)
        self.assertNotIn('Answers', names)

    def test_titles_are_not_names(self):
        review = ('<article id="r"><h4>Outside leads</h4><ol>'
                  '<li>Drucker, <em>Innovation and Entrepreneurship</em> (1985), sources. <strong>Answers.</strong> x</li>'
                  '<li>Shannon, &quot;A Mathematical Theory of Communication&quot; (1948): y. <strong>Answers.</strong> z</li>'
                  '</ol></article>')
        names = search_record.lead_names(review)
        self.assertEqual(names, ['Drucker', 'Shannon'])
        # Four-letter surnames (Wald, Roth) are names too; the first version required five letters.
        short = '<article id="s"><h4>Outside leads</h4><ol><li>Wald, the sequential test. <strong>Answers.</strong> x</li></ol></article>'
        self.assertEqual(search_record.lead_names(short), ['Wald'])

    def test_an_earlier_use_of_a_lead_name_is_found(self):
        # A review of 1 October 2026 offered a Contracts Finder search that a review of 30 September
        # had run; the earlier entry must be listed, and the review itself must not.
        hits = dict(search_record.lead_name_hits(EARLIER + REVIEW, REVIEW))
        self.assertEqual([a for a, _ in hits['Contracts Finder']], ['entry-y-built'])
        self.assertNotIn('Taleb', hits)
        self.assertEqual(search_record.lead_name_hits(EARLIER, '<article id="q"><p>none</p></article>'), [])


class QuoteHitsTest(unittest.TestCase):
    def test_an_earlier_quotation_of_the_same_words_is_found(self):
        # The review presented a force's rule as new; two entries had quoted the same words.
        record = ('<article id="old"><h3>Old</h3><p>The force shares only information &quot;that could '
                  'not otherwise be found on publicly available sources&quot;.</p></article>'
                  '<article id="other"><h3>Other</h3><p>Nothing quoted here.</p></article>')
        entry = ('<article id="new"><h3>New</h3><p>Its page says it shares what &quot;could not '
                 'OTHERWISE be found on publicly available sources&quot;, and &quot;two words&quot; '
                 'are too short.</p></article>')
        self.assertEqual(search_record.quote_hits(record + entry, entry),
                         [('could not OTHERWISE be found on publicly available sources', ['old'])])

    def test_a_quotation_one_word_longer_and_carried_follow_ups(self):
        record = ('<article id="old"><p>it shares what &quot;could not otherwise be found on publicly '
                  'available sources&quot;</p></article>'
                  '<article id="rev"><p>&quot;You and Your Research&quot;</p></article>')
        entry = ('<article id="new"><p>&quot;that could not otherwise be found on publicly available '
                 'sources&quot;</p><h4>Lead follow-up</h4>\n<ul><li>Hamming, &quot;You and Your '
                 'Research&quot;.</li></ul></article>')
        self.assertEqual(search_record.quote_hits(record + entry, entry),
                         [('that could not otherwise be found on publicly available sources', ['old'])])

    def test_no_quotation_no_listing(self):
        self.assertEqual(search_record.quote_hits('<article id="a"><p>x</p></article>', '<article id="b"><p>plain</p></article>'), [])


if __name__ == '__main__':
    unittest.main()
