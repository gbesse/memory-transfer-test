import io
import json
import tempfile
import unittest
import warnings
import zipfile
from pathlib import Path

from export_receipt import audit, archive_json, demo, read_archive


SOURCE = {"bank_id": "demo", "memory_units": [
    {"id": "fact", "fact_type": "world"},
    {"id": "obs-a", "fact_type": "observation", "source_memory_ids": ["fact"]},
    {"id": "obs-b", "fact_type": "observation", "source_memory_ids": ["gone"]},
]}


class ExportReceiptTests(unittest.TestCase):
    def test_missing_orphan_is_visible(self):
        report = demo()
        self.assertEqual(report["missing_and_orphaned_ids"], ["obs-2"])

    def test_complete_archive_still_reports_orphan(self):
        report = audit(SOURCE, {"source_bank_id": "demo", "observation_count": 2},
                       [{"source_id": "obs-a"}, {"source_id": "obs-b"}])
        self.assertEqual(report["status"], "orphaned")
        self.assertEqual(report["missing_ids"], [])

    def test_missing_source_id_is_inconclusive(self):
        report = audit(SOURCE, {"source_bank_id": "demo", "observation_count": 1}, [{}])
        self.assertEqual(report["status"], "inconclusive")

    def test_bank_mismatch_rejected(self):
        with self.assertRaises(ValueError):
            audit(SOURCE, {"source_bank_id": "other", "observation_count": 0}, [])

    def test_archive_only_observation_is_not_called_missing(self):
        source = {"bank_id": "demo", "memory_units": []}
        report = audit(source, {"source_bank_id": "demo", "observation_count": 1},
                       [{"source_id": "later"}])
        self.assertEqual(report["status"], "unexpected")

    def test_zip_duplicate_entry_rejected(self):
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w") as archive:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", UserWarning)
                archive.writestr("manifest.json", json.dumps({"archive_type": "bank"}))
                archive.writestr("manifest.json", json.dumps({"archive_type": "bank"}))
        buffer.seek(0)
        with zipfile.ZipFile(buffer) as archive:
            with self.assertRaises(ValueError):
                archive_json(archive, "manifest.json")

    def test_real_zip_reader_accepts_bank_archive(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "bank.zip"
            with zipfile.ZipFile(path, "w") as archive:
                archive.writestr("manifest.json", json.dumps({"archive_type": "bank", "source_bank_id": "demo", "observation_count": 1}))
                archive.writestr("observations.json", json.dumps([{"source_id": "obs-a"}]))
            manifest, observations = read_archive(path)
        self.assertEqual(manifest["source_bank_id"], "demo")
        self.assertEqual(observations[0]["source_id"], "obs-a")


if __name__ == "__main__":
    unittest.main()
