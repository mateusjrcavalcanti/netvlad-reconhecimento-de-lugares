from pathlib import Path


APP_DIR = Path(__file__).resolve().parent
ROOT_DIR = APP_DIR.parent
DATA_DIR = ROOT_DIR / "data"
DATASETS_DIR = ROOT_DIR / "datasets"
DESCRIPTORS_DIR = DATA_DIR / "descriptors"
UPLOAD_DIR = DATA_DIR / "uploads"
NETVLAD_CHECKPOINT_PATH = DATA_DIR / "netvlad_checkpoint.pt"
SCHEMA_PATH = APP_DIR / "schema.sql"
