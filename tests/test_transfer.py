import json
import unittest
from pathlib import Path
from memory_transfer import check

EXAMPLES = Path(__file__).resolve().parents[1] / 'examples'


def read(name, key):
    return json.loads((EXAMPLES / name).read_text())[key]


class TransferTests(unittest.TestCase):
    def test_valid_migration(self):
        result = check(read('source.json', 'records'), read('destination-ok.json', 'records'), read('probes.json', 'probes'))
        self.assertTrue(result['pass'])

    def test_correction_forget_and_scope_regressions(self):
        result = check(read('source.json', 'records'), read('destination-bug.json', 'records'), read('probes.json', 'probes'))
        self.assertFalse(result['pass'])
        self.assertEqual(result['unexpected_ids'], ['m1', 'm3'])
        self.assertEqual(result['changed_ids'], ['m4'])
        self.assertGreaterEqual(sum(not p['pass'] for p in result['probes']), 3)


class LineageValidationTests(unittest.TestCase):
    def record(self, identifier='m1', **fields):
        return dict(id=identifier, text='private sample', scope='team:a', provenance='chat:1', **fields)

    def assert_invalid(self, records, code):
        result = check(records, records, [])
        self.assertFalse(result['pass'])
        self.assertFalse(result['input_valid'])
        self.assertIn(code, [item['code'] for item in result['validation_errors']])
        self.assertNotIn('private sample', json.dumps(result))

    def test_duplicate_id_cannot_hide_different_facts(self):
        self.assert_invalid([self.record(), self.record()], 'duplicate_id')

    def test_cross_scope_correction_cannot_hide_another_scope(self):
        a = self.record(); b = self.record('m2', supersedes='m1'); b['scope'] = 'team:b'
        self.assert_invalid([a, b], 'cross_scope_correction')

    def test_self_and_long_cycles_are_invalid(self):
        self.assert_invalid([self.record(supersedes='m1')], 'correction_cycle')
        self.assert_invalid([self.record('m1', supersedes='m2'), self.record('m2', supersedes='m1')], 'correction_cycle')

    def test_deleted_correction_does_not_resurrect_old_fact(self):
        source = [self.record(), self.record('m2', supersedes='m1', status='deleted')]
        self.assertTrue(check(source, [], [])['pass'])
        self.assertFalse(check(source, [self.record()], [])['pass'])

    def test_compacted_missing_target_is_allowed(self):
        rows = [self.record('m2', supersedes='compacted-m1')]
        self.assertTrue(check(rows, rows, [])['pass'])

    def test_invalid_shape_status_and_probes_are_blocked(self):
        self.assert_invalid([self.record(status='unknown')], 'invalid_status')
        self.assert_invalid([{'id': 'm1'}], 'record_shape')
        self.assert_invalid([self.record(supersedes=[])], 'invalid_supersedes')
        self.assertFalse(check([], [], [{'scope': 'team:a', 'term': []}])['input_valid'])

    def test_long_acyclic_history_is_iterative(self):
        rows = [self.record(str(i), supersedes=str(i-1)) for i in range(3000)]
        self.assertTrue(check(rows, rows, [])['pass'])
