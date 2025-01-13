import sys
import tempfile
import unittest
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR / "scripts"))

from generate_labeled_dataset import generate_labeled_dataset, resolve_image_class  # noqa: E402


class DatasetLabelGenerationTest(unittest.TestCase):
    def test_resolves_expected_classes_from_frame_number(self):
        self.assertEqual(resolve_image_class("frame00001.png"), "bancadas_a")
        self.assertEqual(resolve_image_class("frame00211.png"), "bancadas_b")
        self.assertEqual(resolve_image_class("frame00456.png"), "corredor")
        self.assertEqual(resolve_image_class("frame01351.png"), "armarios")
        self.assertEqual(resolve_image_class("frame01751.png"), "porta")

    def test_generates_csv_rows_for_available_frames(self):
        with tempfile.TemporaryDirectory() as temporary_dir:
            dataset_dir = Path(temporary_dir)
            (dataset_dir / "frame00001.png").touch()
            (dataset_dir / "frame01751.png").touch()
            (dataset_dir / "notes.txt").touch()

            csv_content = generate_labeled_dataset(dataset_dir)

        self.assertEqual(
            csv_content,
            "frame00001.png;bancadas_a;\r\nframe01751.png;porta;\r\n",
        )


if __name__ == "__main__":
    unittest.main()
