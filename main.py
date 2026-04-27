import json

import cv2
from ultralytics import YOLO

model = YOLO("yolov8n.pt")

with open("roi_data.json") as f:
    roi_coords = json.load(f)

cap = cv2.VideoCapture("simulation-longer.mp4")
fps = cap.get(cv2.CAP_PROP_FPS)
delay = int(1000 / fps)
frame_count = 0
last_results = {}

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    frame_count += 1

    if frame_count % 5 == 0:
        for i in range(0, len(roi_coords), 2):
            x1, y1 = roi_coords[i]
            x2, y2 = roi_coords[i + 1]

            cropped = frame[y1:y2, x1:x2]
            results = model.predict(
                source=cropped, classes=[0], conf=0.5, verbose=False
            )

            is_occupied = len(results[0].boxes) > 0
            last_results[i] = {"occupied": is_occupied, "coords": (x1, y1, x2, y2)}

    for i, result in last_results.items():
        x1, y1, x2, y2 = result["coords"]
        color = (0, 0, 255) if result["occupied"] else (0, 255, 0)
        label = "Occupied" if result["occupied"] else "Free"
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
        cv2.putText(
            frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2
        )

    cv2.imshow("Demo", frame)

    if cv2.waitKey(delay) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
