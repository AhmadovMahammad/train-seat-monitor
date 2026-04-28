import json
import os
from pathlib import Path

import cv2

BASE_DIR = Path(__file__).parent
CONFIG_PATH = BASE_DIR / "config.json"
VIDEO_SOURCE = BASE_DIR / "public" / "simulation-longer.mp4"
EMPTY_STATES_DIR = BASE_DIR / "public" / "empty-states"

os.makedirs(EMPTY_STATES_DIR, exist_ok=True)

with open(CONFIG_PATH) as f:
    config = json.load(f)

for train in config["trains"]:
    for wagon in train["wagons"]:
        for camera in wagon["cameras"]:
            cap = cv2.VideoCapture(str(VIDEO_SOURCE))
            ret, frame = cap.read()
            cap.release()

            if not ret:
                continue

            name = f"{train['id']}_{wagon['id']}_{camera['id']}.png"
            cv2.imwrite(str(EMPTY_STATES_DIR / name), frame)
