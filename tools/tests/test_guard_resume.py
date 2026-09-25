import json
import subprocess
import sys
import unittest
from pathlib import Path

HOOK = Path(__file__).resolve().parents[1] / "hooks" / "guard-resume.py"


def run(command, tool="Bash"):
    payload = json.dumps({"tool_name": tool, "tool_input": {"command": command}})
    return subprocess.run([sys.executable, str(HOOK)], input=payload, text=True,
                          capture_output=True)


class GuardResumeTest(unittest.TestCase):
    def test_blocks_filters_and_redirections(self):
        for command in [
            "python3 tools/resume.py 2>&1 | head -40",
            "cd /repo && python3 tools/resume.py --read ab --part 1 | sed -n '40,400p'",
            "python3 tools/resume.py --read ab --part 4 | head -120; git log",
            "python3 tools/resume.py | tail -5",
            "python3 tools/resume.py > out.txt",
        ]:
            with self.subTest(command=command):
                result = run(command)
                self.assertEqual(result.returncode, 2)
                self.assertIn("resume.py bare", result.stderr)

    def test_allows_bare_calls_and_other_commands(self):
        for command in [
            "python3 tools/resume.py",
            "cd /repo && python3 tools/resume.py --read ab --part 2",
            "python3 tools/resume.py 2>&1",
            "python3 tools/resume.py --read ab --part 3; git log | head",
            "git log --oneline | head -3",
            "python3 tools/resume.py || echo failed",
        ]:
            with self.subTest(command=command):
                self.assertEqual(run(command).returncode, 0)

    def test_ignores_other_tools(self):
        self.assertEqual(run("python3 tools/resume.py | head", tool="Read").returncode, 0)


if __name__ == "__main__":
    unittest.main()
