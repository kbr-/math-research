import importlib.util
import io
import json
import tempfile
import unittest
from contextlib import redirect_stderr
from pathlib import Path
from unittest import mock

spec = importlib.util.spec_from_file_location('reviewer_brief', Path(__file__).resolve().parents[1] / 'hooks/reviewer_brief.py')
hook = importlib.util.module_from_spec(spec)
spec.loader.exec_module(hook)


def call(prompt, agent='medium-reviewer', tool='Agent'):
    return {'tool_name': tool, 'tool_input': {'subagent_type': agent, 'prompt': prompt}}


class ReviewerBriefTest(unittest.TestCase):
    def run_hook(self, payload):
        err = io.StringIO()
        with mock.patch('sys.stdin', io.StringIO(json.dumps(payload))), redirect_stderr(err):
            return hook.main(), err.getvalue()

    def test_a_brief_that_hands_over_a_whole_document_is_refused(self):
        for prompt in ('Read the file, then read the whole Path section of PLAN.md once.',
                       'Audit the rows against the entire theory.',
                       'Read notes/x/PLAN.md in full before you start.',
                       'First read all of the notebook.'):
            with self.subTest(prompt=prompt):
                status, err = self.run_hook(call(prompt))
                self.assertEqual(status, 2)
                self.assertIn('tools/notebook-excerpt.py ANCHOR --out FILE', err)
        status, err = self.run_hook(call('Read the whole Path.'))
        self.assertIn('("whole Path")', err)

    def test_a_narrow_brief_other_agents_and_other_tools_pass(self):
        narrow = (f'Audit every row in {Path(__file__).resolve()}; read that file in full first. It holds the increments '
                  'the rows cite. Search PLAN.md only for a clause you challenge.')
        for payload in (call(narrow), call('Read the whole Path.', agent='Explore'),
                        call('Read the whole Path.', tool='Bash'), {'tool_name': 'Agent'}):
            with self.subTest(payload=payload):
                self.assertEqual(self.run_hook(payload), (0, ''))

    def test_the_refusal_names_a_further_tool_only_where_the_branch_s_own_module_does(self):
        with tempfile.TemporaryDirectory() as without, tempfile.TemporaryDirectory() as tools:
            there = hook.refusal(call('Read the whole notebook.'), tools=Path(without))
            (Path(tools) / 'branch_own.py').write_text('EXCERPT_TOOL = "`tools/rows.py --brief` for a table or "\n')
            here = hook.refusal(call('Read the whole notebook.'), tools=Path(tools))
        self.assertIn('built with `tools/rows.py --brief` for a table or `tools/notebook-excerpt.py ANCHOR --out FILE` '
                      'for the notebook', here)
        self.assertNotIn('rows.py', there)
        self.assertIn('built with `tools/notebook-excerpt.py ANCHOR --out FILE` for the notebook', there)

    def test_an_entry_draft_needs_its_commit_message_in_the_brief(self):
        with tempfile.TemporaryDirectory() as folder:
            draft, message = Path(folder) / 'entry_x.html', Path(folder) / 'commit_x.txt'
            draft.write_text('<article></article>')
            message.write_text('Main: x')
            refused = hook.refusal(call(f'Review the draft {draft} with excerpts.'))
            self.assertIn('no drafted commit message', refused)
            self.assertIsNone(hook.refusal(call(f'Review the draft {draft} and the commit message {message}; '
                                                'run one claim search.')))
            # A brief without an entry draft (a blind stage, a tool review) needs none.
            notes = Path(folder) / 'blind.md'
            notes.write_text('goal')
            self.assertIsNone(hook.refusal(call(f'Read {notes} only.')))
            # A tracked page named in a layout review is not a draft; a test file is not a commit message.
            page = Path(__file__).resolve().parents[2] / 'index.html'
            self.assertIsNone(hook.refusal(call(f'Check the layout of {page}.')))
            stray = Path(folder) / 'test_commit_hook.py'
            stray.write_text('')
            self.assertIn('no drafted commit message', hook.refusal(call(f'Review {draft} and {stray}.')))

    def test_an_entry_draft_needs_a_record_search_in_the_brief(self):
        # 16 October 2026: two record searches in a row missed a registered result; the reviewer's search found it.
        with tempfile.TemporaryDirectory() as folder:
            draft, message = Path(folder) / 'entry_x.html', Path(folder) / 'commit_x.txt'
            draft.write_text('<article data-kind="research"></article>')
            message.write_text('Main: x')
            base = f'Review the draft {draft} and the commit message {message}.'
            page = Path(folder) / 'fixture.html'   # a framework tool's review names other pages
            page.write_text('<html><body>fixture</body></html>')
            self.assertIsNone(hook.refusal(call(f'Review the tool on {page} and the commit message {message}.')))
            self.assertEqual(hook.refusal(call(base)), hook.NO_SEARCH_REASON)
            for ask in ('One or two claim searches are allowed (python3 tools/search-claims.py WORDS).',
                        'Run one record search in the words of the next attempt.',
                        'Search the registry for results the draft misses.',
                        'Make one or two searches of the record before the audit.',
                        'A claim search for the missed results.',
                        # 17 October 2026: refused on the "not" of "does not cite".
                        'Run two searches with python3 tools/search-claims.py -n 5 and report registered '
                        'results the draft does not cite that bear on it.'):
                with self.subTest(ask=ask):
                    self.assertIsNone(hook.refusal(call(f'{base} {ask}')))
            # A sentence that names the search to deny it does not ask for one (the builds' reviewer).
            for denial in ('No record search is needed.', 'Skip the claim search.', 'A record search is not needed.'):
                with self.subTest(denial=denial):
                    self.assertEqual(hook.refusal(call(f'{base} {denial}')), hook.NO_SEARCH_REASON)
            notes = Path(folder) / 'blind.md'
            notes.write_text('goal')
            self.assertIsNone(hook.refusal(call(f'Read {notes} only.')))   # no draft, no search needed

    def test_input_that_is_not_json_passes(self):
        with mock.patch('sys.stdin', io.StringIO('not json')):
            self.assertEqual(hook.main(), 0)




class BlindStageTest(unittest.TestCase):
    # The exposing case, 17 October 2026: the stage-one brief beside the previous review's text.
    PROMPT = 'Read {d}/stage1.txt and do what it asks. Its files are your only sources.'

    def test_a_blind_brief_beside_unnamed_files_is_refused(self):
        with tempfile.TemporaryDirectory() as d:
            Path(d, 'stage1.txt').write_text('BLIND STAGE\nStage one of a route review. Results: ' + d + '/results.txt\n')
            Path(d, 'results.txt').write_text('claims\n')
            Path(d, 'six.txt').write_text('the previous review and its route\n')
            repo = Path(__file__).resolve().parents[2]
            self.assertEqual(hook.blind_leaks(self.PROMPT.format(d=d), repo), [str(Path(d, 'six.txt').resolve())])
            Path(d, 'six.txt').unlink()
            self.assertEqual(hook.blind_leaks(self.PROMPT.format(d=d), repo), [])

    def test_the_reviewer_s_ways_around_are_refused(self):
        # Its second pass, 17 October 2026: a subfolder, and a bare name that admitted a file.
        repo = Path(__file__).resolve().parents[2]
        with tempfile.TemporaryDirectory() as d:
            Path(d, 'stage1.txt').write_text('BLIND STAGE\n')
            Path(d, 'old').mkdir()
            Path(d, 'old', 'six.txt').write_text('route\n')
            self.assertEqual(len(hook.blind_leaks('Read ' + d + '/stage1.txt.', repo)), 1)
            Path(d, 'six.txt').write_text('route\n')
            self.assertEqual(len(hook.blind_leaks('Read ' + d + '/stage1.txt. Do not read six.txt.', repo)), 2)

    def test_a_brief_that_is_not_blind_may_share_its_folder(self):
        # Its third pass: a stage-two message naming the stage-one report was refused by the first word pattern.
        repo = Path(__file__).resolve().parents[2]
        for text in ('Second stage: the route and the draft.', 'Independent alternative reports your stage one.'):
            with tempfile.TemporaryDirectory() as d:
                Path(d, 'brief.txt').write_text(text + '\n')
                Path(d, 'six.txt').write_text('the previous review\n')
                self.assertEqual(hook.blind_leaks('Read ' + d + '/brief.txt. ' + text, repo), [], text)


class MissingBriefFileTest(unittest.TestCase):
    def test_a_brief_naming_a_file_that_is_not_there_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            there = Path(tmp) / 'brief.txt'
            there.write_text('x')
            self.assertIsNone(hook.refusal(call(f'Read only {there} and answer.')))
            reason = hook.refusal(call(f'Read only {tmp}/absent.txt and {there}.'))
            self.assertIn(f'{tmp}/absent.txt', reason)
            self.assertNotIn(str(there) + ',', reason)
            # A directory, a relative path, a pattern and another agent's brief are left alone.
            self.assertIsNone(hook.refusal(call(f'Work from {tmp}/nowhere and save to research/results/x/review.txt; '
                                                f'run tools/tests/run.py; see {tmp}/*.txt')))
            self.assertIsNone(hook.refusal(call(f'Read {tmp}/absent.txt', agent='general-purpose')))

    def test_files_named_inside_the_brief_and_in_a_follow_up_must_exist(self):
        # 16 October 2026: the brief file existed, the excerpt it named did not.
        with tempfile.TemporaryDirectory() as tmp:
            brief = Path(tmp) / 'brief.md'
            brief.write_text(f'Draft: {tmp}/draft.html\nDependencies: {tmp}/deps.md\n')
            (Path(tmp) / 'draft.html').write_text('x')
            reason = hook.refusal(call(f'Read the brief at {brief} and only the files it names.'))
            self.assertIn(f'{tmp}/deps.md', reason)
            (Path(tmp) / 'deps.md').write_text('x')
            self.assertIsNone(hook.refusal(call(f'Read the brief at {brief} and only the files it names.')))
            follow = {'tool_name': 'SendMessage', 'tool_input': {'to': 'a1', 'message': f'Check {tmp}/draft2.html.'}}
            self.assertIn('draft2.html', hook.refusal(follow))
            (Path(tmp) / 'draft2.html').write_text('x')
            self.assertIsNone(hook.refusal(follow, log=Path(tmp) / 'none.tsv'))

    def test_a_draft_needs_the_sentence_listing_since_its_last_write(self):
        # 16 October 2026: a review's claim sentences dropped their qualifiers; the listing had been skipped.
        import os
        with tempfile.TemporaryDirectory() as tmp:
            tools = Path(tmp) / 'repo' / 'tools'
            tools.mkdir(parents=True)
            log = Path(tmp) / 'repo' / 'research' / 'logs' / 'claim-searches.jsonl'
            log.parent.mkdir(parents=True)
            log.write_text('')
            draft = Path(tmp) / 'draft.html'
            draft.write_text('<article id="entry-2026-10-17-x" data-kind="review"><p>x</p></article>')
            os.utime(draft, (1000, 1000))
            brief = Path(tmp) / 'brief.md'
            brief.write_text(f'Draft: {draft}\n')
            prompt = f'Read the brief at {brief} and only the files it names.'
            self.assertIn('draft_claim_sentences', hook.unread_sentences(prompt, tools) and
                          hook.SENTENCES_REASON.format(draft))
            self.assertEqual(hook.unread_sentences(prompt, tools), [str(draft)])
            log.write_text(json.dumps({'unix_s': 999, 'query': 'draft_counts entry-2026-10-17-x 3'}) + '\n')
            self.assertEqual(hook.unread_sentences(prompt, tools), [str(draft)])      # run before the last write
            log.write_text(json.dumps({'unix_s': 1001, 'query': 'draft_counts entry-2026-10-17-x 3'}) + '\n')
            self.assertEqual(hook.unread_sentences(prompt, tools), [])
            follow = f'Follow-up: {draft} is corrected.'
            os.utime(draft, (2000, 2000))
            self.assertEqual(hook.unread_sentences(follow, tools), [str(draft)])
            plain = Path(tmp) / 'page.html'
            plain.write_text('<html>no article</html>')
            self.assertEqual(hook.unread_sentences(f'See {plain}.', tools), [])

    def test_a_draft_marked_reviewed_before_its_gate_is_filled_is_refused(self):
        # 17 October 2026: three entries in a row went to their reviewer with "reviewed" in the status line and
        # "[after review]" in the gate; their briefs named draft.html beside brief.md, by its bare name.
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp) / 'rev-el'
            folder.mkdir()
            draft = folder / 'draft.html'
            brief = folder / 'brief.md'
            brief.write_text('Files in this folder: draft.html (entry draft), claim-spec.json.\n')
            prompt = f'Read {brief} and follow it.'
            early = ('<article id="entry-x" data-kind="research"><p class="entry-meta">17 October 2026 · Working '
                     'proof, reviewed; scope · Item.</p><p><strong>Verification gate.</strong> [after review]</p>')
            draft.write_text(early)
            self.assertEqual(hook.premature_reviewed(prompt), [str(draft)])
            self.assertEqual(hook.premature_reviewed(f'Follow-up on {draft}.'), [str(draft)])
            for good in (early.replace('reviewed;', 'under review;'), early.replace('reviewed;', 'unreviewed;'),
                         early.replace('[after review]', 'One medium reviewer checked the proof.')):
                with self.subTest(good=good[60:110]):
                    draft.write_text(good)
                    self.assertEqual(hook.premature_reviewed(prompt), [])

    def test_a_follow_up_claiming_an_update_its_refused_command_was_to_write_is_refused(self):
        # 16 October 2026: the command writing the spec was refused, and the follow-up said it was updated.
        with tempfile.TemporaryDirectory() as tmp:
            spec, excerpts = Path(tmp) / 'spec.json', Path(tmp) / 'deps.md'
            spec.write_text('{}')
            excerpts.write_text('x')
            written = hook.datetime.fromtimestamp(spec.stat().st_mtime)
            log = Path(tmp) / 'blocks.tsv'
            blocked = written + hook.timedelta(seconds=30)
            hook.block_log.record('bash_guard', log, blocked, what='Refused: a script replaces text', paths=[str(spec)])
            now = blocked + hook.timedelta(seconds=60)

            def send(text, when=now):
                return hook.refusal({'tool_name': 'SendMessage', 'tool_input': {'message': text}}, log=log, now=when)

            words = ('updated', 'rewritten', 'rewrote', 'now written', 'corrected', 'revised')
            for word in words:
                self.assertIn('spec.json', send(f'The spec {spec} is {word} as described.'), word)
                # The same word in a legitimate sentence passes: about a file the refused call did not name.
                self.assertIsNone(send(f'The excerpts {excerpts} are {word} as described.'), word)
            # A file named beside the updated one is not refused for it; the stale one alone is named.
            both = send(f'The spec {spec} is updated; the excerpts are at {excerpts}.')
            self.assertIn('spec.json', both)
            self.assertNotIn('deps.md', both)
            # The file read back, a refusal older than the window, no file named: all pass.
            self.assertIsNone(send(f'The spec {spec} is updated, checked on disk.'))
            self.assertIsNone(send(f'The spec {spec} is updated.', blocked + hook.timedelta(seconds=900)))
            self.assertIsNone(send('The corrected lemma now holds for every t.'))
            # An unrelated refusal, naming no file or another one, does not refuse the message.
            log.write_text('')
            hook.block_log.record('bash_guard', log, blocked, what='Refused: a pipe')
            hook.block_log.record('bash_guard', log, blocked, paths=[str(excerpts)])
            self.assertIsNone(send(f'The spec {spec} is updated.'))
            # A refusal older than the file's last write passes: the update was written after it.
            log.write_text('')
            hook.block_log.record('bash_guard', log, written - hook.timedelta(seconds=30), paths=[str(spec)])
            self.assertIsNone(send(f'The spec {spec} is updated.'))
            # The second case of 16 October 2026: the refused command named the spec as $T/spec.json, and the
            # message named it by its file name, saying "checked on disk" of another file only.
            log.write_text('')
            command = f'T={tmp} && python3 - <<EOF\nopen("$T/spec.json","w")\nEOF'
            hook.block_log.record('bash_guard', log, blocked, paths=hook.block_log.paths_in(command))
            said = (f'The corrected draft is {excerpts} (checked on disk). The updated claim spec is spec.json '
                    'beside it.')
            self.assertIn('spec.json', send(said))
            self.assertIsNone(send('The updated claim spec is spec.json beside it, checked on disk.'))
            # A file name that only resembles the refused file's does not count.
            self.assertIsNone(send('The updated claim spec is old-spec.json beside it.'))
            # A full path with the same file name in another directory is that file, not the refused one: the
            # reviewer's two cases (another notebook.html, another scratch directory's spec.json).
            other = Path(tmp) / 'other'
            other.mkdir()
            (other / 'spec.json').write_text('{}')
            self.assertIsNone(send(f'The draft is updated; {other / "spec.json"} is unchanged.'))
            # Replayed on a transcript, at each message's own time: the stale message is found, the other not.
            stamp = blocked.astimezone(hook.datetime.now().astimezone().tzinfo).isoformat()

            def sent(text):
                return json.dumps({'timestamp': stamp, 'message': {'content': [
                    {'type': 'tool_use', 'name': 'SendMessage', 'input': {'message': text}}]}})
            later = (blocked + hook.timedelta(seconds=60)).astimezone().isoformat()
            lines = [sent('ignored, sent before the time below'), 'not json',
                     sent('The updated claim spec is spec.json beside it.').replace(stamp, later),
                     sent('The plan is updated.').replace(stamp, later)]
            covered = []
            found = hook.replay(lines, log, covered)
            self.assertEqual([stale for _, _, stale in found], [[str(spec)]])
            # All three replayed messages have the refusal within their window, the first at the refusal's time.
            self.assertEqual(len(covered), 3)


if __name__ == '__main__':
    unittest.main()
