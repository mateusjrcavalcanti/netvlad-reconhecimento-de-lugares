import gradio as gr
import pandas as pd

from config import CSV_PATH, DATABASE_PATH, DATASET_DIR
from database import clear_descriptors, init_db, save_image_descriptor
from netvlad.utils import extract_netvlad_descriptor


def read_labeled_dataset():
    if not CSV_PATH.exists():
        raise FileNotFoundError(f"Dataset labels not found: {CSV_PATH}")

    return pd.read_csv(
        CSV_PATH,
        sep=";",
        header=None,
        names=["filename", "class", "unused"],
        engine="python",
    )


def load_locations():
    data = read_labeled_dataset()
    locations = {}

    for _, row in data.iterrows():
        locations.setdefault(row["class"], []).append(row["filename"])

    return locations


def dataset_summary():
    data = read_labeled_dataset()
    rows = []
    missing = []

    for _, row in data.iterrows():
        filename = row["filename"]
        class_name = row["class"]
        image_path = DATASET_DIR / filename
        rows.append((filename, class_name, image_path.exists()))

        if not image_path.exists():
            missing.append(filename)

    return {
        "csv_rows": len(rows),
        "available_images": sum(1 for _, _, exists in rows if exists),
        "missing_images": len(missing),
        "classes": len({class_name for _, class_name, _ in rows}),
        "missing_filenames": missing,
    }


def dataset_gallery(location):
    if not location:
        return "Nenhuma classe/local selecionado.", []

    locations = load_locations()
    filenames = locations.get(location, [])
    images = [str(DATASET_DIR / filename) for filename in filenames if (DATASET_DIR / filename).exists()]
    return f"{len(images)} imagens encontradas em {location}.", images


def describe_dataset_images(progress=gr.Progress()):
    init_db()
    clear_descriptors()
    data = read_labeled_dataset()

    total = len(data.index)
    processed = 0
    skipped = 0

    progress(0, desc="Preparando geração de descritores")

    for index, (_, row) in enumerate(data.iterrows(), start=1):
        image_path = DATASET_DIR / row["filename"]
        progress(index / total, desc=f"Processando {index}/{total}: {row['filename']}")

        if not image_path.exists():
            skipped += 1
            continue

        descriptor = extract_netvlad_descriptor(str(image_path))
        save_image_descriptor(row["class"], descriptor)
        processed += 1

    progress(1, desc="Descritores gerados")

    return (
        f"Descritores gerados para {processed} imagens em {DATABASE_PATH}. "
        f"{skipped} imagens do CSV foram ignoradas porque nao existem no dataset."
    )
