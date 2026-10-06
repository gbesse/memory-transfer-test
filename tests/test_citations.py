import unittest

from citation_migration import audit


class CitationMigrationTests(unittest.TestCase):
    def setUp(self):
        self.source = {"records": [{"id": "old"}], "pages": [{"id": "p", "based_on": ["old"]}]}
        self.destination = {"records": [{"id": "new"}], "pages": [{"id": "p", "based_on": ["new"]}]}

    def test_remapped_citation_is_healthy(self):
        self.assertTrue(audit(self.source, self.destination, {"old": "new"})["ok"])

    def test_stale_source_id_is_detected_after_merge(self):
        self.destination["pages"][0]["based_on"] = ["old"]
        kinds = {row["kind"] for row in audit(self.source, self.destination, {"old": "new"})["findings"]}
        self.assertEqual(kinds, {"wrong_citation", "orphan"})


if __name__ == "__main__":
    unittest.main()
