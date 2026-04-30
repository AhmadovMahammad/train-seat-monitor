import json

import cv2
from ultralytics import YOLO

from settings import Settings

with open(Settings.CONFIG_PATH) as f:
    config = json.load(f)

train = config["trains"][0]
wagon = train["wagons"][0]
camera = wagon["cameras"][0]
seats = camera.get("seats", [])

model = YOLO(Settings.YOLO_MODEL)
cap = cv2.VideoCapture(Settings.VIDEO_SOURCE)
fps = cap.get(cv2.CAP_PROP_FPS)
delay = int(1000 / fps)

w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
out = cv2.VideoWriter("output.mp4", cv2.VideoWriter_fourcc(*"mp4v"), fps, (w, h))

frame_count = 0
last_status = {}

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    frame_count += 1

    if frame_count % 5 == 0:
        for seat in seats:
            (x1, y1), (x2, y2) = seat["coords"]
            cropped = frame[y1:y2, x1:x2]
            results = model.predict(
                source=cropped, classes=[0], conf=0.5, verbose=False
            )
            last_status[seat["id"]] = len(results[0].boxes) > 0

    for seat in seats:
        (x1, y1), (x2, y2) = seat["coords"]
        is_occupied = last_status.get(seat["id"], False)
        color = (0, 0, 255) if is_occupied else (0, 255, 0)
        label = "Occupied" if is_occupied else "Free"
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
        cv2.putText(
            frame,
            f"{seat['id']}: {label}",
            (x1, y1 - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            color,
            2,
        )

    out.write(frame)
    cv2.imshow("Seat Monitor", frame)
    if cv2.waitKey(delay) & 0xFF == ord("q"):
        break

cap.release()
out.release()
cv2.destroyAllWindows()
