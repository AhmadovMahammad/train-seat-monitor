import json

import cv2

img = cv2.imread("empty-state.png")
roi_coords = []


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

    cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
    cv2.imshow("image", img)


cv2.imshow("image", img)
cv2.setMouseCallback("image", mouse_click)
cv2.waitKey(0)

with open("roi_data.json", "w") as f:
    json.dump(roi_coords, f)

cv2.destroyAllWindows()
