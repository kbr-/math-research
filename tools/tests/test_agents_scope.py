import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
# Nouns of particular research goals.  AGENTS.md holds rules for every notebook; a rule that needs one of these
# belongs in that notebook's living sections (user, 10 October 2026).  The list cannot catch a goal-specific
# rule written in general words.
GOAL_WORDS = ('near-half', 'parity', 'CNF', 'polynomial calculus', 'PC degree', 'pigeonhole', 'deficit',
              'ceiling', 'kernel', 'cutoff', 'syzyg', 'Boolean', 'F_2', 'Tseitin', 'binomial', 'covering sum')


class AgentsScopeTest(unittest.TestCase):
    def test_agents_md_has_no_goal_vocabulary(self):
        text = (ROOT / 'AGENTS.md').read_text()
        found = [word for word in GOAL_WORDS if re.search(re.escape(word), text, re.I)]
        self.assertEqual(found, [], 'goal-specific words in AGENTS.md; move the rule to the notebook it concerns')


if __name__ == '__main__':
    unittest.main()
