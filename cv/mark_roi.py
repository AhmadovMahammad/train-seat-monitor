import json

import cv2

from settings import Settings

with open(Settings.CONFIG_PATH) as f:
    config = json.load(f)

for train in config["trains"]:
    for wagon in train["wagons"]:
        for camera in wagon["cameras"]:
            name = f"{train['id']}_{wagon['id']}_{camera['id']}.png"
            img = cv2.imread(str(Settings.EMPTY_STATES_DIR / name))

            roi_coords = []
            seats = []

            def mouse_click(event, x, y, _, __):
                if event != cv2.EVENT_LBUTTONDOWN:
                    return

                roi_coords.append((x, y))

                if len(roi_coords) % 2 != 0:
                    return

                x1 = min(roi_coords[-2][0], roi_coords[-1][0])
                y1 = min(roi_coords[-2][1], roi_coords[-1][1])
                x2 = max(roi_coords[-2][0], roi_coords[-1][0])
                y2 = max(roi_coords[-2][1], roi_coords[-1][1])

                roi_coords[-2] = (x1, y1)
                roi_coords[-1] = (x2, y2)

                seat_id = f"seat_{len(seats) + 1}"
                seats.append({"id": seat_id, "coords": [[x1, y1], [x2, y2]]})

                cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(
                    img,
                    seat_id,
                    (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (0, 255, 0),
                    2,
                )
                cv2.imshow(name, img)

            cv2.imshow(name, img)
            cv2.setMouseCallback(name, mouse_click)
            cv2.waitKey(0)
            cv2.destroyAllWindows()

            camera["seats"] = seats

with open(Settings.CONFIG_PATH, "w") as f:
    json.dump(config, f, indent=2)
