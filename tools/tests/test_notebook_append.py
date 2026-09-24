"""notebook-append.py inserts after the last record article and replaces the next step."""
import importlib.util
from pathlib import Path
import sys
import unittest

TOOLS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS))
spec = importlib.util.spec_from_file_location('notebook_append', TOOLS / 'notebook-append.py')
tool = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tool)

NOTEBOOK = ('<section id="proposed-next-step">\n<h2>Proposed next step</h2>\n<p>old</p>\n</section>\n'
            '<section id="research-record">\n<h2>Record</h2>\n<article id="a1">one</article>\n'
            '<article id="a2">two</article>\n</section>\n<footer></footer>')


class NotebookAppendTests(unittest.TestCase):
    def test_appends_after_last_article_and_replaces_next_step(self):
        out = tool.append(NOTEBOOK, '<article id="a3">three</article>\n', '<p>new</p>')
        self.assertIn('<article id="a2">two</article>\n<article id="a3">three</article>\n</section>', out)
        self.assertIn('<h2>Proposed next step</h2>\n<p>new</p>\n</section>', out)
        self.assertNotIn('<p>old</p>', out)

    def test_keeps_next_step_without_option(self):
        out = tool.append(NOTEBOOK, '<article id="a3">three</article>')
        self.assertIn('<p>old</p>', out)

    def test_fails_closed(self):
        with self.assertRaisesRegex(ValueError, 'already present'):
            tool.append(NOTEBOOK, '<article id="a2">dup</article>')
        with self.assertRaisesRegex(ValueError, 'one <article'):
            tool.append(NOTEBOOK, '<p>not an article</p>')
        with self.assertRaisesRegex(ValueError, 'research-record'):
            tool.append('<p>none</p>', '<article id="x">x</article>')


if __name__ == '__main__':
    unittest.main()
