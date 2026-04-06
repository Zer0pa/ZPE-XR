import unittest

from zpe_xr.comparator_triage import COMPARATOR_TRIAGE_WARNING, build_comparator_triage_report


class ComparatorTriageTests(unittest.TestCase):
    def test_report_locks_warning_and_first_target(self) -> None:
        report = build_comparator_triage_report()
        self.assertEqual(report["warning"], COMPARATOR_TRIAGE_WARNING)
        self.assertEqual(report["first_target"], "modern_float16_delta_plus_zlib_local")

        by_id = {candidate["comparator_id"]: candidate for candidate in report["candidates"]}
        self.assertEqual(by_id[report["first_target"]]["priority"], "first_target")

    def test_market_reference_rows_stay_blocked(self) -> None:
        report = build_comparator_triage_report()
        by_id = {row["comparator_id"]: row for row in report["candidates"]}
        self.assertEqual(by_id["unity_ngo"]["priority"], "blocked")
        self.assertFalse(by_id["unity_ngo"]["executable_now"])
        self.assertEqual(by_id["normcore"]["priority"], "blocked")

    def test_photon_stays_deferred_due_to_semantics_gap(self) -> None:
        report = build_comparator_triage_report()
        by_id = {row["comparator_id"]: row for row in report["candidates"]}
        self.assertEqual(by_id["photon_fusion_xr_hands_doc"]["priority"], "defer")
        self.assertIn("narrower", by_id["photon_fusion_xr_hands_doc"]["authority_alignment"])
