import copy
import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('claim_registry_shape', ROOT / 'tools/claim_registry.py')
cr = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cr)


def outcome(function, value, schema):
    try:
        function(value, schema)
        return None
    except ValueError as error:
        return str(error)


class CompiledShapeTest(unittest.TestCase):
    """The compiled schema checkers agree with the direct interpreter, message for message."""

    def setUp(self):
        self.schema = json.loads((ROOT / 'research/claims/schema.json').read_text())
        registry = json.loads((ROOT / 'research/claims/index.json').read_text())
        self.value = dict(registry, claims=registry['claims'][:3])

    def test_valid_sample_and_mutations_agree(self):
        cases = [self.value]
        broken = copy.deepcopy(self.value); broken['claims'][1]['id'] = ''
        cases.append(broken)
        broken = copy.deepcopy(self.value); broken['claims'][2]['unknown_field'] = 1
        cases.append(broken)
        broken = copy.deepcopy(self.value); del broken['claims'][0]['id']
        cases.append(broken)
        broken = copy.deepcopy(self.value); broken['claims'][0]['id'] = 7
        cases.append(broken)
        broken = copy.deepcopy(self.value); broken['claims'][1]['id'] = 'not an id!'
        cases.append(broken)
        for case in cases:
            with self.subTest(case=cases.index(case)):
                expected = outcome(cr._shape_reference, case, self.schema)
                self.assertEqual(outcome(cr.shape, case, self.schema), expected)
        self.assertIsNone(outcome(cr.shape, self.value, self.schema))
        self.assertIsNotNone(outcome(cr.shape, cases[1], self.schema))


if __name__ == '__main__':
    unittest.main()
