import hashlib
import json
import math
import random
import shutil
from collections import Counter, defaultdict
from pathlib import Path
from zipfile import ZipFile


def polygon_to_box(line: str) -> str:
    values = [float(value) for value in line.split()]

    if len(values) != 9:
        raise ValueError("Expected a class ID and four coordinate pairs.")

    if not all(math.isfinite(value) for value in values):
        raise ValueError("Annotation contains a non-finite number.")

    class_id = values[0]
    if not class_id.is_integer() or not 0 <= class_id < 10:
        raise ValueError("Class ID must be an integer from 0 to 9.")

    xs = values[1::2]
    ys = values[2::2]

    left = max(0.0, min(1.0, min(xs)))
    right = max(0.0, min(1.0, max(xs)))
    top = max(0.0, min(1.0, min(ys)))
    bottom = max(0.0, min(1.0, max(ys)))

    width = right - left
    height = bottom - top

    if width <= 0 or height <= 0:
        raise ValueError("Annotation has no usable area inside the image.")

    center_x = (left + right) / 2
    center_y = (top + bottom) / 2

    return (
        f"{int(class_id)} "
        f"{center_x:.8f} {center_y:.8f} "
        f"{width:.8f} {height:.8f}"
    )


def convert_dataset(source_zip: Path, output_dir: Path) -> dict:
    output_dir.mkdir(parents=True, exist_ok=False)

    report = {
        "converted_annotations": 0,
        "clipped_annotations": [],
        "rejected_annotations": [],
    }

    with ZipFile(source_zip) as archive:
        for member in archive.infolist():
            if member.is_dir():
                continue

            relative_path = Path(member.filename)
            destination = (output_dir / relative_path).resolve()

            if not destination.is_relative_to(output_dir.resolve()):
                raise ValueError("ZIP contains a path outside the output folder.")

            destination.parent.mkdir(parents=True, exist_ok=True)

            is_label = (
                len(relative_path.parts) == 3
                and relative_path.parts[0] in {"train", "valid", "test"}
                and relative_path.parts[1] == "labels"
                and relative_path.suffix == ".txt"
            )

            if not is_label:
                destination.write_bytes(archive.read(member))
                continue

            converted = []

            for line_number, line in enumerate(
                archive.read(member).decode("utf-8").splitlines(),
                start=1,
            ):
                if not line.strip():
                    continue

                try:
                    box = polygon_to_box(line)
                except ValueError as error:
                    report["rejected_annotations"].append({
                        "file": member.filename,
                        "line": line_number,
                        "annotation": line,
                        "reason": str(error),
                    })
                    continue

                coordinates = [float(value) for value in line.split()[1:]]

                if any(value < 0 or value > 1 for value in coordinates):
                    report["clipped_annotations"].append({
                        "file": member.filename,
                        "line": line_number,
                        "original": line,
                        "converted": box,
                    })

                converted.append(box)
                report["converted_annotations"] += 1

            destination.write_text(
                "\n".join(converted) + ("\n" if converted else ""),
                encoding="utf-8",
            )

    (output_dir / "conversion_report.json").write_text(
        json.dumps(report, indent=2),
        encoding="utf-8",
    )

    return report


def select_unique_images(dataset_dir: Path) -> tuple[list[Path], dict]:
    groups = defaultdict(list)

    for split in ("train", "valid", "test"):
        for image_path in sorted(
            (dataset_dir / split / "images").glob("*.jpg")
        ):
            digest = hashlib.sha256(image_path.read_bytes()).hexdigest()
            groups[digest].append(image_path)

    selected = []
    excluded_groups = []

    for digest, image_paths in groups.items():
        if len(image_paths) == 1:
            selected.append(image_paths[0])
            continue

        excluded_groups.append({
            "sha256": digest,
            "images": [
                path.relative_to(dataset_dir).as_posix()
                for path in image_paths
            ],
            "reason": "Duplicate image group excluded pending label review.",
        })

    report = {
        "selected_images": len(selected),
        "excluded_images": sum(
            len(group["images"]) for group in excluded_groups
        ),
        "excluded_groups": excluded_groups,
    }

    return selected, report


def get_image_classes(image_path: Path) -> set[int]:
    label_path = (
        image_path.parent.parent / "labels" / f"{image_path.stem}.txt"
    )

    classes = set()

    for line in label_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue

        class_id = int(line.split()[0])
        classes.add(class_id)

    return classes


def split_images(
    images: list[Path],
    seed: int = 42,
) -> dict[str, list[Path]]:
    if len(images) != len(set(images)):
        raise ValueError("Image paths must be unique.")

    ratios = {"train": 0.70, "valid": 0.15, "test": 0.15}
    classes = {path: get_image_classes(path) for path in images}
    totals = Counter(
        class_id for ids in classes.values() for class_id in ids
    )

    if any(totals[class_id] < 3 for class_id in range(10)):
        raise ValueError("Each class needs at least three images.")

    targets = {
        "train": round(len(images) * ratios["train"]),
        "valid": round(len(images) * ratios["valid"]),
    }
    targets["test"] = len(images) - sum(targets.values())
    needed = {
        name: {
            class_id: totals[class_id] * ratio
            for class_id in range(10)
        }
        for name, ratio in ratios.items()
    }
    splits = {name: [] for name in ratios}
    ordered = sorted(images)
    random.Random(seed).shuffle(ordered)
    remaining = dict.fromkeys(ordered)

    while remaining:
        remaining_counts = Counter(
            class_id
            for path in remaining
            for class_id in classes[path]
        )

        if not remaining_counts:
            for path in remaining:
                destination = max(
                    ratios,
                    key=lambda name: targets[name] - len(splits[name]),
                )
                splits[destination].append(path)
            break

        rarest = min(
            remaining_counts,
            key=lambda class_id: (remaining_counts[class_id], class_id),
        )
        candidates = [
            path for path in remaining
            if rarest in classes[path]
        ]

        for path in candidates:
            available = [
                name for name in ratios
                if len(splits[name]) < targets[name]
            ]
            destination = max(
                available,
                key=lambda name: (
                    needed[name][rarest],
                    targets[name] - len(splits[name]),
                ),
            )
            splits[destination].append(path)

            for class_id in classes[path]:
                needed[destination][class_id] -= 1

            del remaining[path]

    for name, paths in splits.items():
        present = {
            class_id for path in paths for class_id in classes[path]
        }
        if present != set(range(10)):
            raise ValueError(f"{name} is missing a class; review the split.")

    return splits


def export_dataset(
    source_dir: Path,
    splits: dict[str, list[Path]],
    output_dir: Path,
) -> None:
    expected_splits = {"train", "valid", "test"}
    if set(splits) != expected_splits:
        raise ValueError("Expected train, valid, and test splits.")

    source_dir = source_dir.resolve()
    jobs = []
    seen = set()

    for split, image_paths in splits.items():
        if not image_paths:
            raise ValueError(f"{split} has no images.")

        for image_path in image_paths:
            image_path = image_path.resolve()
            relative = image_path.relative_to(source_dir)
            if (
                len(relative.parts) != 3
                or relative.parts[0] not in expected_splits
                or relative.parts[1] != "images"
                or image_path.suffix.lower() != ".jpg"
            ):
                raise ValueError(f"Unexpected image path: {image_path}")

            if image_path in seen:
                raise ValueError(f"Repeated image: {image_path}")
            seen.add(image_path)

            label_path = (
                image_path.parent.parent
                / "labels"
                / f"{image_path.stem}.txt"
            )
            if not image_path.is_file() or not label_path.is_file():
                raise FileNotFoundError(f"Missing image or label: {image_path}")

            export_stem = f"{relative.parts[0]}_{image_path.stem}"
            jobs.append((split, image_path, label_path, export_stem))

    retained_files = (
        "README.dataset.txt",
        "README.roboflow.txt",
        "conversion_report.json",
    )
    for filename in retained_files:
        if not (source_dir / filename).is_file():
            raise FileNotFoundError(f"Missing source record: {filename}")

    output_dir.mkdir(parents=True, exist_ok=False)
    output_dir = output_dir.resolve()
    for split in splits:
        (output_dir / split / "images").mkdir(parents=True)
        (output_dir / split / "labels").mkdir()

    manifest = {split: [] for split in splits}
    for split, image_path, label_path, export_stem in jobs:
        image_name = f"{export_stem}.jpg"
        shutil.copy2(
            image_path,
            output_dir / split / "images" / image_name,
        )
        shutil.copy2(
            label_path,
            output_dir / split / "labels" / f"{export_stem}.txt",
        )
        manifest[split].append({
            "source": image_path.relative_to(source_dir).as_posix(),
            "image": f"{split}/images/{image_name}",
            "label": f"{split}/labels/{export_stem}.txt",
        })

    for filename in retained_files:
        shutil.copy2(source_dir / filename, output_dir / filename)

    names = [
        "Acne", "Blackheads", "Dark-Spots", "Dry-Skin",
        "Englarged-Pores", "Eyebags", "Oily-Skin",
        "Skin-Redness", "Whiteheads", "Wrinkles",
    ]
    config = [
        f"path: {json.dumps(output_dir.as_posix())}",
        "train: train/images",
        "val: valid/images",
        "test: test/images",
        "names:",
    ]
    config.extend(
        f"  {class_id}: {name}"
        for class_id, name in enumerate(names)
    )
    (output_dir / "data.yaml").write_text(
        "\n".join(config) + "\n",
        encoding="utf-8",
    )
    (output_dir / "export_manifest.json").write_text(
        json.dumps(manifest, indent=2),
        encoding="utf-8",
    )
