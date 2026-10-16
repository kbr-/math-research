import contextlib
import importlib.util
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import types
import unittest
import unittest.mock
from pathlib import Path

HOOK = Path(__file__).resolve().parents[1] / "hooks" / "bash_guard.py"
sys.path.insert(0, str(HOOK.parent))   # the hook imports its neighbours by name, as a program started there does
spec = importlib.util.spec_from_file_location("bash_guard", HOOK)
guard = importlib.util.module_from_spec(spec)
spec.loader.exec_module(guard)


def run(command, tool="Bash", background=False):
    """The hook's status and message for a call, from its main() in this process: starting the hook as a
    program for each of some 140 commands took most of this file's time."""
    payload = json.dumps({"tool_name": tool, "tool_input": {"command": command, "run_in_background": background}})
    said = io.StringIO()
    with unittest.mock.patch("sys.stdin", io.StringIO(payload)), contextlib.redirect_stderr(said):
        status = guard.main()
    return types.SimpleNamespace(returncode=status, stderr=said.getvalue())


class CannotFailTestsTest(unittest.TestCase):
    def test_a_commit_adding_a_test_that_cannot_fail_is_refused_only_in_a_session_of_this_checkout(self):
        flagged = types.SimpleNamespace(returncode=1, stdout='CANNOT FAIL tools/tests/test_x.py::X.test_y: it passes\n'
                                        '1 tests checked, 1 flagged.\n')
        clean = types.SimpleNamespace(returncode=0, stdout='ok tools/tests/test_x.py::X.test_y\n')
        project = str(HOOK.parents[2])
        with unittest.mock.patch.dict(os.environ, {'CLAUDE_PROJECT_DIR': project}):
            reason = guard.cannot_fail_tests(run=lambda *a, **k: flagged)
            self.assertIn('cannot fail', reason)
            self.assertIn('test_x.py::X.test_y', reason)
            self.assertIsNone(guard.cannot_fail_tests(run=lambda *a, **k: clean))
            # A crash or a timeout lets the commit through, with a notice saying it was not checked.
            said = io.StringIO()
            crashed = types.SimpleNamespace(returncode=2, stdout='', stderr='Traceback: KeyError')
            self.assertIsNone(guard.cannot_fail_tests(run=lambda *a, **k: crashed, notice=said))
            self.assertIn('failed without a verdict (exit status 2): Traceback: KeyError', said.getvalue())

            def timeout(*a, **k):
                raise subprocess.TimeoutExpired('x', 60)
            self.assertIsNone(guard.cannot_fail_tests(run=timeout, notice=said))
            self.assertIn('timed out after 60 s', said.getvalue())
        with unittest.mock.patch.dict(os.environ, {}, clear=True):
            self.assertIsNone(guard.cannot_fail_tests(run=lambda *a, **k: flagged))


class BashGuardTest(unittest.TestCase):
    def test_the_hook_started_as_a_program_reads_its_call_and_refuses_with_status_two(self):
        payload = json.dumps({"tool_name": "Bash", "tool_input": {"command": "python3 tools/resume.py | tail -5"}})
        with tempfile.TemporaryDirectory() as home:
            done = subprocess.run([sys.executable, str(HOOK)], input=payload, text=True, capture_output=True,
                                  env={**os.environ, "HOME": home, "CLAUDE_PROJECT_DIR": home})
        self.assertEqual(done.returncode, 2)
        self.assertIn("Run this command bare", done.stderr)
        self.assertEqual(run("python3 tools/resume.py | tail -5").stderr, done.stderr)

    def test_blocks_filters_and_redirections(self):
        for command in [
            "python3 tools/resume.py 2>&1 | head -40",
            "cd /repo && python3 tools/resume.py --read ab --part 1 | sed -n '40,400p'",
            "python3 tools/resume.py --read ab --part 4 | head -120; git log",
            "python3 tools/resume.py | tail -5",
            "python3 tools/resume.py > out.txt",
            "./compute.sh start t1 --model 'M, high' | tail -20",
            "cd /repo && ./compute.sh start t1 --model M 2>&1 | grep -i warn",
            "./compute.sh start t1 > start.txt",
            "./tools/finish-turn.py t1 2>&1 | tail -15",
            "./tools/finish-turn.py t1 --next t2 | head",
            "./tools/check_records.py --diff 2>&1 | tail -2 && git commit -q -m x",
            "python3 tools/check-claims.py 2>&1 | tail -1 && tools/ff-base.sh",
            "python3 tools/claim_rebase.py --spec s.json 2>&1 | tail -2 && git rebase --continue",
            "FOO=1 python3 -u tools/resume.py | head",
            "(python3 tools/resume.py) | head",
            "bash compute.sh start t1 | tail",
            "./compute.sh run t1 -- python3 x.py | tail -5",
            "./compute.sh run t1 --threads 1 -- ./kernel 3 | grep n=",
            "./compute.sh --session t1 --threads 1 python3 x.py | head",
            "for a in 1 2; do ./compute.sh run t1 -- ./k $a 2>&1 | grep x; done",
            "./compute.sh run t1 -- ./k > out.txt",
            "python3 tools/search-claims.py extension variables degree | head -6",
            "python3 tools/search-claims.py weighted retraction 2>&1 | grep -E '^[a-z]+:' | head",
            "python3 tools/lead_queue.py history n.html a:s1 --status | sed -n '1,4p'",
            "python3 tools/notebook-append.py e.html --next n.html > out.txt 2>&1",
            "python3 tools/notebook-append.py e.html --next n.html | head -3",
        ]:
            with self.subTest(command=command):
                result = run(command)
                self.assertEqual(result.returncode, 2)
                self.assertIn("read its output in full", result.stderr)

    def test_allows_bare_calls_and_other_commands(self):
        for command in [
            "python3 tools/resume.py",
            "python3 tools/search-claims.py -n 20 extension variables degree",
            "python3 tools/lead_queue.py history n.html a:s1 --status",
            "python3 tools/notebook-append.py e.html --next n.html --stand-unchanged 'No change.'",
            "python3 tools/notebook-append.py --help | sed -n '1,30p'",
            "python3 tools/lead_queue.py pending n.html | head",
            "python3 tools/search-claims.py --show lem:x | head -40",
            "python3 tools/search-claims.py --help | grep limit",
            "grep -n similar tools/search-claims.py | head",
            "cd /repo && python3 tools/resume.py --read ab --part 2",
            "python3 tools/resume.py 2>&1",
            "python3 tools/resume.py --read ab --part 3; git log | head",
            "git log --oneline | head -3",
            "python3 tools/resume.py || echo failed",
            "./compute.sh start t1 --model 'M, high'",
            "./compute.sh start t1 --model M 2>&1",
            "./compute.sh run t1 -- python3 x.py",
            "./compute.sh --status | head",
            "./compute.sh phase t1 reading",
            "./tools/finish-turn.py t1",
            "./tools/finish-turn.py t1 && git status | head",
            "grep -n AGENTS tools/resume.py | head -30",
            "cd /repo && rg -n x tools/finish-turn.py | head",
            "sed -n 1,40p compute.sh | grep start",
            "echo '{\"command\":\"python3 tools/resume.py\"}' | python3 hook.py pre",
            "git log -- tools/resume.py | head",
            "python3 tools/test_resume.py | head",
            "./compute.sh --timeout 30 sh -c 'docker ps | head -3 > names.txt'",
            "./compute.sh start t1 --model \"a | b > c\"",
        ]:
            with self.subTest(command=command):
                self.assertEqual(run(command).returncode, 0)

    def test_ignores_other_tools(self):
        self.assertEqual(run("python3 tools/resume.py | head", tool="Read").returncode, 0)

    def test_unchained_heredoc_is_refused(self):
        bad = "python3 - f <<'EOF'\nimport sys\nassert False\nEOF\npython3 tools/notebook-append.py x"
        self.assertEqual(run(bad).returncode, 2)
        self.assertIn("heredoc", run(bad).stderr)
        for good in ["python3 - f <<'EOF' && python3 tools/notebook-append.py x\nprint(1)\nEOF",
                     "python3 - <<'EOF'\nprint(1)\nEOF",
                     "set -e\npython3 - <<'EOF'\nprint(1)\nEOF\ngit status",
                     "cat > f <<'EOF'\nx\nEOF"]:
            self.assertEqual(run(good).returncode, 0, good)

    def test_a_heredoc_replace_helper_is_refused(self):
        for helper in ("def sub(old, new):\n    pass", "def sub(path, old, new, count=1):\n    pass",
                       "pat = r'\\s+'.join(map(re.escape, old.split()))"):
            command = f"python3 - <<'EOF'\n{helper}\nEOF"
            with self.subTest(helper=helper):
                result = run(command)
                self.assertEqual(result.returncode, 2)
                self.assertIn("tools/replace_text.py FILE OLD_FILE NEW_FILE", result.stderr)
        for good in ("python3 - <<'EOF'\ns = s.replace(old, new)\nEOF", "grep -n 'def sub(old, new)' x.py",
                     "python3 - <<'EOF'\ndef subtotal(older, newer):\n    pass\nEOF"):
            with self.subTest(good=good):
                self.assertEqual(run(good).returncode, 0)

    def test_sed_in_place_over_a_range_or_to_a_next_line_of_a_source_file_is_refused(self):
        for command, how in (("sed -i '12,15d' tools/x.py", "a range of lines (12,15d)"),
                             ("sed -i '0,/^import json$/s//import json\\nimport os/' probe.py", "a range of lines"),
                             ("cd repo && sed -i -e '/^def a/,/^def b/d' src/a.ts", "a range of lines"),
                             ("sed -i '5,+2s/a/b/' conf.yaml", "a range of lines"),
                             ("sed -i '3,$d' run.sh; echo done", "a range of lines"),
                             ("sed -i '/^    x = 1$/{n;d}' tools/x.py", "a step to the next line"),
                             ("sed -i.bak '/a/{N;s/a\\nb/c/}' x.py", "a step to the next line"),
                             ("sed --in-place 's/a/b/; 2,3d' x.py", "a range of lines (2,3d)"),
                             ("sed -i 12,15d tools/x.py", "a range of lines (12,15d)"),
                             ("sed -i 's/a/b/' notes.txt\nsed -i '1,2d' x.py", "a range of lines (1,2d)"),
                             ("LC_ALL=C sed -i '1,2d' x.py", "a range of lines (1,2d)")):
            with self.subTest(command=command):
                done = run(command)
                self.assertEqual(done.returncode, 2, done.stderr)
                self.assertIn(f"sed -i edits a source file over {how}", done.stderr)
                self.assertIn("Make the edit with the Edit tool", done.stderr)
        # A substitution or a pattern address names its lines by their text; prose has its own tool; sed that edits
        # nothing in place, or is only spoken of, is no edit.
        for command in ("sed -i 's/old/new/' tools/x.py", "sed -i '/^import sys$/d' x.py", "sed -i '12,15d' notes.txt",
                        "sed -n '12,15p' tools/x.py", "sed '12,15d' tools/x.py > out.py", "sed -i 's/a,b/c/' x.py",
                        "sed -i 's/n/N/' x.py", "git commit -m \"sed -i '1,2d' x.py was wrong\"",
                        "sed -i '12,15d' data/a.tsv research/notes/b.txt", "grep -n 'sed -i 1,2d x.py' log",
                        "python3 -c \"x = 'a; sed -i 1,2d x.py'; print(x)\"", "echo sed -i 1,2d x.py",
                        "cat > notes.txt <<'EOF'\nsed -i '1,2d' x.py\nEOF", "sed -i 's/a/b/' notes.txt\npython3 run.py",
                        "sed -i 's/a/b/' x.py # 1,2d"):
            with self.subTest(command=command):
                self.assertEqual(run(command).returncode, 0, run(command).stderr)

    def test_sed_in_place_at_a_line_named_by_its_number_in_a_source_file_is_refused(self):
        for command, part in (("sed -i '129s/old/new/' tools/x.py", "129s/old/new/"), ("sed -i 12d x.py", "12d"),
                              ("sed -i '$d' run.sh", "$d"), ("sed -i '3{s/a/b/}' x.py", "3{s/a/b/}"),
                              ("sed -i '7!d' conf.toml", "7!d"), ("sed -i -e 's/a/b/' -e '5d' x.py", "5d"),
                              ("sed -i '5a\\    return x' x.py", "5a"), ("sed -i \"${line}d\" x.py", "${line}d"),
                              ("sed -i 's/a/b/; 40s/c/d/' x.py", "40s/c/d/")):
            with self.subTest(command=command):
                done = run(command)
                self.assertEqual(done.returncode, 2, done.stderr)
                self.assertIn(f"sed -i edits a source file at a line named by its number ({part}", done.stderr)
        # A number inside a substitution or a pattern is text, and prose has its own tool.
        for command in ("sed -i 's/1a/2b/' x.py", "sed -i '/^12d$/d' x.py", "sed -i '129s/old/new/' notes.txt",
                        "sed -n '129p' x.py", "sed -i 's/^v = 3$/v = 4/' x.py"):
            with self.subTest(command=command):
                self.assertEqual(run(command).returncode, 0, run(command).stderr)

    def test_sed_in_place_on_a_markdown_file_is_refused_whatever_its_script(self):
        for command, name in (("sed -i 's/^Status: .*/Status: done./' notes/a/PLAN.md", "notes/a/PLAN.md"),
                              ("sed -i '12,15d' notes.md", "notes.md"), ("sed -i -e '/^x$/d' x.py AGENTS.md", "AGENTS.md"),
                              ("cd repo && sed -i 's/a/b/' README.md && git add README.md", "README.md")):
            with self.subTest(command=command):
                done = run(command)
                self.assertEqual(done.returncode, 2, done.stderr)
                self.assertIn(f"sed -i edits wrapped prose ({name})", done.stderr)
                self.assertIn("tools/replace_text.py FILE OLD_FILE NEW_FILE", done.stderr)
        # Reading one, or editing a file that only has md in its name, is no such edit.
        for command in ("sed -n '1,5p' notes.md", "sed 's/a/b/' notes.md > out.md", "sed -i 's/a/b/' cmd_tool.py",
                        "sed -i 's/a/b/' notes.mdx.txt"):
            with self.subTest(command=command):
                self.assertEqual(run(command).returncode, 0, run(command).stderr)

    def test_sed_substituting_in_a_page_is_refused(self):
        # A notebook or an entry draft is prose: a substitution that misses says nothing.
        for command, name in (("sed -i 's|old words|new words|' $D/entry.html", "$D/entry.html"),
                              ("sed -i -e 's#a#b#' -e 's#c#d#' notebook.html", "notebook.html"),
                              ("D=x && sed -i 's/a/b/' x/entry.html && grep -c b x/entry.html", "x/entry.html")):
            with self.subTest(command=command):
                done = run(command)
                self.assertEqual(done.returncode, 2, done.stderr)
                self.assertIn(f"sed -i replaces prose in a page ({name})", done.stderr)
        # Reading a page, or substituting into a copy, is no such edit.
        for command in ("sed -n '1,5p' notebook.html", "sed 's/a/b/' notebook.html > out.html"):
            with self.subTest(command=command):
                self.assertEqual(run(command).returncode, 0, run(command).stderr)

    def test_sed_in_place_with_an_unescaped_ampersand_in_a_replacement_is_refused(self):
        # (A page is refused whatever its substitution, by the test above; these are text files.)
        for command in ("sed -i 's#a b#x &lt; y#' entry.txt", "sed -i -e 's/p/q/' -e 's|r|M&amp;N|' a.txt"):
            with self.subTest(command=command):
                done = run(command)
                self.assertEqual(done.returncode, 2, done.stderr)
                self.assertIn("unescaped & in a replacement", done.stderr)
        # An escaped ampersand, one only in the pattern, and sed without -i are fine.
        for command in ("sed -i 's#a b#x \\&lt; y#' entry.txt", "sed -i 's/&lt;/</' entry.txt",
                        "sed 's/a/&b/' entry.html"):
            with self.subTest(command=command):
                self.assertEqual(run(command).returncode, 0, run(command).stderr)

    def test_rm_of_a_framework_tool_is_refused(self):
        for command in ("rm -rf /tmp/x tools/browser_get.cjs", "cd repo && rm tools/hooks/x.py",
                        "rm -f /home/u/repo/tools/a.py; ls"):
            with self.subTest(command=command):
                done = run(command)
                self.assertEqual(done.returncode, 2, done.stderr)
                self.assertIn("a framework tool", done.stderr)
        # Scratch, results and git rm are fine.
        for command in ("rm -rf /home/u/.claude/jobs/x/tmp/bget", "rm research/results/a/old.json",
                        "git rm tools/old.py"):
            with self.subTest(command=command):
                self.assertEqual(run(command).returncode, 0, run(command).stderr)

    def test_an_inline_script_replacing_text_in_a_file_is_refused(self):
        heredoc = "python3 - <<'EOF'\nfrom pathlib import Path\n{}\nEOF"
        for script in (
                "python3 -c \"from pathlib import Path; p=Path('x.md'); p.write_text(p.read_text().replace('a','b'))\"",
                heredoc.format("p = Path('x.md'); s = p.read_text(); p.write_text(s.replace('a', 'b'))"),
                heredoc.format("import re\np = Path('x.md'); p.write_text(re.sub('a', 'b', p.read_text()))"),
                "python3 -I - <<'EOF' && echo done\ns = open('x.md').read().replace('a', 'b')\n"
                "with open('x.md', 'w') as f:\n    print(s, file=f)\nEOF",
                heredoc.format("p = Path('x.bin'); p.write_bytes(p.read_bytes().replace(b'a', b'b'))")):
            with self.subTest(script=script):
                result = run(script)
                self.assertEqual(result.returncode, 2)
                self.assertIn("a script replaces text in a file", result.stderr)
                self.assertIn("tools/replace_text.py FILE OLD_FILE NEW_FILE", result.stderr)
        for good in (
                # Reading and printing, or writing what wasn't replaced, is no edit.
                "python3 -c \"print(open('x.md').read().replace('a', 'b'))\"",
                "python3 -c \"import sys; sys.stdout.write(open('x.md').read().replace('a', 'b'))\"",
                heredoc.format("Path('out.json').write_text(json.dumps(rows))"),
                # Words in a commit message or a shell pipeline are no script.
                "git commit -F - <<'EOF'\nUse .replace( and write_text( no more\nEOF",
                "sed -n 1,5p x.md | grep -c 're.sub(' && echo '.write_text('"):
            with self.subTest(good=good):
                self.assertEqual(run(good).returncode, 0, run(good).stderr)

    def test_a_scratch_script_replacing_text_in_a_file_is_refused_when_run_by_path(self):
        # 16 October 2026: replace scripts in the scratchpad, run by path, swallowed three labels of an entry.
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            edit = Path(tmp) / 'fix.py'
            edit.write_text("import sys\np = sys.argv[1]; t = open(p).read()\nt = t.replace('a', 'b')\n"
                            "open(p, 'w').write(t)\n")
            reader = Path(tmp) / 'count.py'
            reader.write_text("import sys\nprint(open(sys.argv[1]).read().replace('a', 'b').count('b'))\n")
            writer = Path(tmp) / 'make.py'
            writer.write_text("open('out.json', 'w').write('[]')\n")
            result = run(f"python3 {edit} research/x.html")
            self.assertEqual(result.returncode, 2)
            self.assertIn("a script replaces text in a file", result.stderr)
            for good in (f"python3 {reader} x.md", f"python3 {writer}", "python3 tools/replace_text.py a b c",
                         f"python3 {tmp}/absent.py x"):
                with self.subTest(good=good):
                    self.assertEqual(run(good).returncode, 0, run(good).stderr)

    def test_long_compute_runs_go_to_the_background(self):
        long_runs = ["./compute.sh run t1 --threads 1 --timeout 600 --expect 300 -- M2 --script x.m2",
                     "./compute.sh run t1 --expect 120 -- ./k",
                     "./compute.sh --session t1 --timeout 900 python3 x.py",
                     "cd /repo && ./compute.sh run t1 --timeout=1500 -- ./k",
                     "./compute.sh --threads 1 --timeout 900 python3 x.py --expect 1",
                     # Allowed over a minute with no word that it will be short: the timeout is how long it may hold the turn.
                     "./compute.sh --threads 14 --timeout 175 --category network_tool -- python3 review.py",
                     "./compute.sh --threads 1 --timeout 61 python3 tools/tests/run.py"]
        for command in long_runs:
            with self.subTest(command=command):
                self.assertEqual(run(command).returncode, 2)
                self.assertIn("background", run(command).stderr)
                self.assertEqual(run(command, background=True).returncode, 0)
        for command in ["./compute.sh run t1 --threads 1 --timeout 120 --expect 5 -- ./k",
                        "./compute.sh run t1 -- ./k --timeout 9999",        # the workload's own option
                        "./compute.sh phase t1 coding",
                        "./compute.sh --threads 1 --timeout 60 python3 tools/tests/run.py",
                        "./compute.sh --threads 14 --timeout 175 --expect 40 --category network_tool -- python3 review.py",
                        "./compute.sh --status"]:
            with self.subTest(command=command):
                self.assertEqual(run(command).returncode, 0)

    def test_clones_and_pulls_go_to_the_background(self):
        downloads = ["git clone -q git@gitlab.com:group/repo.git repo",
                     "cd ~/dev && [ -d shared ] || git clone -q git@gitlab.com:g/shared.git shared",
                     "for r in a b; do git -C ~/dev clone git@x:g/$r.git; done",
                     "glab repo clone group/repo",
                     "docker pull -q prom/prometheus:v3.5.0 && echo ok",
                     "docker image pull alpine"]
        for command in downloads:
            with self.subTest(command=command):
                self.assertEqual(run(command).returncode, 2)
                self.assertIn("background", run(command).stderr)
                self.assertEqual(run(command, background=True).returncode, 0)
        for command in ['pgrep -af "git clone"', "git log --grep clone", "docker images",
                        "echo docker pull later", "git fetch -q origin", "git clone --help",
                        "docker pull -h", "git clone --help && git clone -h"]:
            with self.subTest(command=command):
                self.assertEqual(run(command).returncode, 0)


    def test_workloads_outside_compute_sh_are_refused(self):
        for command in ["pytest -q tests/test_x.py",
                        "cd /repo && .venv/bin/python -m pytest -q tests",
                        "python3 -m unittest tools/tests/test_x.py",
                        "uv run --frozen pytest tests",
                        "APP_DB=x timeout 60 .venv/bin/pytest -x",
                        "scripts/local/api-tests.sh -k relay",
                        "bash notes/some-work/suite_tips.sh",
                        "python3 tools/tests/run.py",
                        "python3 tools/tests/test_browser_get.py 2>&1 | tail -1",
                        "python3 -I /tmp/claude-1/p/scratchpad/probe.py --out x",
                        "git status; python3 /tmp/s/scratchpad/m.py 2>&1 | tail",
                        "sh /tmp/s/scratchpad/loop.sh",
                        "cat cases.txt | python3 /tmp/s/scratchpad/m.py"]:
            with self.subTest(command=command):
                result = run(command)
                self.assertEqual(result.returncode, 2)
                self.assertIn("compute.sh", result.stderr)
        for command in ["./compute.sh --threads 4 env A=1 .venv/bin/python -m pytest -q tests",
                        "~/dev/noemesis/compute.sh python3 /tmp/s/scratchpad/m.py",
                        "./compute.sh --threads 1 --timeout 60 python3 tools/tests/run.py",
                        "docker exec db pytest -q",
                        "GIT_SEQUENCE_EDITOR=\"python3 /tmp/s/scratchpad/todo.py\" git rebase -i HEAD~3",
                        "python3 tools/claim-index.py render",
                        "python3 -c 'import pytest; print(pytest.__version__)'",
                        "grep -n pytest .gitlab-ci.yml",
                        "cat /tmp/s/scratchpad/probe.py",
                        "S=/tmp/s/scratchpad/probe.py; ./compute.sh python3 $S",
                        "git grep -n -E 'python3 -m (unittest|pytest)' -- '*.md' | head",
                        "cat > notes.md <<'EOF' && echo done\npytest -q tests\nEOF"]:
            with self.subTest(command=command):
                self.assertEqual(run(command).returncode, 0)


class StaleBranchTest(unittest.TestCase):
    """A clone whose remote-tracking refs were last updated in January, its `other` tracking origin's."""

    def git(self, repo, *args, date=None):
        env = {**os.environ, "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t",
               "GIT_COMMITTER_EMAIL": "t@t", **({"GIT_COMMITTER_DATE": date} if date else {})}
        subprocess.run(["git", "-C", str(repo), *args], check=True, capture_output=True, env=env)

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp)
        self.origin, self.seed, self.work = self.tmp / "origin.git", self.tmp / "seed", self.tmp / "work"
        self.git(self.tmp, "init", "-q", "--bare", "-b", "main", str(self.origin))
        self.git(self.tmp, "init", "-q", "-b", "main", str(self.seed))
        (self.seed / "f").write_text("1\n")
        self.git(self.seed, "add", "f")
        self.git(self.seed, "commit", "-qm", "one")
        self.git(self.seed, "push", "-q", str(self.origin), "main", "main:other")
        self.git(self.tmp, "clone", "-q", str(self.origin), str(self.work))
        self.git(self.work, "branch", "-q", "--track", "other", "origin/other")
        # A fetch in January moved origin/other; FETCH_HEAD dates from then too.
        self.git(self.seed, "commit", "-q", "--allow-empty", "-m", "january")
        self.git(self.seed, "push", "-q", str(self.origin), "main:other")
        self.git(self.work, "fetch", "-q", "origin", "other:other", date="2026-01-01T00:00:00")
        january = time.mktime((2026, 1, 1, 0, 0, 0, 0, 0, -1))
        os.utime(self.work / ".git" / "FETCH_HEAD", (january, january))

    def stale(self, command, cwd=None):
        return guard.stale_branch(command, str(cwd or self.work), time.time())

    def test_refuses_reading_a_branch_whose_upstream_is_stale(self):
        for command in ("git show other:f", "git diff main..other -- f", "git log origin/other~1",
                        "git -c core.pager=cat merge-base main origin/other", "git rev-parse other^{commit}",
                        "GIT_PAGER=cat git log other", "timeout 5 git log other", "env time git log other"):
            with self.subTest(command=command):
                reason = self.stale(command)
                self.assertIn("origin/other", reason)
                self.assertRegex(reason, r"last fetched or pushed \d{6} minutes ago")
                self.assertIn(f"git -C {self.work} fetch origin other", reason)
        self.assertIn("`other` follows origin/other, last fetched", self.stale("git show other:f"))
        self.assertIn("fetch origin other:other also fast-forwards the local other", self.stale("git show other:f"))
        self.assertIn("`origin/other` is last fetched", self.stale("git log origin/other"))
        # Reading origin/HEAD reads its target.
        self.git(self.work, "remote", "set-head", "origin", "other")
        self.assertIn("`origin/HEAD` follows origin/other, last fetched", self.stale("git log origin/HEAD"))
        self.git(self.work, "branch", "-q", "--track", "unfetched", "origin/main")
        self.assertIn("`unfetched` follows origin/main, with no fetch or push recorded here",
                      self.stale("git log unfetched"))
        self.assertIn("`origin/other` is", self.stale(f"cd {self.work} && git log origin/other", cwd=self.tmp))
        self.assertIn("`origin/other` is", self.stale(f"git -C {self.work} log origin/other", cwd=self.tmp))
        self.assertEqual(run(f"git -C {self.work} show other:f").returncode, 2)

    def test_allows_the_current_branch_paths_local_branches_and_a_fetch_first(self):
        self.git(self.work, "branch", "local-only")
        for command in ("git log main", "git log -- other", "git log -n 5", "git show HEAD:f", "git log local-only",
                        "git fetch && git log other", "timeout 60 git fetch -q origin other && git log other",
                        "env GIT_TERMINAL_PROMPT=0 nohup git fetch origin; git log other",
                        "git fetch -q origin && git log other", "git fetch --all && git diff origin/other",
                        "git status && git branch -a", "echo git log other"):
            with self.subTest(command=command):
                self.assertIsNone(self.stale(command))

    def test_a_push_counts_as_fresh(self):
        self.git(self.work, "switch", "-q", "other")
        self.git(self.work, "commit", "-q", "--allow-empty", "-m", "pushed now")
        self.git(self.work, "push", "-q", "origin", "other")
        self.git(self.work, "switch", "-q", "-c", "pushed")
        self.git(self.work, "push", "-q", "-u", "origin", "pushed")
        self.git(self.work, "switch", "-q", "main")
        for command in ("git log other", "git log pushed"):
            with self.subTest(command=command):
                self.assertIsNone(self.stale(command))

    def test_a_fetch_that_found_nothing_counts_for_its_own_branch_and_remote_only(self):
        mirror = self.tmp / "mirror.git"
        self.git(self.tmp, "clone", "-q", "--bare", str(self.origin), str(mirror))
        self.git(self.work, "remote", "add", "mirror", str(mirror))
        for fetch in (("origin", "main"), ("mirror", "other")):
            self.git(self.work, "fetch", "-q", *fetch)
            self.assertIn("`other` follows origin/other", self.stale("git log other"))
        self.assertIn("`other` follows origin/other", self.stale("git fetch mirror && git log other"))
        self.git(self.work, "fetch", "-q", "origin")
        self.assertIsNone(self.stale("git log other"))

    def test_a_fetch_by_address_counts_for_the_remote_whose_tracking_refs_it_writes(self):
        all_to = lambda remote: f"git fetch {self.origin} '+refs/heads/*:refs/remotes/{remote}/*'"
        self.assertIsNone(self.stale(f"{all_to('origin')} && git log origin/other"))
        self.assertIsNone(self.stale(f"git fetch -q {self.origin} other:refs/remotes/origin/other; git log other"))
        # An address alone updates no tracking ref, and another remote's refs are not origin's.
        self.assertIn("`origin/other` is last fetched", self.stale(f"git fetch {self.origin} && git log origin/other"))
        self.assertIn("`origin/other` is last fetched", self.stale(f"{all_to('mirror')} && git log origin/other"))
        # Made for real, the fetch is then seen by a later command too.
        subprocess.run(all_to("origin"), shell=True, cwd=self.work, check=True, capture_output=True)
        self.assertIsNone(self.stale("git log origin/other"))

    def test_refuses_a_local_branch_behind_its_fetched_upstream(self):
        (self.seed / "f").write_text("2\n")
        self.git(self.seed, "commit", "-qam", "two")
        self.git(self.seed, "push", "-q", str(self.origin), "main:other")
        self.git(self.work, "fetch", "-q", "origin", "other")
        self.assertIn("the local `other` is behind or apart from origin/other", self.stale("git log other"))
        self.assertIsNone(self.stale("git log origin/other"))
        self.git(self.work, "fetch", "-q", "origin", "other:other")
        self.assertIsNone(self.stale("git log other"))




class StagingSilencedTest(unittest.TestCase):
    def test_git_add_and_commit_keep_their_errors(self):
        for command in ('git add a b 2>/dev/null && git commit -m x',
                        'git add a; git commit -q -m x >/dev/null 2>&1',
                        'git -C repo add a &>/dev/null'):
            with self.subTest(command=command):
                self.assertIn('errors shown', guard.staging_silenced(command))
        for command in ('git add a b && git commit -q -m x',
                        'git add a; ls missing 2>/dev/null',
                        'GIT_EDITOR=true git rebase --continue >/dev/null 2>&1',
                        'git status --short 2>/dev/null',
                        "cat > notes.txt <<'EOF'\ngit add a 2>/dev/null\nEOF"):
            with self.subTest(command=command):
                self.assertIsNone(guard.staging_silenced(command))


if __name__ == '__main__':
    unittest.main()
