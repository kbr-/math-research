import copy
import importlib.util
from pathlib import Path
import sys
import unittest

TOOLS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS))
spec = importlib.util.spec_from_file_location('remap_revisions', TOOLS / 'remap-revisions.py')
rr = importlib.util.module_from_spec(spec); spec.loader.exec_module(rr)
from claim_reviews import claim_digest, digest, field_value
from claim_attention import fingerprint

OLD, NEW, OTHER = 'a' * 40, 'b' * 40, 'c' * 40


def claim(cid):
    return {'id': cid, 'summary': 'S ' + cid, 'assessment': 'Working', 'record': '[R](x.html#a)',
            'mathematical_status': 'working_proof', 'topics': [], 'significance': None,
            'formalization': {'status': 'not_started'}, 'reviews': {}}


def edge(src, kind, tgt, rev):
    return {'id': f'{src}::{kind}::{tgt}', 'type': kind,
            'source': {'namespace': 'current', 'id': src, 'locator': None},
            'target': {'namespace': 'current', 'id': tgt, 'locator': None},
            'review': {'revision': rev}}


def registry():
    data = {'claims': [claim('lem:a'), claim('lem:b')],
            'relationships': [edge('lem:a', 'corrects', 'lem:b', OLD)]}
    for c in data['claims']:
        for field in ('relationships', 'significance'):
            c['reviews'][field] = {'revision': OLD if c['id'] == 'lem:a' else OTHER,
                                   'claim_sha256': claim_digest(c),
                                   'value_sha256': digest(field_value(data, c, field))}
    return data


class RemapRevisionsTest(unittest.TestCase):
    def test_revisions_and_remap_only_hashes_are_updated(self):
        data = registry()
        stale_value = 'f' * 64
        data['claims'][1]['reviews']['significance']['value_sha256'] = stale_value  # stale for another reason
        new, changed, refreshed = rr.remap_registry(data, {OLD: NEW})
        self.assertEqual(changed, 3)  # the edge and lem:a's two reviews; lem:b's name OTHER
        self.assertEqual(new['relationships'][0]['review']['revision'], NEW)
        self.assertEqual(sorted(refreshed), ['lem:a.relationships.value_sha256', 'lem:b.relationships.value_sha256'])
        for c in new['claims']:
            self.assertEqual(c['reviews']['relationships']['value_sha256'],
                             digest(field_value(new, c, 'relationships')))
        self.assertEqual(new['claims'][1]['reviews']['significance']['value_sha256'], stale_value)
        self.assertEqual(data['relationships'][0]['review']['revision'], OLD)  # input untouched

    def test_attention_fingerprints_follow_correction_edges(self):
        data = registry()
        old_fp = fingerprint(data, data['claims'][0])
        attention = {'events': [{'claim': 'lem:a', 'fingerprint': old_fp},
                                {'claim': 'lem:a', 'fingerprint': 'earlier'}]}
        new, _, _ = rr.remap_registry(data, {OLD: NEW})
        self.assertEqual(rr.remap_attention(attention, data, new), 1)
        self.assertEqual(attention['events'][0]['fingerprint'], fingerprint(new, new['claims'][0]))
        self.assertEqual(attention['events'][1]['fingerprint'], 'earlier')

    def test_unmapped_registry_is_unchanged(self):
        data = registry()
        new, changed, refreshed = rr.remap_registry(data, {'d' * 40: NEW})
        self.assertEqual((new, changed, refreshed), (data, 0, []))


if __name__ == '__main__':
    unittest.main()
