import cv2
import numpy as np
import pickle


class XYCut:
    def __init__(self, bboxes, im):
        self.bboxes = bboxes
        self.im = im
        self.tree = None

    def cut(self, max_depth=2, debug=False):
        self.tree = self._recursive_xy_cut(
            (0, 0, self.im.shape[1], self.im.shape[0]),
            max_depth=max_depth,
            debug=debug,
        )

    def draw_bboxes(self, blank):
        for bbox in self.bboxes:
            blank = cv2.rectangle(
                blank,
                (bbox[0], bbox[1]),
                (bbox[0] + bbox[2], bbox[1] + bbox[3]),
                (255, 255, 255),
                1,
            )
        return blank

    def draw_profiles(self, blank, crop):
        hp, vp = self._compute_profiles(crop)
        hp *= 10
        vp *= 10
        x, y, w, h = crop

        for i, p in enumerate(hp):
            blank[y + i, x + w - p : x + w] = (255, 255, 255)

        for i, p in enumerate(vp):
            blank[y + h - p : y + h, i + x] = (255, 255, 255)

        return blank

    def draw(self, im, level, debug=False):
        return self._draw_tree(im, self.tree, level, debug=debug)

    def _draw_tree(self, im, tree, level, d=0, debug=False):
        crop = tree[d]["crop"]

        if d == level:
            crop_area = crop[2] * crop[3]
            print(crop_area)
            if crop_area < 40000:
                return im
            im = cv2.rectangle(
                im,
                (crop[0], crop[1]),
                (crop[0] + crop[2], crop[1] + crop[3]),
                (0, 255, 0),
                1,
            )   

            if debug:
                print("akkk")
                cv2.imshow("debug", im)
                cv2.waitKey(0)

            return im

        if "c1" in tree[d]:
            im = self._draw_tree(im, tree[d]["c1"], level, d=d + 1, debug=debug)

        if "c2" in tree[d]:
            im = self._draw_tree(im, tree[d]["c2"], level, d=d + 1, debug=debug)

        if "c3" in tree[d]:
            im = self._draw_tree(im, tree[d]["c3"], level, d=d + 1, debug=debug)

        if "c4" in tree[d]:
            im = self._draw_tree(im, tree[d]["c4"], level, d=d + 1, debug=debug)

        return im

    def _bbox_in_crop(self, bbox, crop):
        # crop : (x, y, w, h)
        x, y, w, h = bbox
        x2 = x + w
        y2 = y + h

        return (
            x >= crop[0]
            and x2 <= crop[0] + crop[2]
            and y >= crop[1]
            and y2 <= crop[1] + crop[3]
        )

    def _bbox_intersects_crop(self, bbox, crop):
        # crop : (x, y, w, h)
        x, y, w, h = bbox
        x2 = x + w
        y2 = y + h

        return (
            x <= crop[0] + crop[2]
            and x2 >= crop[0]
            and y <= crop[1] + crop[3]
            and y2 >= crop[1]
        )

    def _compute_profiles(self, crop):
        # crop : (x, y, w, h)

        hp = np.zeros((crop[3]), np.uint8)
        vp = np.zeros((crop[2]), np.uint8)

        for bbox in self.bboxes:
            if not self._bbox_intersects_crop(bbox, crop):
                continue
            x, y, w, h = bbox
            x = x - crop[0]
            y = y - crop[1]

            hp[y : y + h] += 1
            vp[x : x + w] += 1

        return hp, vp

    # Find the biggest valley and return its index in profile
    def _profile_cut(self, profile):
        vws = len(profile) // 30  # valley window size
        if vws < 3:
            return None, None

        kernel = cv2.getGaussianKernel(vws, 1)

        min_val = 100000000
        min_idx = 0
        for i in range(vws, len(profile) - vws):
            window = profile[i - vws : i]

            res = sum(sum(window * kernel))
            if res < min_val:
                min_val = res
                min_idx = i

        return min_idx, min_val / vws

    def _recursive_xy_cut(self, crop, d=0, max_depth=2, debug=False):
        hp, vp = self._compute_profiles(crop)
        tree = {}
        tree[d] = {}
        tree[d]["crop"] = crop

        if d == max_depth:
            print("max depth reached", d)
            return tree

        xcut, xval = self._profile_cut(vp)
        ycut, yval = self._profile_cut(hp)

        if xcut is None or ycut is None:
            print("no cut found", d)
            return tree

        if debug:
            print("x_valley_score", xval)
            print("y_valley_score", yval)
            blank = np.zeros(self.im.shape, dtype=np.uint8)
            # draw crop rectangle
            blank = cv2.rectangle(
                blank,
                (crop[0], crop[1]),
                (crop[0] + crop[2], crop[1] + crop[3]),
                (0, 0, 255),
                1,
            )
            blank = self.draw_bboxes(blank)
            blank = cv2.line(
                blank,
                (crop[0] + xcut, 0),
                (crop[0] + xcut, blank.shape[0]),
                (0, 255, 255),
                2,
            )
            blank = cv2.line(
                blank,
                (0, crop[1] + ycut),
                (blank.shape[1], crop[1] + ycut),
                (0, 255, 255),
                2,
            )
            blank = self.draw_profiles(blank, crop)
            cv2.imshow("debug", blank)
            cv2.waitKey(0)

        tree[d]["c1"] = self._recursive_xy_cut(
            (crop[0], crop[1], xcut, ycut),
            d=d + 1,
            max_depth=max_depth,
            debug=debug,
        )

        tree[d]["c2"] = self._recursive_xy_cut(
            (crop[0] + xcut, crop[1], crop[2] - xcut, ycut),
            d=d + 1,
            max_depth=max_depth,
            debug=debug,
        )

        tree[d]["c3"] = self._recursive_xy_cut(
            (crop[0], crop[1] + ycut, xcut, crop[3] - ycut),
            d=d + 1,
            max_depth=max_depth,
            debug=debug,
        )

        tree[d]["c4"] = self._recursive_xy_cut(
            (crop[0] + xcut, crop[1] + ycut, crop[2] - xcut, crop[3] - ycut),
            d=d + 1,
            max_depth=max_depth,
            debug=debug,
        )

        return tree


if __name__ == "__main__":
    blank = np.zeros((1080, 1920, 3), dtype=np.uint8)

    bboxes = [
        [20, 20, 1880, 50],
        [20, 100, 300, 500],
        [20, 700, 300, 300],
        [400, 100, 300, 900],
        [800, 100, 1090, 900],
    ]
    bboxes = pickle.load(open("bboxes.pkl", "rb"))

    xycut = XYCut(bboxes, blank)
    xycut.cut(max_depth=3, debug=True)
    blank = xycut.draw_bboxes(blank)
    blank = xycut.draw(blank, 3, debug=True)
    cv2.imshow("aze", blank)
    cv2.waitKey(0)
