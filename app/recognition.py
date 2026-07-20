import shutil
from collections import Counter
from pathlib import Path

from config import UPLOAD_DIR
from database import fetch_all_descriptors
from netvlad.NetVLADComparator import NetVLADComparator
from netvlad.utils import extract_netvlad_descriptor


def single_best_match(query_descriptor, dataset_name):
    all_descriptors = fetch_all_descriptors(dataset_name)
    if not all_descriptors:
        raise ValueError("Nenhum descritor encontrado. Gere os descritores do dataset primeiro.")

    best_match_class = None
    best_match_image = None
    best_similarity = float("inf")
    netvlad_comparator = NetVLADComparator()

    for _, descriptor_class, image_path, descriptor in all_descriptors:
        similarity = netvlad_comparator.compare_descriptors(
            query_descriptor,
            descriptor,
            "euclidean",
        )

        if similarity < best_similarity:
            best_similarity = similarity
            best_match_class = descriptor_class
            best_match_image = image_path

    return best_match_class, best_match_image, best_similarity


def multimatch(query_descriptor, dataset_name, top_n=5):
    all_descriptors = fetch_all_descriptors(dataset_name)
    if not all_descriptors:
        raise ValueError("Nenhum descritor encontrado. Gere os descritores do dataset primeiro.")

    netvlad_comparator = NetVLADComparator()
    similarities = []

    for _, descriptor_class, image_path, descriptor in all_descriptors:
        similarity = netvlad_comparator.compare_descriptors(
            query_descriptor,
            descriptor,
            "euclidean",
        )
        similarities.append((similarity, descriptor_class, image_path))

    similarities.sort(key=lambda item: item[0])
    top_matches = similarities[:top_n]
    top_classes = [class_name for _, class_name, _ in top_matches]
    best_match_class = Counter(top_classes).most_common(1)[0][0]

    return best_match_class, top_matches


def save_query_image(image_path):
    UPLOAD_DIR.mkdir(exist_ok=True)
    source_path = Path(image_path)
    destination = UPLOAD_DIR / source_path.name
    shutil.copyfile(source_path, destination)
    return destination


def recognize_place(dataset_name, image_path):
    if not dataset_name:
        return "Selecione um dataset para reconhecer.", None, None, []
    if image_path is None:
        return "Envie uma imagem para reconhecer.", None, None, []

    try:
        query_image_path = save_query_image(image_path)
        descriptor = extract_netvlad_descriptor(str(query_image_path))
        single_class, reference_image, distance = single_best_match(descriptor, dataset_name)
        voting_class, top_matches = multimatch(descriptor, dataset_name)
    except Exception as exc:
        return f"Erro: {exc}", None, None, []

    result = (
        f"Melhor classe: {single_class}\n"
        f"Distancia euclidiana: {distance:.6f}\n"
        f"Classe por top-5: {voting_class}"
    )
    top_table = [[class_name, image_path, float(score)] for score, class_name, image_path in top_matches]

    return result, str(query_image_path), reference_image or None, top_table
