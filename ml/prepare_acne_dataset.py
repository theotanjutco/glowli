import json
import shutil
from pathlib import Path


def select_acne_candidates(dataset_dir: Path) -> tuple[dict, dict]:
    selected = {}
    report = {}

    for split in ("train", "valid"):
        images = []
        acne_boxes = 0
        excluded_images = 0
        label_dir = dataset_dir / split / "labels"

        for label_path in sorted(label_dir.glob("*.txt")):
            rows = label_path.read_text(encoding="utf-8").splitlines()
            acne_rows = [
                row for row in rows
                if row.strip() and int(row.split()[0]) == 0
            ]

            if not acne_rows:
                excluded_images += 1
                continue

            image_path = (
                dataset_dir / split / "images" / f"{label_path.stem}.jpg"
            )
            if not image_path.is_file():
                raise FileNotFoundError(image_path)

            images.append(image_path)
            acne_boxes += len(acne_rows)

        if not images:
            raise ValueError(f"No acne candidates found in {split}")

        selected[split] = images
        report[split] = {
            "candidate_images": len(images),
            "acne_boxes": acne_boxes,
            "excluded_images": excluded_images,
        }

    return selected, report


def export_acne_dataset(source_dir: Path, output_dir: Path) -> dict:
    source_dir = source_dir.resolve()
    output_dir = output_dir.resolve()

    if output_dir.exists():
        raise FileExistsError(f"Output already exists: {output_dir}")

    selected, counts = select_acne_candidates(source_dir)
    jobs = []

    for split, image_paths in selected.items():
        for image_path in image_paths:
            label_path = (
                image_path.parent.parent / "labels" / f"{image_path.stem}.txt"
            )
            rows = label_path.read_text(encoding="utf-8").splitlines()
            acne_rows = [
                row for row in rows
                if row.strip() and int(row.split()[0]) == 0
            ]

            if not acne_rows:
                raise ValueError(f"Acne annotations missing: {label_path}")

            jobs.append((split, image_path, acne_rows))

    attribution_files = ("README.dataset.txt", "README.roboflow.txt")
    for filename in attribution_files:
        if not (source_dir / filename).is_file():
            raise FileNotFoundError(source_dir / filename)

    output_dir.mkdir(parents=True, exist_ok=False)
    for split in selected:
        (output_dir / split / "images").mkdir(parents=True)
        (output_dir / split / "labels").mkdir()

    manifest = []
    for split, image_path, acne_rows in jobs:
        image_target = output_dir / split / "images" / image_path.name
        label_target = output_dir / split / "labels" / f"{image_path.stem}.txt"
        shutil.copy2(image_path, image_target)
        label_target.write_text("\n".join(acne_rows) + "\n", encoding="utf-8")
        manifest.append({
            "source": image_path.relative_to(source_dir).as_posix(),
            "image": image_target.relative_to(output_dir).as_posix(),
            "label": label_target.relative_to(output_dir).as_posix(),
        })

    for filename in attribution_files:
        shutil.copy2(source_dir / filename, output_dir / filename)

    config = [
        f"path: {json.dumps(output_dir.as_posix())}",
        "train: train/images",
        "val: valid/images",
        "names:",
        "  0: Acne",
    ]
    (output_dir / "data.yaml").write_text(
        "\n".join(config) + "\n", encoding="utf-8"
    )

    report = {
        "source_dataset": source_dir.as_posix(),
        "selection": "Images with class-0 annotations; only class-0 boxes retained.",
        "limitation": "Positive-only subset; no verified acne-free negatives.",
        "counts": counts,
        "images": manifest,
    }
    (output_dir / "export_manifest.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    return report
