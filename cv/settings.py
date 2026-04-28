from pathlib import Path


class Settings:
    BASE_DIR = Path(__file__).parent
    PROJECT_ROOT = BASE_DIR.parent

    CONFIG_PATH = PROJECT_ROOT / "config.json"
    VIDEO_SOURCE = BASE_DIR / "public" / "simulation-longer.mp4"
    EMPTY_STATES_DIR = BASE_DIR / "public" / "empty-states"
    YOLO_MODEL = BASE_DIR / "yolov8n.pt"
    # MODE_DEVELOPMENT = True
