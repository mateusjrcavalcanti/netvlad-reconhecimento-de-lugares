from pathlib import Path


APP_DIR = Path(__file__).resolve().parent
ROOT_DIR = APP_DIR.parent
DATA_DIR = ROOT_DIR / "data"
DATASET_DIR = ROOT_DIR / "dataset"
CSV_PATH = DATASET_DIR / "labeled_dataset.csv"
DATABASE_PATH = DATA_DIR / "database.db"
UPLOAD_DIR = DATA_DIR / "uploads"
NETVLAD_CHECKPOINT_PATH = DATA_DIR / "netvlad_checkpoint.pt"
SCHEMA_PATH = APP_DIR / "schema.sql"
