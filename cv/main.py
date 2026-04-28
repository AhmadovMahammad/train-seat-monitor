import json
from multiprocessing import Process

import cv2
from ultralytics import YOLO

from settings import Settings


def process_camera(train_id, wagon_id, camera):
    model = YOLO(Settings.YOLO_MODEL)
    seats = camera.get("seats", [])
    if not seats:
        return

    cap = cv2.VideoCapture(Settings.VIDEO_SOURCE)
    fps = cap.get(cv2.CAP_PROP_FPS)
    delay = int(1000 / fps)

    window_name = f"{train_id} | {wagon_id} | {camera['id']}"
    frame_count = 0
    last_results = {}

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
                is_occupied = len(results[0].boxes) > 0
                last_results[seat["id"]] = {
                    "occupied": is_occupied,
                    "coords": (x1, y1, x2, y2),
                }

        for seat_id, result in last_results.items():
            x1, y1, x2, y2 = result["coords"]
            color = (0, 0, 255) if result["occupied"] else (0, 255, 0)
            status = "Occupied" if result["occupied"] else "Free"
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            cv2.putText(
                frame,
                f"{seat_id}: {status}",
                (x1, y1 - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                color,
                2,
            )

        cv2.imshow(window_name, frame)

        if cv2.waitKey(delay) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    with open(Settings.CONFIG_PATH) as f:
        config = json.load(f)

    processes = []
    for train in config["trains"]:
        for wagon in train["wagons"]:
            for camera in wagon["cameras"]:
                p = Process(
                    target=process_camera, args=(train["id"], wagon["id"], camera)
                )
                processes.append(p)
                p.start()

    for p in processes:
        p.join()
