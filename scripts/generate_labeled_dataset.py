#!/usr/bin/env python3
import argparse
from pathlib import Path


CLASS_RANGES = {
    "bancadas_a": [
        (0, 186),
        (651, 836),
    ],
    "bancadas_b": [
        (187, 481),
        (876, 1271),
    ],
    "corredor": [
        (191, 206),
        (456, 876),
        (831, 876),
        (1246, 1346),
    ],
    "armarios": [
        (1351, 1746),
        (2216, 2291),
    ],
    "porta": [
        (1751, 2211),
    ],
}


def frame_number(filename):
    return int(filename[5:10])


def resolve_image_class(filename):
    number = frame_number(filename)
    resolved_class = None

    for class_name, ranges in CLASS_RANGES.items():
        for minimum, maximum in ranges:
            if minimum <= number <= maximum:
                resolved_class = class_name
                break

    if resolved_class is None:
        raise ValueError(f"No class range found for {filename}.")

    return resolved_class


def generate_labeled_dataset(dataset_dir):
    frame_files = sorted(path.name for path in dataset_dir.iterdir() if path.name.startswith("frame"))

    rows = []
    for filename in frame_files:
        rows.append(f"{filename};{resolve_image_class(filename)};")

    return "\r\n".join(rows) + "\r\n"


def parse_args():
    parser = argparse.ArgumentParser(description="Generate dataset/labeled_dataset.csv from frame filenames.")
    parser.add_argument(
        "--dataset-dir",
        default="dataset",
        type=Path,
        help="Directory containing frame images.",
    )
    parser.add_argument(
        "--output",
        default=None,
        type=Path,
        help="CSV output path. Defaults to <dataset-dir>/labeled_dataset.csv.",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    dataset_dir = args.dataset_dir
    output = args.output or dataset_dir / "labeled_dataset.csv"

    output.write_text(generate_labeled_dataset(dataset_dir), encoding="utf-8", newline="")
    print(f"Wrote {output}")


if __name__ == "__main__":
    main()
