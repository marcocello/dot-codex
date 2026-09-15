import csv
import importlib.util
import tempfile
import unittest
from pathlib import Path


SCRIPT_PATH = Path(__file__).with_name("merge_findings.py")


def load_merge_module():
    spec = importlib.util.spec_from_file_location("merge_findings", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class MergeFindingsTest(unittest.TestCase):
    def setUp(self):
        self.module = load_merge_module()
        self.tempdir = tempfile.TemporaryDirectory()
        self.addCleanup(self.tempdir.cleanup)
        self.root = Path(self.tempdir.name)
        self.fields = self.module.fields_for(self.module.GENERIC_SCORE_LIMITS)

    def write_rows(self, path, rows, fields=None):
        with path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fields or self.fields)
            writer.writeheader()
            writer.writerows(rows)

    def row(self, url, title="Senior Product Engineer", overall="84"):
        return {
            "analysis_date": "2026-08-19",
            "provider": "Example Jobs",
            "provider_rank": "1",
            "job_title": title,
            "company": "Example Co",
            "location": "Remote",
            "work_mode": "remote",
            "employment_type": "full-time",
            "job_url": url,
            "listing_date": "",
            "role_scope_points": "26",
            "experience_evidence_points": "20",
            "objective_alignment_points": "18",
            "practical_conditions_points": str(int(overall) - 64),
            "overall_points": overall,
            "fit": "strong",
            "reason": "Strong match to the supplied profile and objective.",
            "missing_constraints": "Compensation; work authorization",
        }

    def read_rows(self, path):
        with path.open(encoding="utf-8", newline="") as handle:
            return list(csv.DictReader(handle))

    def test_preserves_history_and_skips_canonical_url_duplicates(self):
        existing = self.root / "findings.csv"
        incoming = self.root / "incoming.csv"
        old = self.row("https://example.com/jobs/1?utm_source=old")
        duplicate = self.row("https://EXAMPLE.com/jobs/1/?utm_medium=new#apply")
        new = self.row("https://example.com/jobs/2", title="Platform Lead", overall="78")
        self.write_rows(existing, [old])
        self.write_rows(incoming, [duplicate, new])

        result = self.module.merge_findings(existing, incoming, existing)

        self.assertEqual(result, {"existing": 1, "added": 1, "duplicates": 1})
        self.assertEqual(self.read_rows(existing), [old, new])

    def test_creates_history_with_generic_schema(self):
        existing = self.root / "findings.csv"
        incoming = self.root / "incoming.csv"
        new = self.row("https://example.com/jobs/3")
        self.write_rows(incoming, [new])

        result = self.module.merge_findings(existing, incoming, existing)

        self.assertEqual(result, {"existing": 0, "added": 1, "duplicates": 0})
        self.assertEqual(self.read_rows(existing), [new])

    def test_accepts_legacy_scorecard_for_existing_histories(self):
        fields = self.module.fields_for(self.module.LEGACY_SCORE_LIMITS)
        legacy = self.row("https://example.com/jobs/4")
        for generic, old in zip(
            self.module.GENERIC_SCORE_LIMITS,
            self.module.LEGACY_SCORE_LIMITS,
        ):
            legacy[old] = legacy.pop(generic)
        existing = self.root / "findings.csv"
        incoming = self.root / "incoming.csv"
        self.write_rows(existing, [legacy], fields)
        self.write_rows(incoming, [legacy], fields)

        result = self.module.merge_findings(existing, incoming, existing)

        self.assertEqual(result, {"existing": 1, "added": 0, "duplicates": 1})

    def test_rejects_a_header_mismatch(self):
        existing = self.root / "findings.csv"
        incoming = self.root / "incoming.csv"
        self.write_rows(existing, [self.row("https://example.com/jobs/5")])
        legacy_fields = self.module.fields_for(self.module.LEGACY_SCORE_LIMITS)
        legacy = self.row("https://example.com/jobs/6")
        for generic, old in zip(
            self.module.GENERIC_SCORE_LIMITS,
            self.module.LEGACY_SCORE_LIMITS,
        ):
            legacy[old] = legacy.pop(generic)
        self.write_rows(incoming, [legacy], legacy_fields)

        with self.assertRaisesRegex(ValueError, "header must match"):
            self.module.merge_findings(existing, incoming, existing)

    def test_rejects_an_overall_score_that_does_not_equal_components(self):
        existing = self.root / "findings.csv"
        incoming = self.root / "incoming.csv"
        invalid = self.row("https://example.com/jobs/7", overall="99")
        invalid["practical_conditions_points"] = "20"
        self.write_rows(incoming, [invalid])

        with self.assertRaisesRegex(ValueError, "overall_points"):
            self.module.merge_findings(existing, incoming, existing)


if __name__ == "__main__":
    unittest.main()
