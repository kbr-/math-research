import contextlib
from datetime import datetime, timedelta, timezone
import io
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import haiku_judge  # noqa: E402
import stand_in_review as tool  # noqa: E402

NOW = datetime(2026, 10, 10, 12, 0, tzinfo=timezone.utc)


def stamp(minutes_ago):
    return (NOW - timedelta(minutes=minutes_ago)).strftime('%Y-%m-%dT%H:%M:%S.000Z')


class StandInReviewTest(unittest.TestCase):
    def setUp(self):
        scratch = tempfile.TemporaryDirectory()
        self.addCleanup(scratch.cleanup)
        self.root = Path(scratch.name)
        (self.root / 'skills' / 'engineering-discipline').mkdir(parents=True)
        (self.root / tool.SKILL).write_text('THE SKILL: measure before claiming.\n')
        self.transcript = self.root / 'session.jsonl'
        said = lambda ago, text, **more: {'type': 'assistant', 'timestamp': stamp(ago), 'message': {'content': [
            {'type': 'text', 'text': text}, {'type': 'tool_use', 'name': 'Bash', 'input': {'command': 'x'}}]}, **more}
        lines = [said(200, 'Three hours old.'), said(100, 'It is surely   faster now.'),
                 {'type': 'user', 'timestamp': stamp(90), 'message': {'content': [{'type': 'text', 'text': 'the user speaks'}]}},
                 said(50, 'A subagent wrote this.', isSidechain=True), said(30, 'The suite passed.'), said(5, 'Done; nothing measured.')]
        self.transcript.write_text('not json\n' + ''.join(json.dumps(line) + '\n' for line in lines))
        self.asked = []

    def ask(self, *objections, fail=None):
        def answer(prompt, timeout, model, thinking):
            self.asked.append((prompt, model, thinking))
            if fail:
                raise haiku_judge.Failed(fail)
            return {'objections': list(objections)}
        return answer

    def run_tool(self, *argv, ask=None, now=NOW):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            status = tool.main(['--transcript', str(self.transcript), *argv], root=self.root, now=now, ask=ask or self.ask())
        return status, out.getvalue().splitlines()

    def test_the_first_review_reads_the_assistants_last_two_hours_after_the_skill_and_the_instruction(self):
        status, lines = self.run_tool(ask=self.ask(
            {'quote': 'it is surely faster now.', 'objection': 'You measured  nothing.'},
            {'quote': 'words that are not there', 'objection': 'Invented.'}, {'quote': 'The suite passed.', 'objection': ' '}, 'no object'))
        prompt, model, thinking = self.asked[0]
        self.assertEqual((status, model, thinking), (0, 'claude-opus-5-5', True))
        self.assertTrue(prompt.startswith('THE SKILL: measure before claiming.\n\n\nCheck whether the skill above was followed'))
        self.assertTrue(prompt.endswith('THE ASSISTANT\'S TEXT:\nIt is surely   faster now.\n\nThe suite passed.\n\nDone; nothing measured.\n'))
        # An objection is kept only with a quote found in the text, whatever its spacing and case, and with words of its own.
        self.assertEqual(lines[1:], ['1. You measured nothing.', '   on: "it is surely faster now."'])
        self.assertRegex(lines[0], r'^Stand-in review of 70 characters written since 10:00 UTC: 1 objections '
                                   r'\(research/logs/stand-in-review/20261010T120000\.json\)\. Check each against the record; the next entry '
                                   r'answers them in a paragraph starting "Review\."$')
        kept = json.loads((self.root / tool.STATE / '20261010T120000.json').read_text())
        self.assertEqual((kept['dropped'], len(kept['objections']), kept['given']), (3, 1, 70))     # 26, 17 and 23 characters and two blank lines between
        self.assertEqual(tool.unanswered(self.root), 'research/logs/stand-in-review/20261010T120000.json')

    def test_it_runs_again_only_twenty_minutes_later_and_then_reads_what_was_written_since(self):
        self.run_tool(now=NOW - timedelta(minutes=19, seconds=59))
        status, lines = self.run_tool()
        self.assertEqual((status, lines, len(self.asked)), (0, [
            'Stand-in review: it ran 19 minutes ago; the first checkpoint 20 minutes after that run gets the next, of everything since.'], 1))
        self.run_tool('--force')
        self.assertEqual(len(self.asked), 2)
        tool.keep(self.root, {'fired': (NOW - timedelta(minutes=20)).isoformat()})
        status, lines = self.run_tool()
        self.assertTrue(self.asked[2][0].endswith("THE ASSISTANT'S TEXT:\nDone; nothing measured.\n"))
        self.assertEqual(lines, ['Stand-in review of 23 characters written since 11:40 UTC: no objection.'])
        self.assertIsNone(tool.unanswered(self.root))
        # A review with no objection leaves the one before it owed, and its own time as the last run.
        tool.keep(self.root, {'fired': (NOW - timedelta(minutes=40)).isoformat(), 'unanswered': 'research/logs/stand-in-review/20261010T120000.json'})
        self.run_tool()
        self.assertEqual(tool.state_of(self.root), {'fired': NOW.isoformat(), 'unanswered': 'research/logs/stand-in-review/20261010T120000.json'})

    def test_what_cannot_be_reviewed_is_said_and_never_fails_and_leaves_the_review_due(self):
        status, lines = self.run_tool(ask=self.ask(fail='no answer within 180 s'))
        self.assertEqual((status, lines), (0, ['Stand-in review gave no verdict (no answer within 180 s); this checkpoint passes without one.']))
        self.assertEqual(tool.state_of(self.root), {})
        tool.keep(self.root, {'fired': (NOW - timedelta(minutes=1)).isoformat()})
        self.assertEqual(self.run_tool(now=NOW + timedelta(hours=1))[1], ['Stand-in review not run: the assistant wrote nothing since it last ran.'])
        (self.root / tool.SKILL).unlink()
        self.assertEqual(self.run_tool('--force')[1], [
            'Stand-in review not run: neither of skills/engineering-discipline/SKILL.md and AGENTS.md is here.'])
        self.assertEqual(tool.review(self.root, None, NOW, force=True), ['Stand-in review not run: no transcript of this session was found.'])
        self.assertEqual(len(self.asked), 1)

    def test_a_branch_without_the_skill_is_held_to_its_agents_file(self):
        (self.root / 'AGENTS.md').write_text('THE RULES: a belief is no evidence.\n')
        self.run_tool()
        self.assertTrue(self.asked[0][0].startswith('THE SKILL: measure before claiming.\n\n\nCheck whether the skill above was followed'))
        self.assertIn('the engineer whose skill it is. List', self.asked[0][0])
        (self.root / tool.SKILL).unlink()
        tool.keep(self.root, {})
        self.run_tool()
        self.assertTrue(self.asked[1][0].startswith('THE RULES: a belief is no evidence.\n\n\nCheck whether the rules above were followed'))
        self.assertIn('the engineer whose rules they are. List', self.asked[1][0])
        self.assertIn('where a\ndirective of the rules was not followed', self.asked[1][0])

    def test_the_sessions_transcript_is_found_only_inside_a_claude_code_session(self):
        folder = self.root / '.claude' / 'projects' / '-work-my-repo'
        folder.mkdir(parents=True)
        for name, age in (('a.jsonl', 50), ('b.jsonl', 5)):
            (folder / name).write_text('{}\n')
            os.utime(folder / name, (NOW.timestamp() - age, NOW.timestamp() - age))
        inside = {'CLAUDECODE': '1'}
        self.assertEqual(tool.session_transcript(Path('/work/my.repo'), self.root, inside), folder / 'b.jsonl')
        self.assertIsNone(tool.session_transcript(Path('/work/other'), self.root, inside))
        # Another agent's finisher in the same directory would be given this session's text.
        self.assertIsNone(tool.session_transcript(Path('/work/my.repo'), self.root, {}))
        # The session's own transcript is taken where the session names itself, though another was written later.
        named = {**inside, 'CLAUDE_CODE_SESSION_ID': 'a'}
        self.assertEqual(tool.session_transcript(Path('/work/my.repo'), self.root, named), folder / 'a.jsonl')
        self.assertEqual(tool.session_transcript(Path('/work/my.repo'), self.root, {**inside, 'CLAUDE_CODE_SESSION_ID': 'gone'}), folder / 'b.jsonl')

    def test_a_codex_session_is_read_from_the_file_its_thread_names(self):
        thread, other = '01a12817-e695-70f2-a532-dc75749bd269', '01a12817-e695-70f2-a532-dc75749bd260'
        day = self.root / '.codex' / 'sessions' / '2026' / '10' / '10'
        day.mkdir(parents=True)
        item = lambda ago, payload: json.dumps({'timestamp': stamp(ago), 'type': 'response_item', 'payload': payload}) + '\n'
        said = lambda role, text, **more: {'type': 'message', 'role': role, 'content': [{'type': 'output_text' if role == 'assistant' else 'input_text', 'text': text}], **more}
        (day / f'rollout-2026-10-10T10-00-00-{thread}.jsonl').write_text(
            item(200, said('assistant', 'Three hours old.')) + item(60, said('user', 'the user speaks'))
            + item(50, said('assistant', 'Reading the proof.', phase='commentary'))
            + item(40, {'type': 'reasoning', 'summary': [{'type': 'summary_text', 'text': 'private reasoning'}]})
            + item(30, {'type': 'agent_message', 'author': '/root/reviewer', 'content': [{'type': 'input_text', 'text': 'a subagent reports'}]})
            + item(20, {'type': 'custom_tool_call_output', 'output': 'tool output'})
            + item(10, said('assistant', 'The lemma holds; it is surely general.', phase='final_answer')))
        (day / f'rollout-2026-10-10T11-00-00-{other}.jsonl').write_text(item(5, said('assistant', 'Another thread.')))
        home = {'CODEX_THREAD_ID': thread}
        found = tool.session_transcript(self.root, self.root, home)
        self.assertEqual(found.name, f'rollout-2026-10-10T10-00-00-{thread}.jsonl')
        self.assertEqual(tool.written_since(found, NOW - tool.FIRST), ['Reading the proof.', 'The lemma holds; it is surely general.'])
        # A Codex home given by its variable; a thread with no file, a thread with two, and no thread's name: nothing.
        self.assertEqual(tool.session_transcript(self.root, self.root / 'elsewhere', {**home, 'CODEX_HOME': str(self.root / '.codex')}), found)
        self.assertIsNone(tool.session_transcript(self.root, self.root, {'CODEX_THREAD_ID': other[:-1] + '1'}))
        # What is no thread's name is no pattern to search by, though it would match one file.
        self.assertIsNone(tool.session_transcript(self.root, self.root, {'CODEX_THREAD_ID': thread[:-1] + '[9]'}))
        # A Claude Code session started from a Codex one is a Claude Code session.
        self.assertIsNone(tool.session_transcript(self.root, self.root, {**home, 'CLAUDE_CODE_SESSION_ID': 'x', 'CLAUDECODE': '1'}))
        (day.parent / f'rollout-copy-{thread}.jsonl').write_text('')
        self.assertIsNone(tool.session_transcript(self.root, self.root, home))

    def test_a_branch_turns_it_off_and_an_answered_review_is_owed_no_more(self):
        (self.root / 'tools' / 'hooks').mkdir(parents=True)
        (self.root / 'tools' / 'hooks' / 'checks_off').write_text('review\n')
        self.assertEqual((self.run_tool(), self.asked), ((0, []), []))
        (self.root / 'tools' / 'hooks' / 'checks_off').write_text('judge\n')
        self.run_tool(ask=self.ask({'quote': 'The suite passed.', 'objection': 'In how long?'}))
        owed = 'research/logs/stand-in-review/20261010T120000.json'
        self.assertEqual(self.run_tool('--unanswered'), (0, [owed]))
        self.assertEqual(self.run_tool('--answered'), (0, []))
        self.assertEqual((self.run_tool('--unanswered'), tool.unanswered(self.root)), ((0, []), None))
        self.assertEqual(tool.state_of(self.root)['fired'], NOW.isoformat())


if __name__ == '__main__':
    unittest.main()
