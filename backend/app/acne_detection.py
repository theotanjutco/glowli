from functools import lru_cache
from pathlib import Path
from threading import Lock

from PIL import Image
from ultralytics import YOLO


MODEL_PATH = (
    Path(__file__).resolve().parents[2]
    / ".cache" / "training" / "acne_baseline_10" / "weights" / "best.pt"
)

CONFIDENCE_THRESHOLD = 0.25
NMS_THRESHOLD = 0.45

_model_lock = Lock()


@lru_cache(maxsize=1)
def _get_model() -> YOLO:
    if not MODEL_PATH.is_file():
        raise RuntimeError("The acne model file is missing.")

    model = YOLO(str(MODEL_PATH))
    if model.names != {0: "Acne"}:
        raise RuntimeError("Expected a single-class Acne model.")

    return model


def predict_acne(image: Image.Image) -> list[dict]:
    with _model_lock:
        model = _get_model()
        result = model.predict(
            source=image,
            imgsz=640,
            conf=CONFIDENCE_THRESHOLD,
            iou=NMS_THRESHOLD,
            device="cpu",
            save=False,
            verbose=False,
        )[0]

        boxes = result.boxes
        if boxes is None or len(boxes) == 0:
            return []

        coordinates = boxes.xyxyn.cpu().tolist()
        scores = boxes.conf.cpu().tolist()

    return [
        {
            "label": "Acne",
            "confidence": score,
            "box": {
                "x1": corners[0],
                "y1": corners[1],
                "x2": corners[2],
                "y2": corners[3],
            },
        }
        for corners, score in zip(coordinates, scores)
    ]
