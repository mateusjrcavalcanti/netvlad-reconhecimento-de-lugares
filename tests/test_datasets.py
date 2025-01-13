import sys
import tempfile
import unittest
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR / "app"))

import config  # noqa: E402
import datasets  # noqa: E402


class DatasetSummaryTest(unittest.TestCase):
    def test_dataset_summary_counts_available_and_missing_images(self):
        original_dataset_dir = config.DATASET_DIR
        original_csv_path = config.CSV_PATH
        original_module_dataset_dir = datasets.DATASET_DIR
        original_module_csv_path = datasets.CSV_PATH

        try:
            with tempfile.TemporaryDirectory() as temporary_dir:
                dataset_dir = Path(temporary_dir)
                csv_path = dataset_dir / "labeled_dataset.csv"
                csv_path.write_text(
                    "frame00001.png;bancadas_a;\nframe00006.png;bancadas_a;\n",
                    encoding="utf-8",
                )
                (dataset_dir / "frame00001.png").touch()

                config.DATASET_DIR = dataset_dir
                config.CSV_PATH = csv_path
                datasets.DATASET_DIR = config.DATASET_DIR
                datasets.CSV_PATH = config.CSV_PATH

                summary = datasets.dataset_summary()
        finally:
            config.DATASET_DIR = original_dataset_dir
            config.CSV_PATH = original_csv_path
            datasets.DATASET_DIR = original_module_dataset_dir
            datasets.CSV_PATH = original_module_csv_path

        self.assertEqual(summary["csv_rows"], 2)
        self.assertEqual(summary["available_images"], 1)
        self.assertEqual(summary["missing_images"], 1)
        self.assertEqual(summary["classes"], 1)
        self.assertEqual(summary["missing_filenames"], ["frame00006.png"])


if __name__ == "__main__":
    unittest.main()
