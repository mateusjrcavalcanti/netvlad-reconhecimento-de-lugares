import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np


ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR / "app"))

import config  # noqa: E402
import database  # noqa: E402


class DescriptorDatabaseTest(unittest.TestCase):
    def test_descriptor_blob_round_trip(self):
        descriptor = np.array([[1.25, 2.5, 3.75]], dtype=np.float32)
        blob = database.encode_descriptor(descriptor)
        decoded = database.decode_descriptor(blob)

        np.testing.assert_array_equal(decoded, descriptor)
        self.assertEqual(decoded.dtype, np.float32)

    def test_save_and_fetch_descriptor_from_sqlite(self):
        original_data_dir = config.DATA_DIR
        original_database_path = config.DATABASE_PATH
        original_module_data_dir = database.DATA_DIR
        original_module_database_path = database.DATABASE_PATH

        try:
            with tempfile.TemporaryDirectory() as temporary_dir:
                temporary_path = Path(temporary_dir)
                config.DATA_DIR = temporary_path
                config.DATABASE_PATH = temporary_path / "database.db"
                database.DATA_DIR = config.DATA_DIR
                database.DATABASE_PATH = config.DATABASE_PATH

                descriptor = np.array([[4.0, 5.0]], dtype=np.float32)
                database.init_db()
                database.save_image_descriptor("porta", descriptor)
                rows = database.fetch_all_descriptors()
        finally:
            config.DATA_DIR = original_data_dir
            config.DATABASE_PATH = original_database_path
            database.DATA_DIR = original_module_data_dir
            database.DATABASE_PATH = original_module_database_path

        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0][1], "porta")
        np.testing.assert_array_equal(rows[0][2], descriptor)


if __name__ == "__main__":
    unittest.main()
