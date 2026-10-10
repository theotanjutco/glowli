from functools import lru_cache
from pathlib import Path
from threading import Lock

import cv2
import numpy as np
from PIL import Image


MODEL_PATH = (
    Path(__file__).resolve().parents[1]
    / "models"
    / "face_detection_yunet_2023mar.onnx"
)

MAX_DETECTION_SIZE = 640
SCORE_THRESHOLD = 0.9
NMS_THRESHOLD = 0.3

_detector_lock = Lock()


@lru_cache(maxsize=1)
def _get_detector():
    if not MODEL_PATH.is_file():
        raise RuntimeError("The YuNet model file is missing.")

    return cv2.FaceDetectorYN.create(
        model=str(MODEL_PATH),
        config="",
        input_size=(320, 320),
        score_threshold=SCORE_THRESHOLD,
        nms_threshold=NMS_THRESHOLD,
        top_k=5000,
    )


def count_faces(image: Image.Image) -> int:
    detection_image = image.copy()
    detection_image.thumbnail(
        (MAX_DETECTION_SIZE, MAX_DETECTION_SIZE),
        Image.Resampling.LANCZOS,
    )

    rgb_pixels = np.asarray(detection_image)
    bgr_pixels = cv2.cvtColor(rgb_pixels, cv2.COLOR_RGB2BGR)

    height, width = bgr_pixels.shape[:2]

    with _detector_lock:
        detector = _get_detector()
        detector.setInputSize((width, height))
        _, faces = detector.detect(bgr_pixels)

    return 0 if faces is None else len(faces)
