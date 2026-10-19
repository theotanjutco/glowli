from pathlib import Path

from ultralytics import YOLO


def main() -> None:
    project_root = Path(__file__).resolve().parents[1]
    dataset_config = (
        project_root / ".cache" / "datasets" / "acne-only-v1" / "data.yaml"
    )
    weights_path = project_root / ".cache" / "models" / "yolov8n.pt"
    training_dir = project_root / ".cache" / "training"
    run_name = "acne_baseline_10"

    if not dataset_config.is_file():
        raise FileNotFoundError(f"Dataset config not found: {dataset_config}")

    if not weights_path.is_file():
        raise FileNotFoundError(f"Pretrained weights not found: {weights_path}")

    if (training_dir / run_name).exists():
        raise FileExistsError(
            f"Training run already exists: {training_dir / run_name}"
        )

    model = YOLO(str(weights_path))
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
        project=str(training_dir),
        name=run_name,
        exist_ok=False,
    )


if __name__ == "__main__":
    main()
