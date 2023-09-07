import numpy as np
import cv2


class GridSeg:
    def __init__(self, bboxes, grid_size, im_shape):
        self.bboxes = []
        self.w_resize_factor = im_shape[0] / im_shape[1]

        # squaring
        for bbox in bboxes:
            x, y, w, h = bbox
            self.bboxes.append(
                (
                    int(x * self.w_resize_factor),
                    int(y),
                    int(w * self.w_resize_factor),
                    int(h),
                )
            )

        self.grid_size = grid_size
        self.im_shape = im_shape
        self.square_size = int(im_shape[0] / grid_size)
        self.grid = np.zeros((self.grid_size, self.grid_size))
        self.grid_max_value = 0
        self._compute_grid()

    def _compute_grid(self):
        for bbox in self.bboxes:
            x, y, w, h = bbox
            x1 = int(x / self.square_size)
            y1 = int(y / self.square_size)
            x2 = int((x + w) / self.square_size)
            y2 = int((y + h) / self.square_size)

            self.grid[y1:y2, x1:x2] += 1

        self.grid_max_value = np.max(self.grid)

    def draw_grid(self):
        img = np.zeros((self.grid_size, self.grid_size, 3), dtype=np.uint8)

        for y in range(self.grid_size):
            for x in range(self.grid_size):
                img[y, x, :] = self.grid[y, x] / self.grid_max_value * 255

        return img

    def get_regions(self):
        img = self.draw_grid()
        img = cv2.dilate(img, np.ones((3, 3), dtype=np.uint8), None, iterations=1)
        img = cv2.erode(img, np.ones((3, 3), dtype=np.uint8), None, iterations=1)
        binary = cv2.threshold(
            cv2.cvtColor(img, cv2.COLOR_BGR2GRAY),
            0,
            255,
            cv2.THRESH_BINARY | cv2.THRESH_OTSU,
        )[1]
        contours = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contours = contours[0]

        meta_bboxes = []

        for cnt in contours:
            (x, y, w, h) = cv2.boundingRect(cnt)
            meta_bboxes.append(
                (
                    int(x * self.square_size * 1 / self.w_resize_factor),
                    int(y * self.square_size),
                    int(w * self.square_size * 1 / self.w_resize_factor),
                    int(h * self.square_size),
                )
            )

        return meta_bboxes

    def intersects(self, bbox1, bbox2):
        x1, y1, w1, h1 = bbox1
        x2, y2, w2, h2 = bbox2

        return x1 <= x2 + w2 and x2 <= x1 + w1 and y1 <= y2 + h2 and y2 <= y1 + h1

    # entries is a list of  dicts
    # entry = {
    #     "x": box["x"],
    #     "y": box["y"],
    #     "w": box["w"],
    #     "h": box["h"],
    #     "text": ocrResult,
    #     "conf": conf,
    # }
    def final(self, entries):
        regions = self.get_regions()
        final = []
        for region in regions:
            x, y, w, h = region
            final.append({})
            final[-1]["x"] = x
            final[-1]["y"] = y
            final[-1]["w"] = w
            final[-1]["h"] = h
            final[-1]["text"] = ""
            for entry in entries:
                bbox = (entry["x"], entry["y"], entry["w"], entry["h"])
                if self.intersects(region, bbox):
                    final[-1]["text"] += entry["text"] + " "
        
        return final


# bboxes = pickle.load(open("bboxes.pkl", "rb"))
# gs = GridSeg(bboxes, 100, (1080, 1920))
# regions = gs.get_regions()
# img = cv2.imread("0.png")
# for region in regions:
#     x, y, w, h = region
#     print(region)
#     img = cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
# cv2.imshow("region", img)
# img = gs.draw_grid()
# cv2.imshow("ROI", cv2.resize(img, (500, 500)))
# cv2.waitKey(0)
