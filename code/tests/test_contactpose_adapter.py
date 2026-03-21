from io import BytesIO
import json
from pathlib import Path
import unittest
import zipfile

from zpe_xr.contactpose_adapter import (
    annotation_candidates_from_zip,
    contactpose_21_to_zpe_xr_26,
    read_annotation_from_zip,
)


class ContactPoseAdapterTests(unittest.TestCase):
    def test_contactpose_topology_bridge_returns_26_joints(self) -> None:
        hand = [(float(idx), float(idx + 1), float(idx + 2)) for idx in range(21)]
        converted = contactpose_21_to_zpe_xr_26(hand)
        self.assertEqual(len(converted), 26)
        self.assertEqual(converted[0], hand[0])
        self.assertEqual(converted[2:6], tuple(hand[1:5]))

    def test_annotation_candidates_from_sample_bundle_recurse_nested_archives(self) -> None:
        outer_zip = self._write_sample_bundle(Path(self.id().replace(".", "_") + ".zip"))

        candidates = annotation_candidates_from_zip(outer_zip, min_frames=45, require_both_hands=True)

        self.assertEqual(len(candidates), 1)
        self.assertEqual(candidates[0].object_name, "wine_glass")
        self.assertIn("::", candidates[0].archive_member)

        annotation = read_annotation_from_zip(outer_zip, candidates[0].archive_member)
        self.assertEqual(annotation["object"], "wine_glass")
        self.assertEqual(len(annotation["frames"]), 50)

    def _write_sample_bundle(self, filename: Path) -> Path:
        outer_zip = Path(self._testMethodName + "_" + filename.name).resolve()
        annotation = {
            "object": "wine_glass",
            "hands": [
                {"valid": True, "joints": [[0.0, 0.0, 0.0] for _ in range(21)]},
                {"valid": True, "joints": [[1.0, 1.0, 1.0] for _ in range(21)]},
            ],
            "frames": [{"hTo": [{}, {}]} for _ in range(50)],
        }

        object_zip_bytes = BytesIO()
        with zipfile.ZipFile(object_zip_bytes, "w") as object_zip:
            object_zip.writestr("wine_glass/annotations.json", json.dumps(annotation))

        grasps_zip_bytes = BytesIO()
        with zipfile.ZipFile(grasps_zip_bytes, "w") as grasps_zip:
            grasps_zip.writestr("grasps/full28_use/wine_glass.zip", object_zip_bytes.getvalue())

        with zipfile.ZipFile(outer_zip, "w") as outer:
            outer.writestr("ContactPose sample data/grasps.zip", grasps_zip_bytes.getvalue())

        self.addCleanup(lambda: outer_zip.unlink(missing_ok=True))
        return outer_zip
