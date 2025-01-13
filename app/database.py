from io import BytesIO
import sqlite3

import numpy as np

from config import DATA_DIR, DATABASE_PATH, SCHEMA_PATH


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
    return columns.get("descriptor") not in (None, "BLOB")


def init_db():
    DATA_DIR.mkdir(exist_ok=True)
    with sqlite3.connect(DATABASE_PATH) as db:
        if descriptor_storage_needs_migration(db):
            db.execute("DROP TABLE descriptors")

        with open(SCHEMA_PATH, mode="r", encoding="utf-8") as schema:
            db.executescript(schema.read())
        db.commit()


def clear_descriptors():
    init_db()
    with sqlite3.connect(DATABASE_PATH) as db:
        db.execute("DELETE FROM descriptors")
        db.commit()


def save_image_descriptor(class_name, descriptor):
    with sqlite3.connect(DATABASE_PATH) as db:
        db.execute(
            "INSERT INTO descriptors (class, descriptor) VALUES (?, ?)",
            (class_name, encode_descriptor(descriptor)),
        )
        db.commit()


def fetch_all_descriptors():
    init_db()
    with sqlite3.connect(DATABASE_PATH) as db:
        cursor = db.execute("SELECT id, class, descriptor FROM descriptors")
        return [
            (descriptor_id, class_name, decode_descriptor(descriptor))
            for descriptor_id, class_name, descriptor in cursor.fetchall()
        ]


def descriptor_count():
    init_db()
    with sqlite3.connect(DATABASE_PATH) as db:
        cursor = db.execute("SELECT COUNT(*) FROM descriptors")
        return cursor.fetchone()[0]


def descriptors_ready():
    return descriptor_count() > 0
