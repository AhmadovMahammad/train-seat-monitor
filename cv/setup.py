import json
import os

import cv2

from settings import Settings

os.makedirs(Settings.EMPTY_STATES_DIR, exist_ok=True)

with open(Settings.CONFIG_PATH) as f:
    config = json.load(f)

for train in config["trains"]:
    for wagon in train["wagons"]:
        for camera in wagon["cameras"]:
            cap = cv2.VideoCapture(str(Settings.VIDEO_SOURCE))
            ret, frame = cap.read()
            cap.release()

            if not ret:
                continue

            name = f"{train['id']}_{wagon['id']}_{camera['id']}.png"
            cv2.imwrite(str(Settings.EMPTY_STATES_DIR / name), frame)
