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
