import sys
import tempfile
import unittest
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR / "app"))

import config  # noqa: E402
import datasets  # noqa: E402


class DatasetSummaryTest(unittest.TestCase):
    def test_directory_dataset_summary_counts_classes_and_images(self):
        original_datasets_dir = config.DATASETS_DIR
        original_module_datasets_dir = datasets.DATASETS_DIR

        try:
            with tempfile.TemporaryDirectory() as temporary_dir:
                datasets_dir = Path(temporary_dir)
                class_dir = datasets_dir / "laboratorio" / "porta"
                class_dir.mkdir(parents=True)
                (class_dir / "frame00001.png").touch()
                (class_dir / "notes.txt").touch()

                config.DATASETS_DIR = datasets_dir
                datasets.DATASETS_DIR = config.DATASETS_DIR

                summary = datasets.dataset_summary("laboratorio")
        finally:
            config.DATASETS_DIR = original_datasets_dir
            datasets.DATASETS_DIR = original_module_datasets_dir

        self.assertEqual(summary["available_images"], 1)
        self.assertEqual(summary["classes"], 1)

    def test_list_dataset_names_returns_directory_datasets(self):
        original_datasets_dir = config.DATASETS_DIR
        original_module_datasets_dir = datasets.DATASETS_DIR

        try:
            with tempfile.TemporaryDirectory() as temporary_dir:
                datasets_dir = Path(temporary_dir)
                (datasets_dir / "laboratorio").mkdir()
                (datasets_dir / "externo").mkdir()
                (datasets_dir / "notes.txt").touch()

                config.DATASETS_DIR = datasets_dir
                datasets.DATASETS_DIR = config.DATASETS_DIR

                names = datasets.list_dataset_names()
        finally:
            config.DATASETS_DIR = original_datasets_dir
            datasets.DATASETS_DIR = original_module_datasets_dir

        self.assertEqual(names, ["externo", "laboratorio"])

    def test_delete_image_and_class_updates_dataset(self):
        original_datasets_dir = config.DATASETS_DIR
        original_module_datasets_dir = datasets.DATASETS_DIR

        try:
            with tempfile.TemporaryDirectory() as temporary_dir:
                datasets_dir = Path(temporary_dir)
                class_dir = datasets_dir / "laboratorio" / "porta"
                class_dir.mkdir(parents=True)
                (class_dir / "frame00001.png").touch()

                config.DATASETS_DIR = datasets_dir
                datasets.DATASETS_DIR = config.DATASETS_DIR

                image_message = datasets.delete_image("laboratorio", "porta", "frame00001.png")
                class_message = datasets.delete_class("laboratorio", "porta")
        finally:
            config.DATASETS_DIR = original_datasets_dir
            datasets.DATASETS_DIR = original_module_datasets_dir

        self.assertIn("removida", image_message)
        self.assertIn("removida", class_message)

    def test_parse_video_intervals_validates_rows(self):
        intervals = datasets.parse_video_intervals([[0, 2.5, "porta"], [3, 4, "corredor"]])

        self.assertEqual(
            intervals,
            [
                {"start": 0.0, "end": 2.5, "class": "porta"},
                {"start": 3.0, "end": 4.0, "class": "corredor"},
            ],
        )


if __name__ == "__main__":
    unittest.main()
