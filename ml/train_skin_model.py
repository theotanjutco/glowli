from pathlib import Path

from ultralytics import YOLO


def main() -> None:
    project_root = Path(__file__).resolve().parents[1]
    dataset_config = (
        project_root
        / ".cache"
        / "datasets"
        / "skin-concerns-grouped"
        / "data.yaml"
    )
    if not dataset_config.is_file():
        raise FileNotFoundError(f"Dataset config not found: {dataset_config}")

    model_dir = project_root / ".cache" / "models"
    model_dir.mkdir(parents=True, exist_ok=True)
    model = YOLO(str(model_dir / "yolov8n.pt"))
    model.train(
        data=str(dataset_config),
        epochs=10,
        fraction=1.0,
        imgsz=640,
        batch=4,
        device="cpu",
        workers=0,
        seed=42,
        deterministic=True,
        val=True,
        save=True,
        plots=True,
        project=str(project_root / ".cache" / "training"),
        name="skin_baseline_10",
        exist_ok=False,
    )


if __name__ == "__main__":
    main()
