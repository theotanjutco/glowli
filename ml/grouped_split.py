import random
from collections import Counter, defaultdict
from pathlib import Path

from ml.prepare_dataset import get_image_classes


def build_groups(images: list[Path], pairs: list[tuple[Path, Path]]) -> list[list[Path]]:
    if len(set(images)) != len(images):
        raise ValueError("Image paths must be unique.")
    parent = {path: path for path in images}

    def find(path: Path) -> Path:
        while parent[path] != path:
            parent[path] = parent[parent[path]]
            path = parent[path]
        return path

    for left, right in pairs:
        if left not in parent or right not in parent:
            raise ValueError("Similarity pair references an unknown image.")
        a, b = find(left), find(right)
        parent[max(a, b)] = min(a, b)

    groups = defaultdict(list)
    for path in sorted(images):
        groups[find(path)].append(path)
    return sorted(groups.values(), key=lambda group: group[0])


def split_groups(groups: list[list[Path]], seed: int = 42) -> dict[str, list[Path]]:
    if not groups or any(not group for group in groups):
        raise ValueError("Groups must be nonempty.")
    images = [path for group in groups for path in group]
    if len(set(images)) != len(images):
        raise ValueError("An image belongs to multiple groups.")
    groups = sorted((sorted(group) for group in groups), key=lambda group: group[0])
    classes = {path: get_image_classes(path) for path in images}
    group_counts = [Counter(c for path in group for c in classes[path]) for group in groups]
    if any(sum(c in counts for counts in group_counts) < 3 for c in range(10)):
        raise ValueError("Every class needs at least three independent groups.")

    ratios = {"train": .70, "valid": .15, "test": .15}
    targets = {"train": round(len(images) * .70), "valid": round(len(images) * .15)}
    targets["test"] = len(images) - sum(targets.values())
    totals = Counter(c for ids in classes.values() for c in ids)
    needed = {name: {c: totals[c] * ratio for c in range(10)} for name, ratio in ratios.items()}
    splits = {name: [] for name in ratios}
    order = list(range(len(groups)))
    random.Random(seed).shuffle(order)
    remaining = dict.fromkeys(order)

    while remaining:
        frequencies = Counter(c for index in remaining for c in group_counts[index])
        rarest = min(frequencies, key=lambda c: (frequencies[c], c)) if frequencies else None
        candidates = [i for i in remaining if rarest is None or rarest in group_counts[i]]
        for index in candidates:
            size = len(groups[index])
            available = [name for name in ratios if len(splits[name]) + size <= targets[name]]
            if not available:
                available = list(ratios)
            destination = max(
                available,
                key=lambda name: (
                    needed[name][rarest] if rarest is not None else 0,
                    targets[name] - len(splits[name]),
                ),
            )
            splits[destination].extend(groups[index])
            for c, count in group_counts[index].items():
                needed[destination][c] -= count
            del remaining[index]

    for name, paths in splits.items():
        present = {c for path in paths for c in classes[path]}
        if present != set(range(10)):
            raise ValueError(f"{name} is missing a class; review grouped assignments.")
    return splits
