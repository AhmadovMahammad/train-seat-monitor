import json
from datetime import datetime
from multiprocessing import Process

import cv2
import pika
from ultralytics import YOLO

from settings import Settings


def publish(channel, train_id, wagon_id, camera_id, seat_id, is_occupied):
    message = json.dumps(
        {
            "train_id": train_id,
            "wagon_id": wagon_id,
            "camera_id": camera_id,
            "seat_id": seat_id,
            "status": "occupied" if is_occupied else "free",
            "timestamp": datetime.now().isoformat(),
        }
    )
    channel.basic_publish(exchange="", routing_key="passenger-seat", body=message)


def process_camera(train_id, wagon_id, camera):
    seats = camera.get("seats", [])
    if not seats:
        return

    model = YOLO(Settings.YOLO_MODEL)

    connection = pika.BlockingConnection(pika.ConnectionParameters("localhost"))
    channel = connection.channel()
    channel.queue_declare(
        queue="passenger-seat", durable=True, arguments={"x-queue-type": "quorum"}
    )

    cap = cv2.VideoCapture(Settings.VIDEO_SOURCE)
    frame_count = 0
    last_status = {}

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame_count += 1

        if frame_count % 5 != 0:
            continue

        for seat in seats:
            (x1, y1), (x2, y2) = seat["coords"]
            cropped = frame[y1:y2, x1:x2]
            results = model.predict(
                source=cropped, classes=[0], conf=0.5, verbose=False
            )
            is_occupied = len(results[0].boxes) > 0

            if last_status.get(seat["id"]) == is_occupied:
                continue

            last_status[seat["id"]] = is_occupied
            publish(channel, train_id, wagon_id, camera["id"], seat["id"], is_occupied)

    cap.release()
    connection.close()


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
