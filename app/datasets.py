import re
import shutil
from pathlib import Path

import gradio as gr

from config import DATASETS_DIR
from database import clear_descriptors, descriptor_database_path, init_db, save_image_descriptor
from netvlad.utils import extract_netvlad_descriptor


IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".bmp", ".gif", ".webp"}
SAFE_NAME_PATTERN = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9_-]*$")


def validate_name(name, field_name="nome"):
    value = (name or "").strip()
    if not SAFE_NAME_PATTERN.match(value):
        raise ValueError(
            f"{field_name} invalido. Use letras, numeros, hifen ou underscore, sem espacos."
        )
    return value


def is_image(path):
    return path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS


def dataset_path(dataset_name):
    dataset_name = validate_name(dataset_name, "dataset")
    return DATASETS_DIR / dataset_name


def dataset_items(dataset_name):
    root = dataset_path(dataset_name)
    items = []

    if not root.exists():
        return items

    for class_path in sorted(path for path in root.iterdir() if path.is_dir()):
        for image_path in sorted(path for path in class_path.iterdir() if is_image(path)):
            items.append(
                {
                    "dataset": dataset_name,
                    "class": class_path.name,
                    "filename": image_path.name,
                    "path": image_path,
                }
            )

    return items


def class_names(dataset_name):
    if not dataset_name:
        return []
    return sorted({item["class"] for item in dataset_items(dataset_name)})


def image_names(dataset_name, class_name):
    if not dataset_name or not class_name:
        return []

    root = dataset_path(dataset_name)
    class_name = validate_name(class_name, "classe")
    class_path = root / class_name
    if not class_path.exists():
        return []

    return sorted(path.name for path in class_path.iterdir() if is_image(path))


def load_locations(dataset_name):
    locations = {}

    for item in dataset_items(dataset_name):
        locations.setdefault(item["class"], []).append(item["filename"])

    return locations


def list_dataset_names():
    if not DATASETS_DIR.exists():
        return []

    return sorted(path.name for path in DATASETS_DIR.iterdir() if path.is_dir())


def dataset_summary(dataset_name):
    items = dataset_items(dataset_name) if dataset_name else []

    return {
        "dataset": dataset_name,
        "classes": len({item["class"] for item in items}),
        "available_images": len(items),
        "database_path": descriptor_database_path(dataset_name) if dataset_name else "",
    }


def datasets_table():
    rows = []
    for dataset_name in list_dataset_names():
        summary = dataset_summary(dataset_name)
        rows.append(
            [
                dataset_name,
                summary["classes"],
                summary["available_images"],
                str(summary["database_path"]),
            ]
        )
    return rows


def dataset_gallery(dataset_name, location):
    if not dataset_name:
        return "Nenhum dataset selecionado.", [], gr.update(choices=[], value=None)

    locations = load_locations(dataset_name)
    location_choices = sorted(locations.keys())
    selected_location = location if location in locations else (location_choices[0] if location_choices else None)

    if not selected_location:
        return "Nenhuma classe/local encontrada.", [], gr.update(choices=location_choices, value=None)

    items = [item for item in dataset_items(dataset_name) if item["class"] == selected_location]
    images = [str(item["path"]) for item in items]

    return (
        f"{len(images)} imagens encontradas em {selected_location}.",
        images,
        gr.update(choices=location_choices, value=selected_location),
    )


def dataset_choices_update(selected_dataset=None):
    names = list_dataset_names()
    value = selected_dataset if selected_dataset in names else (names[0] if names else None)
    return gr.update(choices=names, value=value)


def create_dataset(dataset_name):
    dataset_name = validate_name(dataset_name, "dataset")
    root = dataset_path(dataset_name)
    if root.exists():
        return f"Dataset {dataset_name} ja existe.", dataset_choices_update(dataset_name)

    root.mkdir(parents=True)
    return f"Dataset {dataset_name} criado.", dataset_choices_update(dataset_name)


def delete_dataset(dataset_name):
    root = dataset_path(dataset_name)
    if not root.exists():
        return f"Dataset {dataset_name} nao encontrado.", dataset_choices_update()

    shutil.rmtree(root)
    return f"Dataset {dataset_name} removido.", dataset_choices_update()


def create_class(dataset_name, class_name):
    root = dataset_path(dataset_name)
    if not root.exists():
        return "Crie ou selecione um dataset primeiro."

    class_name = validate_name(class_name, "classe")
    (root / class_name).mkdir(parents=True, exist_ok=True)
    return f"Classe {class_name} criada em {dataset_name}."


def delete_class(dataset_name, class_name):
    root = dataset_path(dataset_name)
    class_name = validate_name(class_name, "classe")
    class_path = root / class_name

    if not class_path.exists() or not class_path.is_dir():
        return f"Classe {class_name} nao encontrada em {dataset_name}."

    shutil.rmtree(class_path)
    return f"Classe {class_name} removida de {dataset_name}."


def rename_class(dataset_name, class_name, new_class_name):
    root = dataset_path(dataset_name)
    class_name = validate_name(class_name, "classe ativa")
    new_class_name = validate_name(new_class_name, "novo nome da classe")

    source_path = root / class_name
    destination_path = root / new_class_name

    if not source_path.exists() or not source_path.is_dir():
        return f"Classe {class_name} nao encontrada em {dataset_name}."
    if destination_path.exists():
        return f"Ja existe uma classe chamada {new_class_name} em {dataset_name}."

    source_path.rename(destination_path)
    return f"Classe {class_name} renomeada para {new_class_name}."


def delete_image(dataset_name, class_name, filename):
    root = dataset_path(dataset_name)
    class_name = validate_name(class_name, "classe")
    filename = Path(filename or "").name

    if not filename:
        return "Selecione uma imagem."

    image_path = root / class_name / filename
    if not image_path.exists() or not is_image(image_path):
        return f"Imagem {filename} nao encontrada em {dataset_name}/{class_name}."

    image_path.unlink()
    return f"Imagem {filename} removida de {dataset_name}/{class_name}."


def copy_uploaded_file(uploaded_file, destination_dir):
    source_path = Path(uploaded_file)
    destination = destination_dir / source_path.name
    counter = 1

    while destination.exists():
        destination = destination_dir / f"{source_path.stem}_{counter}{source_path.suffix}"
        counter += 1

    shutil.copyfile(source_path, destination)
    return destination


def upload_images(dataset_name, class_name, files):
    if not files:
        return "Selecione uma ou mais imagens."

    root = dataset_path(dataset_name)
    class_name = validate_name(class_name, "classe")
    destination_dir = root / class_name
    destination_dir.mkdir(parents=True, exist_ok=True)

    saved = []
    for file_path in files:
        source_path = Path(file_path)
        if source_path.suffix.lower() not in IMAGE_EXTENSIONS:
            continue
        saved.append(copy_uploaded_file(source_path, destination_dir).name)

    return f"{len(saved)} imagens adicionadas em {dataset_name}/{class_name}."


def parse_video_intervals(interval_rows):
    if hasattr(interval_rows, "values"):
        interval_rows = interval_rows.values.tolist()
    elif isinstance(interval_rows, dict) and "data" in interval_rows:
        interval_rows = interval_rows["data"]

    intervals = []

    for row in interval_rows or []:
        if not row or len(row) < 3:
            continue
        start, end, class_name = row[:3]
        if start in (None, "") or end in (None, "") or not class_name:
            continue

        start = float(start)
        end = float(end)
        class_name = validate_name(class_name, "classe")

        if start < 0 or end < 0 or end < start:
            raise ValueError("Intervalos devem ter inicio/fim positivos e fim maior ou igual ao inicio.")

        intervals.append({"start": start, "end": end, "class": class_name})

    if not intervals:
        raise ValueError("Informe ao menos um intervalo com inicio, fim e classe.")

    return intervals


def extract_frames_from_video(dataset_name, video_path, fps, interval_rows, progress=gr.Progress()):
    if video_path is None:
        return "Selecione um video.", []

    try:
        import cv2
    except ImportError as exc:
        raise RuntimeError(
            "Dependencia ausente: instale opencv-python-headless para extrair frames de video."
        ) from exc

    fps = float(fps or 0)
    if fps <= 0:
        raise ValueError("FPS deve ser maior que zero.")

    if isinstance(video_path, dict):
        video_path = video_path.get("path") or video_path.get("name")

    dataset_name = validate_name(dataset_name, "dataset")
    intervals = parse_video_intervals(interval_rows)
    capture = cv2.VideoCapture(str(video_path))
    if not capture.isOpened():
        raise ValueError("Nao foi possivel abrir o video selecionado.")

    frame_step = 1.0 / fps
    total_frames = sum(int((item["end"] - item["start"]) * fps) + 1 for item in intervals)
    processed = 0
    saved_paths = []

    progress(0, desc="Preparando extracao de frames")

    try:
        for interval in intervals:
            class_dir = dataset_path(dataset_name) / interval["class"]
            class_dir.mkdir(parents=True, exist_ok=True)

            time_seconds = interval["start"]
            while time_seconds <= interval["end"] + 1e-9:
                capture.set(cv2.CAP_PROP_POS_MSEC, time_seconds * 1000)
                success, frame = capture.read()
                if success:
                    timestamp_ms = int(round(time_seconds * 1000))
                    filename = f"frame_{timestamp_ms:08d}.jpg"
                    destination = class_dir / filename
                    counter = 1
                    while destination.exists():
                        destination = class_dir / f"frame_{timestamp_ms:08d}_{counter}.jpg"
                        counter += 1

                    cv2.imwrite(str(destination), frame)
                    saved_paths.append(str(destination))

                processed += 1
                progress(processed / total_frames, desc=f"Extraindo frame {processed}/{total_frames}")
                time_seconds += frame_step
    finally:
        capture.release()

    progress(1, desc="Extracao concluida")
    return f"{len(saved_paths)} frames extraidos para {dataset_name}.", saved_paths


def describe_dataset_images(dataset_name, progress=gr.Progress()):
    init_db(dataset_name)
    clear_descriptors(dataset_name)
    items = dataset_items(dataset_name)

    total = len(items)
    processed = 0

    if total == 0:
        return f"Nenhuma imagem encontrada em {dataset_name}."

    progress(0, desc=f"Preparando descritores de {dataset_name}")

    for index, item in enumerate(items, start=1):
        progress(index / total, desc=f"Processando {index}/{total}: {item['filename']}")

        descriptor = extract_netvlad_descriptor(str(item["path"]))
        save_image_descriptor(item["class"], descriptor, item["path"], dataset_name)
        processed += 1

    progress(1, desc="Descritores gerados")

    database_path = descriptor_database_path(dataset_name)
    return f"Descritores gerados para {processed} imagens de {dataset_name} em {database_path}."
