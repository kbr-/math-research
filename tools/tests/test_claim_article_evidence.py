import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from claim_evidence import ARTICLE_NORMALIZATION as V, normalize_article

class ArticleEvidenceTests(unittest.TestCase):
    def test_only_generated_decoration_is_ignored(self):
        base='<article id="entry"><p class="entry-meta">Working proof.</p><p>Claim.</p><!-- TIMING turn --></article>\n'
        finished=base.replace('Working proof.</p>', 'Working proof. <span data-generated="finish-turn-producer-v1">Produced by Agent (Model).</span></p>').replace('<!-- TIMING turn -->','<div data-generated="finish-turn-timing-v1" class="timing-report" data-session="turn"><table><tr><td>1 s</td></tr></table></div>')
        self.assertEqual(normalize_article(base,V),normalize_article(finished,V))
        for changed in [finished.replace('Claim.','False claim.'),finished.replace('Working proof.','Refuted.'),finished.replace('id="entry"','id="other"')]:
            self.assertNotEqual(normalize_article(base,V),normalize_article(changed,V))

    def test_unmarked_or_interior_producer_and_unmarked_timing_are_evidence(self):
        base='<article><p class="entry-meta">Status.</p></article>'
        for content in [' Produced by Agent (Model).',' <span>Produced by Agent (Model).</span>',
                        ' <span data-generated="finish-turn-producer-v1">A theorem.</span>',
                        ' <span data-generated="finish-turn-producer-v1">Produced by Agent (Model).</span> More status.']:
            other=base.replace('Status.</p>','Status.'+content+'</p>')
            self.assertNotEqual(normalize_article(base,V),normalize_article(other,V))
        other=base.replace('</article>','<div class="timing-report" data-session="x"><p>A claim.</p></div></article>')
        self.assertNotEqual(normalize_article(base,V),normalize_article(other,V))

    def test_actual_legacy_source_refresh_remains_raw(self):
        from claim_reviews import Evidence
        from claim_registry import ROOT
        target = 'https://kbr.is-a.dev/math-research/#local-zero-cofactor-pruning'
        evidence = Evidence(ROOT)
        item = evidence.snapshot(target)
        self.assertEqual(item, {'target': target, 'sha256': evidence.sha256(target)})
        self.assertNotIn('normalization', item)

    def test_raw_math_and_unknown_versions(self):
        text=r'<article><p>\(a<b\) and \[x<y>z\]</p></article>'
        self.assertEqual(normalize_article(text,V),text)
        with self.assertRaises(ValueError):normalize_article(text,'future-version')
        with self.assertRaises(ValueError):normalize_article('<h4>Claim</h4>',V)

if __name__=='__main__':unittest.main()
