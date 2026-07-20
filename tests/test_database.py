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
        original_descriptors_dir = config.DESCRIPTORS_DIR
        original_module_data_dir = database.DATA_DIR
        original_module_descriptors_dir = database.DESCRIPTORS_DIR

        try:
            with tempfile.TemporaryDirectory() as temporary_dir:
                temporary_path = Path(temporary_dir)
                config.DATA_DIR = temporary_path
                config.DESCRIPTORS_DIR = temporary_path / "descriptors"
                database.DATA_DIR = config.DATA_DIR
                database.DESCRIPTORS_DIR = config.DESCRIPTORS_DIR

                descriptor = np.array([[4.0, 5.0]], dtype=np.float32)
                database.init_db("laboratorio")
                database.save_image_descriptor(
                    "porta",
                    descriptor,
                    "datasets/laboratorio/porta/frame00001.png",
                    "laboratorio",
                )
                rows = database.fetch_all_descriptors("laboratorio")
        finally:
            config.DATA_DIR = original_data_dir
            config.DESCRIPTORS_DIR = original_descriptors_dir
            database.DATA_DIR = original_module_data_dir
            database.DESCRIPTORS_DIR = original_module_descriptors_dir

        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0][1], "porta")
        self.assertEqual(rows[0][2], "datasets/laboratorio/porta/frame00001.png")
        np.testing.assert_array_equal(rows[0][3], descriptor)


if __name__ == "__main__":
    unittest.main()
