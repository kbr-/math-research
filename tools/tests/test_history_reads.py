import json
import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import history_reads as tool

QUEUE = ('<section id="proposed-next-step"><h2>Proposed next step</h2><p>Develop item-1 next.</p></section>'
         '<section id="lead-queue"><h2>Queue</h2><ol>'
         '<li data-check="item-1" data-source="a1"><a href="#a1">item-1</a> (check): Does the bound hold?</li>'
         '</ol></section><section id="research-record">'
         '<article id="a1" data-kind="research"><h3>Queued it</h3></article>'
         '<article id="a2" data-kind="research" data-check="item-1"><h3>First look</h3></article>'
         '<article id="a3" data-kind="research" data-check="item-1"><h3>Second look</h3></article>'
         '</section>')


class HistoryReadsTest(unittest.TestCase):
    def test_earlier_entries_not_read_since_the_session_began_are_listed(self):
        self.assertEqual(tool.unread_history(QUEUE, set()), [('item-1', ['a2', 'a3'])])
        self.assertEqual(tool.unread_history(QUEUE, {'a2'}), [('item-1', ['a3'])])
        self.assertEqual(tool.unread_history(QUEUE, {'a2', 'a3'}), [])
        self.assertEqual(tool.unread_history('<p>No next step.</p>', set()), [])

    def test_only_reads_of_this_notebook_since_the_start_count(self):
        lines = [json.dumps({'unix_s': 5, 'notebook': 'main', 'anchors': ['a2']}),
                 json.dumps({'unix_s': 20, 'notebook': 'side', 'anchors': ['a3']}),
                 json.dumps({'unix_s': 30, 'notebook': 'main', 'anchors': ['a3', 'x']}), 'not json']
        self.assertEqual(tool.read_anchors(lines, 10, 'main'), {'a3', 'x'})


if __name__ == '__main__':
    unittest.main()
