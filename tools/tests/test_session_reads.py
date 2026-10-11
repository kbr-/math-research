import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('session_reads', ROOT / 'tools' / 'session_reads.py')
tool = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tool)


def call(name, **given):
    return json.dumps({'message': {'content': [{'type': 'tool_use', 'name': name, 'input': given}]}})


TRANSCRIPT = [
    call('Bash', command='./compute.sh phase turn-1 reading'),
    call('Read', file_path='/scratch/src/document.tex', offset=590, limit=190),
    call('Bash', command="sed -n 1318,1346p /scratch/src/document.tex | cut -c1-300"),
    call('Bash', command='cut -c1-150 /scratch/dep50.txt | head -14'),
    'not json',
    call('Bash', command='./tools/finish-turn.py turn-1'),
    call('Read', file_path='/scratch/src/later.tex'),
]


class SessionReadsTest(unittest.TestCase):
    def test_the_reads_of_a_window_with_their_ranges(self):
        found = tool.window(tool.calls(TRANSCRIPT), 'phase turn-1', 'finish-turn.py turn-1')
        opened = tool.reads(found)
        self.assertEqual(sorted(opened), ['dep50.txt', 'document.tex'])
        self.assertEqual(tool.shown(opened['document.tex']), '590-779, 1318-1346')
        self.assertEqual(tool.shown(opened['dep50.txt']), 'named in 1 other commands')
        # Without markers the whole transcript is read, and a Read without an offset is its first 2000 lines.
        everything = tool.reads(tool.window(tool.calls(TRANSCRIPT), None, None))
        self.assertEqual(tool.shown(everything['later.tex']), '1-2000')

    def test_ranges_join_and_cover(self):
        self.assertEqual(tool.merged([(10, 20), (21, 30), (40, None), (50, 60)]), [(10, 30), (40, None)])
        spans = [(590, 779), (1318, 1346), None]
        self.assertTrue(tool.covered((600, 700), spans))
        self.assertFalse(tool.covered((1340, 1414), spans))

    def test_a_statement_just_past_a_range_read_is_listed(self):
        source = '\n'.join(['text'] * 9 + ['\\begin{definition}'] + ['text'] * 9 + ['\\begin{proposition}[Bounds]']
                           + ['text'] * 200 + ['\\begin{theorem}'])
        # Lines 5-15 were read: the definition inside is read, the proposition at line 20 is five lines on,
        # the theorem at 221 is beyond the look-ahead; definitions are not statements for this purpose.
        self.assertEqual(tool.statements_ahead(source, [(5, 15)]), [(20, '\\begin{proposition}[Bounds]')])
        self.assertEqual(tool.statements_ahead(source, [(5, 25)]), [])
        self.assertEqual(tool.statements_ahead('theorem foo (x : Nat) :\n  x = x', [(1, 1)]), [])
        lean = 'def a := 1\n\n@[simp] theorem foo : a = 1 := rfl\nprivate lemma bar : a = 1 := rfl\n-- theorem no'
        self.assertEqual([number for number, _ in tool.statements_ahead(lean, [(1, 1)])], [3, 4])
        self.assertEqual(tool.statements_ahead('x\n\\begin{theorem*}', [(1, 1)]), [(2, '\\begin{theorem*}')])
        # A whole-file read is the reading tool's first 2000 lines, not the file.
        self.assertEqual(tool.read_span({'file_path': 'a.tex'}), (1, 2000))
        long = '\n'.join(['text'] * 2010 + ['\\begin{lemma}'])
        self.assertEqual([number for number, _ in tool.statements_ahead(long, [tool.read_span({})])], [2011])
        found = tool.window(tool.calls(TRANSCRIPT), None, None)
        self.assertEqual(tool.ranged_paths(found), {'/scratch/src/document.tex': [(590, 779), (1318, 1346)],
                                                    '/scratch/src/later.tex': [(1, 2000)]})

    def test_a_turn_s_readings_are_those_after_the_finisher_that_started_it(self):
        import tempfile
        with tempfile.TemporaryDirectory() as folder:
            source = Path(folder) / 'paper.tex'
            source.write_text('\n'.join(['text'] * 19 + ['\\begin{lemma}[Next]'] + ['text'] * 5))
            lines = [call('Read', file_path=str(source), offset=1, limit=3),
                     call('Bash', command='./tools/finish-turn.py turn-1 --next turn-2'),
                     call('Bash', command=f'sed -n 5,15p {source}')]
            found = tool.turn_lines(lines, 'turn-2')
            self.assertEqual(len(found), 1)
            self.assertIn('paper.tex line 20', found[0])
            self.assertEqual(tool.current_lines(lines), found)
            # A session that has run no finisher yet is read whole; a ranged source that is no file is said.
            self.assertEqual(tool.current_lines(lines[2:]), found)
            gone = tool.current_lines([call('Bash', command='sed -n 5,15p $NO_SUCH_VARIABLE/paper.tex')])
            self.assertEqual(len(gone), 1)
            self.assertIn('NOT CHECKED: $NO_SUCH_VARIABLE/paper.tex', gone[0])
            # A turn the finisher did not start, or whose name only begins another's, has no window.
            self.assertEqual(tool.turn_lines(lines, 'turn-9'), [])
            self.assertEqual(tool.turn_lines(lines, 'turn'), [])
            self.assertEqual(tool.turn_lines([call('Bash', command='echo "--next turn-2"')] + lines[2:], 'turn-2'), [])
            # A read that reaches the statement prints nothing; a whole-file read covers its first 2000 lines.
            lines.append(call('Read', file_path=str(source), offset=16, limit=10))
            self.assertEqual(tool.turn_lines(lines, 'turn-2'), [])

    def test_a_conclusion_about_a_file_read_in_part_is_listed(self):
        import tempfile

        def said(entry, lines):
            return tool.partial_conclusions(entry, tool.calls(lines))
        with tempfile.TemporaryDirectory() as folder:
            record = Path(folder) / 'AUDIT.md'
            record.write_text('\n'.join(['line'] * 248 + ['## Revision note: layout'] + ['line'] * 28))
            part = [call('Bash', command=f'sed -n 1,60p {record}'), call('Bash', command=f'sed -n 180,225p {record}'),
                    call('Bash', command=f'grep -c sorry {record}')]            # a search is not a reading
            entry = '<p>The record AUDIT.md reports a complete build for the present state. Other text.</p>'
            found = said(entry, part)
            self.assertEqual(len(found), 1)
            self.assertIn('PARTIAL READ: AUDIT.md was read to line 225 of 277', found[0])
            self.assertIn('reports a complete build', found[0])
            # Passed: the range said in the paragraph; no verb of saying; the file read to its end, or shown whole.
            self.assertEqual(said('<p>AUDIT.md, lines 1 to 60, reports a build.</p>', part), [])
            self.assertEqual(said('<p>I opened AUDIT.md for its first section.</p>', part), [])
            # The verb belongs to the file: a noun elsewhere, or what someone else says, is not it.
            self.assertEqual(said('<p>The record of 17 states is in AUDIT.md.</p>', part), [])
            self.assertEqual(said('<p>The reviewer says that AUDIT.md is long.</p>', part), [])
            # The limit, recorded: someone else's saying just after the name is taken for the file's.
            self.assertEqual(len(said('<p>It is in AUDIT.md, as the reviewer says.</p>', part)), 1)
            self.assertEqual(len(said('<p>AUDIT.md, the project\'s own, states a build.</p>', part)), 1)
            # One file under two spellings is one file; of two files of one name, one read to its end passes.
            both = part + [call('Bash', command=f'cd {folder} && sed -n 226,277p AUDIT.md')]
            self.assertEqual(said(entry, both), [])
            other = Path(folder) / 'sub' / 'AUDIT.md'
            other.parent.mkdir()
            other.write_text('one\ntwo')
            self.assertEqual(said(entry, part + [call('Bash', command=f'sed -n 1,2p {other}')]), [])
            self.assertEqual(said(entry, part + [call('Bash', command=f'sed -n 226,277p {record}')]), [])
            self.assertEqual(said(entry, part + [call('Bash', command=f'cat {record}')]), [])
            self.assertEqual(said(entry, part + [call('Read', file_path=str(record))]), [])
            # Not listed: a file never opened by a range, and one that is not on disk.
            self.assertEqual(said(entry, [call('Bash', command=f'grep -c sorry {record}')]), [])
            self.assertEqual(said(entry, [call('Bash', command='sed -n 1,9p /nowhere/AUDIT.md')]), [])
            # A path written with a variable the command assigns, or after a change of directory, is resolved.
            for command in (f'R={folder}; sed -n 1,60p $R/AUDIT.md', f'R={folder}; sed -n 1,60p ${{R}}/AUDIT.md',
                            f'cd {folder} && sed -n 1,60p AUDIT.md', f'D={folder}; cd $D; sed -n 1,60p AUDIT.md'):
                self.assertIn('read to line 60 of 277', said(entry, [call('Bash', command=command)])[0], command)
            # The unread parts of a file the entry names are listed, also where no sentence says what it says.
            unread = tool.unread_ends('<p>Read in part: AUDIT.md.</p>', tool.calls(part))
            self.assertEqual(unread, ['  UNREAD: AUDIT.md, 277 lines, named in the entry: not read are lines '
                                      '61-179, 226-277', '    unread heading, line 249: ## Revision note: layout'])
            self.assertEqual(tool.unread_ends('<p><a href="x/AUDIT.md">the record</a></p>', tool.calls(part)), [])
            self.assertEqual(tool.unread_ends('<p>Another file.</p>', tool.calls(part)), [])
            self.assertEqual(tool.unread_ends('<p>AUDIT.md</p>', tool.calls([call('Read', file_path=str(record))])), [])
            # One turn's calls only.
            lines = [call('Bash', command='./tools/finish-turn.py turn-1 --next turn-2')] + part
            self.assertEqual(len(tool.turn_partial(lines, 'turn-2', entry)), 1)
            self.assertEqual(tool.turn_partial(lines, 'turn-3', entry), [])

    def test_what_a_draft_names(self):
        draft = ('<p>Read in <a href="research/results/x/out.txt">output</a> and document.tex, lines 1380 to '
                 '1414 and line 12; the scratch file is in its corrected form.</p>')
        paths, ranges = tool.named(draft)
        self.assertEqual(paths, ['document.tex', 'out.txt'])
        self.assertEqual(ranges, [(12, 12), (1380, 1414)])
        # The limit, recorded: a file spoken of without its name gives nothing to compare.
        self.assertEqual(tool.named('<p>The scratch file is in its corrected form.</p>'), ([], []))


if __name__ == '__main__':
    unittest.main()
