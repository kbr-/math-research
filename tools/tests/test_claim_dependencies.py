import copy
import importlib.util
from pathlib import Path
import sys
import tempfile
import unittest

TOOLS=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(TOOLS))
from claim_registry import import_markdown, upgrade, HEADER
from claim_reviews import Evidence
spec=importlib.util.spec_from_file_location('dependency_tool',TOOLS/'claim-dependencies.py')
deps=importlib.util.module_from_spec(spec);spec.loader.exec_module(deps)


class DependencyTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        (self.root/'formalization/claims').mkdir(parents=True)
        self.data=upgrade(import_markdown('# Index\n\n'+HEADER+
            '| `lem:a` | A | Working proof | [A](https://kbr.is-a.dev/math-research/#a), [Lean](../formalization/claims/A.lean) |\n'+
            '| `lem:b` | B | Working proof | [B](https://kbr.is-a.dev/math-research/#b), [Lean](../formalization/claims/B.lean) |\n'))
        (self.root/'notebook.html').write_text('<section><article id="entry-a"><h4 id="a">A</h4>'
            '<p>Does not depend on <a href="#b">B</a>; this is a contrast.</p></article>'
            '<article id="entry-b"><h4 id="b">B</h4><p>Statement.</p></article></section>')
        (self.root/'formalization/claims/A.lean').write_text('/-\nClaim: lem:a\nDeclarations: MathResearch.a\n-/\n'
            'import claims.B\n-- needed is not used in this comment\n'
            '/- outer /- needed -/ comment -/\ndef text := "needed"\ntheorem a := by exact needed\n')
        (self.root/'formalization/claims/B.lean').write_text('/-\nClaim: lem:b\nDeclarations: MathResearch.needed\n-/\ntheorem needed := by trivial\n')

    def test_citations_imports_and_actual_identifier_evidence_are_distinct(self):
        report=deps.scan(self.data,self.root)
        rows=[c for c in report['candidates'] if c['source']=='lem:a']
        self.assertEqual({c['method'] for c in rows},{'notebook_link','lean_import','lean_declaration_reference'})
        link=next(c for c in rows if c['method']=='notebook_link')
        self.assertEqual(link['proposed_type'],'cites')
        self.assertIn('not depend',link['occurrences'][0]['context'])
        usage=next(c for c in rows if c['method']=='lean_declaration_reference')
        self.assertEqual(len(usage['occurrences']),1)
        self.assertEqual(self.data['relationships'],[])

    def test_unused_import_does_not_become_a_declaration_use(self):
        path=self.root/'formalization/claims/A.lean'
        path.write_text(path.read_text().replace('by exact needed','by trivial'))
        report=deps.scan(self.data,self.root)
        methods={c['method'] for c in report['candidates'] if c['source']=='lem:a'}
        self.assertIn('lean_import',methods)
        self.assertNotIn('lean_declaration_reference',methods)

    def test_shared_notebook_region_is_flagged(self):
        new=copy.deepcopy(self.data['claims'][0]);new['id']='lem:shared';self.data['claims'].append(new)
        report=deps.scan(self.data,self.root)
        rows=[c for c in report['candidates'] if c['source']=='lem:a' and c['method']=='notebook_link']
        self.assertTrue(rows[0]['ownership_ambiguous'])

    def test_nonheading_anchor_uses_a_flagged_containing_passage(self):
        path=self.root/'notebook.html'
        path.write_text(path.read_text().replace('<h4 id="a">A</h4>',
                        '<h4 id="parent">Parent</h4><p id="a">A</p>'))
        report=deps.scan(self.data,self.root)
        self.assertEqual(report['claims_with_notebook_regions'],2)
        self.assertEqual(report['widened_source_regions'][0]['containing_anchor'],'parent')
        row=next(c for c in report['candidates'] if c['source']=='lem:a' and c['method']=='notebook_link')
        self.assertTrue(row['ownership_ambiguous'])
        self.assertTrue(deps.is_current(row,self.data,Evidence(self.root)))

    def test_decisions_survive_rescan_but_changed_evidence_is_stale(self):
        report=deps.scan(self.data,self.root)
        candidate=next(c for c in report['candidates'] if c['method']=='notebook_link')
        deps.record_decision(self.data,candidate,state='rejected',reason='Explicit negative contrast.',
            reviewer='Test',date='2026-09-19',evidence=Evidence(self.root))
        rescanned=next(c for c in deps.scan(self.data,self.root)['candidates'] if c['id']==candidate['id'])
        self.assertEqual(deps.decision_state(rescanned,self.data,Evidence(self.root)),'rejected')
        path=self.root/'notebook.html';path.write_text(path.read_text().replace('Does not depend','Depends'))
        self.assertEqual(deps.decision_state(candidate,self.data,Evidence(self.root)),'stale')
        with self.assertRaises(ValueError):
            deps.record_decision(self.data,candidate,state='accepted',reason='Changed',reviewer='Test',date='2026-09-19',evidence=Evidence(self.root))

    def test_metadata_packet_preserves_qualification_and_reports_omissions(self):
        path=self.root/'notebook.html'
        path.write_text(path.read_text().replace('<p>Does not depend',
            '<p>Working conditional theorem.</p><div class="math">B = C + D</div>'
            '<p>Scope: only supplied witnesses.</p><p>Does not depend'))
        packet=deps.metadata_packet(self.data,'lem:a',self.root,limit=2,width=20)
        passage=packet['passages'][0]
        self.assertEqual(packet['assessment'],'Working proof')
        self.assertFalse(packet['proof_ready'])
        self.assertIn('Orientation only',deps.packet_text(packet))
        self.assertEqual(passage['included_blocks'],2)
        self.assertGreater(passage['omitted_selected_blocks'],0)
        self.assertTrue(passage['excerpts'][0]['truncated'])
        self.assertIn('B = C + D',passage['excerpts'][1]['text'])
        self.assertIn('omitted',deps.packet_text(packet))
        with self.assertRaises(ValueError):deps.metadata_packet(self.data,'missing',self.root)

    def test_packet_exposes_partial_formalization_scope(self):
        self.data['claims'][0]['formalization'].update(status='partial',scope='Identity only; equality refuted.')
        output=deps.packet_text(deps.metadata_packet(self.data,'lem:a',self.root))
        self.assertIn('partial; Identity only; equality refuted.',output)

    def test_markup_stripping_preserves_raw_math_inequalities(self):
        text='<p>Working theorem: q<n and a>b, with <strong>fixed</strong> p.</p>'
        cleaned=deps.strip_markup(text)
        self.assertIn('q<n and a>b',cleaned)
        self.assertIn('fixed',cleaned)
        self.assertNotIn('<strong>',cleaned)
        self.assertIn(r'\(a<p and b>c\)',deps.strip_markup(r'<p>Scope \(a<p and b>c\).</p>'))

    def test_acceptance_requires_a_matching_curated_relationship(self):
        candidate=next(c for c in deps.scan(self.data,self.root)['candidates'] if c['method']=='notebook_link')
        with self.assertRaises(ValueError):
            deps.record_decision(self.data,candidate,state='accepted',reason='Read it',reviewer='Test',date='2026-09-19',evidence=Evidence(self.root))


if __name__=='__main__':unittest.main()
