from io import BytesIO
import sqlite3

import numpy as np

from config import DATA_DIR, DESCRIPTORS_DIR, SCHEMA_PATH


def normalize_dataset_name(dataset_name):
    value = str(dataset_name or "").strip()
    if not value:
        raise ValueError("Selecione um dataset.")
    return value


def descriptor_database_path(dataset_name):
    dataset_name = normalize_dataset_name(dataset_name)
    return DESCRIPTORS_DIR / f"{dataset_name}.db"


def encode_descriptor(descriptor):
    buffer = BytesIO()
    np.save(buffer, np.asarray(descriptor, dtype=np.float32), allow_pickle=False)
    return buffer.getvalue()


def decode_descriptor(descriptor_blob):
    buffer = BytesIO(descriptor_blob)
    return np.load(buffer, allow_pickle=False)


def descriptor_storage_needs_migration(db):
    cursor = db.execute("PRAGMA table_info(descriptors)")
    columns = {row[1]: row[2].upper() for row in cursor.fetchall()}
    if not columns:
        return False
    return columns.get("descriptor") != "BLOB" or "image_path" not in columns


def init_db(dataset_name):
    DATA_DIR.mkdir(exist_ok=True)
    DESCRIPTORS_DIR.mkdir(exist_ok=True)
    database_path = descriptor_database_path(dataset_name)
    database_path.parent.mkdir(exist_ok=True)

    with sqlite3.connect(database_path) as db:
        if descriptor_storage_needs_migration(db):
            db.execute("DROP TABLE descriptors")

        with open(SCHEMA_PATH, mode="r", encoding="utf-8") as schema:
            db.executescript(schema.read())
        db.commit()


def clear_descriptors(dataset_name):
    init_db(dataset_name)
    with sqlite3.connect(descriptor_database_path(dataset_name)) as db:
        db.execute("DELETE FROM descriptors")
        db.commit()


def save_image_descriptor(class_name, descriptor, image_path, dataset_name):
    with sqlite3.connect(descriptor_database_path(dataset_name)) as db:
        db.execute(
            "INSERT INTO descriptors (class, image_path, descriptor) VALUES (?, ?, ?)",
            (class_name, str(image_path), encode_descriptor(descriptor)),
        )
        db.commit()


def fetch_all_descriptors(dataset_name):
    init_db(dataset_name)
    with sqlite3.connect(descriptor_database_path(dataset_name)) as db:
        cursor = db.execute("SELECT id, class, image_path, descriptor FROM descriptors")
        return [
            (descriptor_id, class_name, image_path, decode_descriptor(descriptor))
            for descriptor_id, class_name, image_path, descriptor in cursor.fetchall()
        ]


def descriptor_count(dataset_name):
    init_db(dataset_name)
    with sqlite3.connect(descriptor_database_path(dataset_name)) as db:
        cursor = db.execute("SELECT COUNT(*) FROM descriptors")
        return cursor.fetchone()[0]


def descriptors_ready(dataset_name):
    return descriptor_count(dataset_name) > 0
