import unittest

from zpe_xr.public_benchmark_catalog import build_public_benchmark_manifest, public_hand_dataset_specs


class PublicBenchmarkCatalogTests(unittest.TestCase):
    def test_catalog_contains_contactpose_and_five_new_public_datasets(self) -> None:
        dataset_ids = [spec.dataset_id for spec in public_hand_dataset_specs()]
        self.assertEqual(
            dataset_ids,
            ["contactpose", "interhand26m", "freihand", "ho3d", "dexycb", "oakink"],
        )

    def test_contactpose_is_only_runnable_dataset_lane(self) -> None:
        specs = {spec.dataset_id: spec for spec in public_hand_dataset_specs()}
        self.assertEqual(specs["contactpose"].adapter_status, "runnable")
        self.assertEqual(specs["contactpose"].tests_requiring_data, ())
        self.assertTrue(specs["contactpose"].homepage.startswith("https://drive.google.com/"))

    def test_manifest_marks_new_dataset_rows_as_scaffold_only(self) -> None:
        manifest = build_public_benchmark_manifest()
        self.assertEqual(manifest["artifact_class"], "planning_scaffold_only")
        self.assertEqual(manifest["datasets"][0]["dataset_id"], "contactpose")
        self.assertEqual(manifest["datasets"][0]["scaffold_status"], "baseline_available")

        planned = {row["dataset_id"]: row for row in manifest["datasets"][1:]}
        self.assertTrue(all(row["scaffold_status"] == "not_run" for row in planned.values()))
