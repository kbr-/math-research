import json
import subprocess
import sys
import unittest
from pathlib import Path

HOOK = Path(__file__).resolve().parents[1] / "hooks" / "guard-full-output.py"


def run(command, tool="Bash"):
    payload = json.dumps({"tool_name": tool, "tool_input": {"command": command}})
    return subprocess.run([sys.executable, str(HOOK)], input=payload, text=True,
                          capture_output=True)


class GuardFullOutputTest(unittest.TestCase):
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
            "FOO=1 python3 -u tools/resume.py | head",
            "(python3 tools/resume.py) | head",
            "bash compute.sh start t1 | tail",
            "./compute.sh run t1 -- python3 x.py | tail -5",
            "./compute.sh run t1 --threads 1 -- ./kernel 3 | grep n=",
            "./compute.sh --session t1 --threads 1 python3 x.py | head",
            "for a in 1 2; do ./compute.sh run t1 -- ./k $a 2>&1 | grep x; done",
            "./compute.sh run t1 -- ./k > out.txt",
        ]:
            with self.subTest(command=command):
                result = run(command)
                self.assertEqual(result.returncode, 2)
                self.assertIn("read its output in full", result.stderr)

    def test_allows_bare_calls_and_other_commands(self):
        for command in [
            "python3 tools/resume.py",
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
        ]:
            with self.subTest(command=command):
                self.assertEqual(run(command).returncode, 0)

    def test_ignores_other_tools(self):
        self.assertEqual(run("python3 tools/resume.py | head", tool="Read").returncode, 0)


if __name__ == "__main__":
    unittest.main()
