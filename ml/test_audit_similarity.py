import io
import unittest

import numpy as np
from PIL import Image, ImageDraw, ImageOps

from ml.audit_similarity import image_variants, match_variants


def pattern(seed: int) -> Image.Image:
    image = Image.new("RGB", (320, 320), "white")
    draw = ImageDraw.Draw(image)
    rng = np.random.default_rng(seed)
    for _ in range(40):
        x, y = rng.integers(0, 260, size=2)
        color = tuple(int(v) for v in rng.integers(0, 256, size=3))
        draw.rectangle((int(x), int(y), int(x) + 40, int(y) + 55), fill=color)
    return image


class SimilarityTests(unittest.TestCase):
    def setUp(self):
        self.image = pattern(42)
        self.hashes = image_variants(self.image)

    def test_identical(self):
        match = match_variants(self.hashes, self.hashes, 6, 8)
        self.assertEqual((match["phash_distance"], match["dhash_distance"]), (0, 0))

    def test_recompressed_and_resized(self):
        buffer = io.BytesIO()
        self.image.resize((200, 200)).save(buffer, format="JPEG", quality=65)
        buffer.seek(0)
        with Image.open(buffer) as image:
            self.assertIsNotNone(match_variants(self.hashes, image_variants(image), 6, 8))

    def test_mirror_and_center_crop(self):
        for image in (ImageOps.mirror(self.image), self.image.crop((16, 16, 304, 304))):
            self.assertIsNotNone(match_variants(self.hashes, image_variants(image), 6, 8))

    def test_unrelated_pattern(self):
        self.assertIsNone(match_variants(self.hashes, image_variants(pattern(99)), 6, 8))

    def test_both_thresholds_required(self):
        self.assertIsNone(match_variants({"original": (0, 0)}, {"original": (0, 511)}, 6, 8))
        self.assertIsNone(match_variants({"original": (0, 0)}, {"original": (127, 0)}, 6, 8))


if __name__ == "__main__":
    unittest.main()
