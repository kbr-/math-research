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


if __name__ == '__main__':
    unittest.main()
