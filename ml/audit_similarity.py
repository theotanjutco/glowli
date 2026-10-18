import argparse
import json
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageOps


def pack_bits(bits: np.ndarray) -> int:
    return int.from_bytes(np.packbits(bits.reshape(-1)).tobytes(), "big")


def fingerprints(image: Image.Image) -> tuple[int, int]:
    gray = image.convert("L")
    small = np.asarray(gray.resize((32, 32), Image.Resampling.LANCZOS), dtype=np.float32)
    coefficients = cv2.dct(small)[:8, :8].reshape(-1)[1:]
    phash = pack_bits(coefficients > np.median(coefficients))
    gradient = np.asarray(gray.resize((9, 8), Image.Resampling.LANCZOS))
    dhash = pack_bits(gradient[:, 1:] > gradient[:, :-1])
    return phash, dhash


def image_variants(image: Image.Image) -> dict[str, tuple[int, int]]:
    width, height = image.size
    crop = image.crop((width * .05, height * .05, width * .95, height * .95))
    return {
        "original": fingerprints(image),
        "mirrored": fingerprints(ImageOps.mirror(image)),
        "center_crop_90": fingerprints(crop),
    }


def match_variants(left: dict, right: dict, phash_limit: int, dhash_limit: int):
    matches = []
    for left_name, (lp, ld) in left.items():
        for right_name, (rp, rd) in right.items():
            if left_name != "original" and right_name != "original":
                continue
            pd, dd = (lp ^ rp).bit_count(), (ld ^ rd).bit_count()
            if pd <= phash_limit and dd <= dhash_limit:
                matches.append((pd + dd, pd, dd, left_name, right_name))
    if not matches:
        return None
    _, pd, dd, left_name, right_name = min(matches)
    return {"phash_distance": pd, "dhash_distance": dd,
            "left_variant": left_name, "right_variant": right_name}


def audit_dataset(dataset_dir: Path, output_dir: Path,
                  phash_limit: int = 6, dhash_limit: int = 8) -> dict:
    if not 0 <= phash_limit <= 63 or not 0 <= dhash_limit <= 64:
        raise ValueError("Invalid hash distance threshold.")
    output_dir.mkdir(parents=True, exist_ok=False)
    records = []
    for split in ("train", "valid", "test"):
        paths = sorted((dataset_dir / split / "images").glob("*.jpg"))
        if not paths:
            raise ValueError(f"No images in {split}.")
        for path in paths:
            with Image.open(path) as image:
                records.append((path, split, image_variants(ImageOps.exif_transpose(image))))
        print(f"Fingerprinted {split}: {len(paths)} images", flush=True)

    pairs = []
    for index, (left, left_split, left_hashes) in enumerate(records):
        for right, right_split, right_hashes in records[index + 1:]:
            match = match_variants(left_hashes, right_hashes, phash_limit, dhash_limit)
            if match is not None:
                pairs.append({"left": left.relative_to(dataset_dir).as_posix(),
                              "right": right.relative_to(dataset_dir).as_posix(),
                              "cross_split": left_split != right_split, **match})
    pairs.sort(key=lambda p: (not p["cross_split"],
                              p["phash_distance"] + p["dhash_distance"],
                              p["left"], p["right"]))
    for index, pair in enumerate(pairs, 1):
        pair["id"] = index
    cross = [pair for pair in pairs if pair["cross_split"]]
    review = cross
    sheets = []
    for start in range(0, len(review), 6):
        sheet = Image.new("RGB", (1000, 900), "white")
        draw = ImageDraw.Draw(sheet)
        for slot, pair in enumerate(review[start:start + 6]):
            x, y = (slot % 2) * 500, (slot // 2) * 300
            draw.text((x + 5, y + 5),
                      f"Pair {pair['id']} | p={pair['phash_distance']} d={pair['dhash_distance']}",
                      fill="black")
            for column, side in enumerate(("left", "right")):
                with Image.open(dataset_dir / pair[side]) as image:
                    thumb = ImageOps.contain(image.convert("RGB"), (240, 240))
                    sheet.paste(thumb, (x + column * 250, y + 30))
                draw.text((x + column * 250 + 5, y + 275),
                          pair[side].split("/")[0], fill="black")
        filename = f"review-{start // 6 + 1:02d}.jpg"
        sheet.save(output_dir / filename)
        sheets.append(filename)
    report = {
        "images": len(records), "phash_limit": phash_limit, "dhash_limit": dhash_limit,
        "candidate_pairs": len(pairs), "cross_split_candidate_pairs": len(cross),
        "review_sheet_pairs": len(review), "sheets": sheets, "pairs": pairs,
        "limitations": "Candidates require visual review. Hashes can miss crops, edits, "
                        "or different photos of the same person. No files were removed.",
    }
    (output_dir / "similarity_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("dataset_dir", type=Path)
    parser.add_argument("output_dir", type=Path)
    args = parser.parse_args()
    report = audit_dataset(args.dataset_dir, args.output_dir)
    print(json.dumps({key: value for key, value in report.items() if key != "pairs"}, indent=2))
