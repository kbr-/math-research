import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'tools'))
from notebook_context import budgets, excerpt


class ContextBudgetTest(unittest.TestCase):
    def config(self, regions=None, total=100):
        return {'version':1, 'hard_multiplier':1.5, 'characters_per_word':12,
                'total_soft_words':total, 'regions':regions or {'@intro':2}}

    def book(self, prefix, record=''):
        return prefix+'<section id="research-record">'+record+'</section>'

    def test_boundaries_and_soft_warning(self):
        for count, status in [(2,'ok'),(3,'soft'),(4,'hard')]:
            with self.subTest(count=count):
                result=budgets(self.book('a '*count), self.config())
                self.assertEqual(result['regions'][0]['status'], status)
                self.assertEqual(result['passed'], status!='hard')

    def test_dense_tex_character_guard_and_html_exclusions(self):
        text=r'<p title="ignored words">\('+'x'*37+r'\)</p><!-- ignored -->'
        result=budgets(self.book(text), self.config())
        self.assertEqual(result['regions'][0]['words'],1)
        self.assertFalse(result['passed'])
        text=r'<h2>Title</h2><p>A <b>bold</b> word &amp; \(x<y\).</p><table><tr><td>cell</td></tr></table>'
        visible=excerpt.visible_text(text)
        self.assertIn(r'\(x<y\)', visible)
        self.assertIn('A bold word &', visible)
        self.assertIn('cell', visible)
        self.assertEqual(excerpt.visible_text('<b>hel</b>lo'), 'hello')

    def test_nested_sections_count_once(self):
        source=self.book('intro<section id="a">parent<section id="b">child</section>tail</section>')
        result=budgets(source,self.config({'@intro':5,'a':5,'b':5}))
        self.assertEqual([r['words'] for r in result['regions']],[1,2,1])
        self.assertEqual(result['total']['words'],4)

    def test_aggregate_blocks_even_if_individual_budgets_pass(self):
        result=budgets(self.book('a b<section id="a">c d</section>'),self.config({'@intro':10,'a':10},total=2))
        self.assertTrue(all(r['status']=='ok' for r in result['regions']))
        self.assertFalse(result['passed'])

    def test_unknown_missing_duplicate_and_unnamed_sections_fail(self):
        for prefix,cfg in [('<section id="a"></section>',self.config()),
                           ('',self.config({'@intro':2,'a':2})),
                           ('<section id="a"></section><section id="a"></section>',self.config({'@intro':2,'a':2})),
                           ('<section></section>',self.config())]:
            with self.subTest(prefix=prefix), self.assertRaises(ValueError):
                budgets(self.book(prefix),cfg)

    def test_record_must_be_top_level_after_closed_sections(self):
        for source in ['<p>no record</p>',
                       '<section id="a"><section id="research-record"></section></section>',
                       '<section id="a">open<section id="research-record"></section>',
                       '<h2>open<section id="research-record"></section>']:
            with self.subTest(source=source), self.assertRaises(ValueError):
                budgets(source,self.config({'@intro':5,'a':5}))

    def test_record_is_unlimited_and_math_is_not_a_section(self):
        source=self.book(r'\(a<section>b\)', '<article>'+'many '*10000+'</article>')
        result=budgets(source,self.config({'@intro':100}))
        self.assertTrue(result['passed'])
        self.assertEqual(result['total']['words'],1)

    def test_invalid_policy_rejected(self):
        for field,value in [('hard_multiplier',.5),('characters_per_word',0),('total_soft_words',True)]:
            cfg=self.config();cfg[field]=value
            with self.subTest(field=field),self.assertRaises(ValueError):budgets(self.book(''),cfg)

    def test_ci_command_saves_report_and_fails_overflow(self):
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary);book=root/'book.html';cfg=root/'budget.json';out=root/'report.json'
            book.write_text(self.book('one two three four'));cfg.write_text(json.dumps(self.config()))
            result=subprocess.run([sys.executable,str(ROOT/'tools/notebook_context.py'),
                                   '--notebook',str(book),'--config',str(cfg),'--out',str(out)],
                                  text=True,capture_output=True)
            self.assertEqual(result.returncode,1,result.stderr)
            self.assertFalse(json.loads(out.read_text())['passed'])
            self.assertIn('excess 1 words',result.stdout)


if __name__=='__main__':unittest.main()
