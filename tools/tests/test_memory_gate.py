import importlib.util
import unittest
from pathlib import Path

TOOLS = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('memory_gate', TOOLS / 'hooks' / 'memory-gate.py')
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)
MEM = '/home/u/.claude/projects/-home-u-dev-math/memory/'


def call(tool, **tool_input):
    return gate.refusal({'tool_name': tool, 'tool_input': tool_input})


class MemoryGateTest(unittest.TestCase):
    def test_writes_to_agent_memory_are_refused(self):
        self.assertIn('AGENTS.md', call('Write', file_path=MEM + 'note.md', content='x'))
        self.assertIsNotNone(call('Edit', file_path=MEM + 'MEMORY.md', old_string='a', new_string='b'))
        self.assertIsNotNone(call('Bash', command=f"printf x >> {MEM}MEMORY.md"))
        self.assertIsNotNone(call('Bash', command=f"python3 - <<'EOF'\nopen('{MEM}n.md','w')\nEOF"))
        self.assertIsNotNone(call('Bash', command=f"cat {MEM}a.md > {MEM}b.md"))

    def test_reading_deleting_and_other_paths_pass(self):
        self.assertIsNone(call('Bash', command=f"ls {MEM}"))
        self.assertIsNone(call('Bash', command=f"rm {MEM}note.md"))
        self.assertIsNone(call('Read', file_path=MEM + 'MEMORY.md'))
        self.assertIsNone(call('Write', file_path='/home/u/dev/math/AGENTS.md', content='x'))
        self.assertIsNone(call('Bash', command='git commit -m "memory controls"'))

    def test_edits_of_claude_md_are_refused(self):
        # 17 October 2026: rules were added to CLAUDE.md, which the user directed to AGENTS.md.
        self.assertIn('AGENTS.md', call('Edit', file_path='/w/CLAUDE.md', old_string='a', new_string='b'))
        self.assertIsNotNone(call('Write', file_path='CLAUDE.md', content='x'))
        self.assertIsNotNone(call('Bash', command='printf x >> CLAUDE.md'))
        self.assertIsNotNone(call('Bash', command='python3 tools/rewrap_md.py CLAUDE.md'))
        self.assertIsNotNone(call('Bash', command="sed -i 's/a/b/' CLAUDE.md"))

    def test_reading_claude_md_and_commits_naming_it_pass(self):
        self.assertIsNone(call('Read', file_path='/w/CLAUDE.md'))
        self.assertIsNone(call('Bash', command='git add CLAUDE.md AGENTS.md'))
        self.assertIsNone(call('Bash', command='grep -n rule CLAUDE.md'))
        self.assertIsNone(call('Edit', file_path='/w/AGENTS.md', old_string='a', new_string='b'))
        # the false refusal of the first version: a commit message naming sed -i and rewrap_md.py
        self.assertIsNone(call('Bash', command="printf 'refuses sed -i, rewrap_md.py edits\\n' > $T/m.md && "
                                               "python3 tools/rewrap_md.py $T/m.md && git add AGENTS.md CLAUDE.md && "
                                               "git commit -q -F $T/m.md"))
        # a heredoc whose body mentions CLAUDE.md, the marker line writing elsewhere
        self.assertIsNone(call('Bash', command="python3 - $F <<'EOF' && python3 tools/replace_text.py $F a b\n"
                                               "print('CLAUDE.md')\nEOF"))
        # but a write on the marker line itself is still seen
        self.assertIsNotNone(call('Bash', command="python3 - <<'EOF' && python3 tools/rewrap_md.py CLAUDE.md\n"
                                                  "print(1)\nEOF"))


if __name__ == '__main__':
    unittest.main()
