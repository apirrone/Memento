import numpy as np
import cv2


class XYCut:
    # bboxes : list of bounding boxes [x, y, w, h]
    def __init__(self, bboxes, im_shape):
        self.bboxes = bboxes
        self.im_shape = im_shape
        self.tree = None

    def cut(self, max_depth=2, debug=False):
        hp, vp = self._profiles()
        self.tree = self._recursive_xy_cut(
            hp,
            vp,
            (0, self.im_shape[1]),
            (0, self.im_shape[0]),
            max_depth=max_depth,
            debug=debug,
        )

    def draw_bboxes(self, im):
        for bbox in self.bboxes:
            im = cv2.rectangle(
                im,
                (bbox[0], bbox[1]),
                (bbox[0] + bbox[2], bbox[1] + bbox[3]),
                (255, 255, 255),
                1,
            )
        return im

    def draw(self, im, level, debug=False):
        return self._draw_tree(im, self.tree, level, debug=debug)

    def _bbox_in_crop(self, bbox, crop):
        # crop : (x, y, w, h)
        x = bbox[0]
        y = bbox[1]
        w = bbox[2]
        h = bbox[3]
        x2 = x + w
        y2 = y + h

        pass

    def _compute_profiles(self, crop):
        # crop : (x, y, w, h)

        hp = np.zeros((crop[3]), np.uint8)
        vp = np.zeros((crop[2]), np.uint8)

        for bbox in self.bboxes:
            x = bbox[0]
            y = bbox[1]
            w = bbox[2]
            h = bbox[3]
            x2 = x + w
            y2 = y + h
            hp[y : y + h] += 1
            vp[x : x + w] += 1

        return hp, vp

    def _profiles(self):
        hp = np.zeros((self.im_shape[0]), np.uint8)
        vp = np.zeros((self.im_shape[1]), np.uint8)

        for bbox in self.bboxes:
            x = bbox[0]
            y = bbox[1]
            w = bbox[2]
            h = bbox[3]
            hp[y : y + h] += 1
            vp[x : x + w] += 1

        return hp, vp

    def draw_profiles(self, im, hp, vp):
        _hp = hp * 10
        _vp = vp * 10
        for i, p in enumerate(_hp):
            im[i, im.shape[1] - p :] = (255, 255, 255)

        for i, p in enumerate(_vp):
            im[im.shape[0] - p :, i] = (255, 255, 255)
        return im

    # Find the biggest valley and return its index in profile
    def _profile_cut(self, profile):
        valley_window_size = len(profile) // 10
        if valley_window_size < 3:
            return None, None

        kernel = cv2.getGaussianKernel(valley_window_size, 1)

        min_val = 100000000
        min_idx = 0
        for i in range(valley_window_size, len(profile) - valley_window_size):
            window = profile[i - valley_window_size : i]

            res = sum(sum(window * kernel))
            if res < min_val:
                min_val = res
                min_idx = i

        return min_idx, min_val / valley_window_size

    def _recursive_xy_cut(self, hp, vp, xcrop, ycrop, d=0, max_depth=2, debug=False):
        tree = {}
        tree[d] = {}

        tree[d]["xcrop"] = xcrop
        tree[d]["ycrop"] = ycrop

        xcut, x_valley_score = self._profile_cut(vp[xcrop[0] : xcrop[1]])
        ycut, y_valley_score = self._profile_cut(hp[ycrop[0] : ycrop[1]])

        if d == max_depth:
            print("max depth reached,", d)
            return tree

        if xcut is None or ycut is None:
            print("no cut found")
            return tree

        if debug:
            print("x_valley_score", x_valley_score)
            print("y_valley_score", y_valley_score)
            blank = np.zeros((*self.im_shape, 3), dtype=np.uint8)
            # draw transparent rectangle for xcrop and ycrop
            blank = cv2.rectangle(
                blank,
                (xcrop[0], ycrop[0]),
                (xcrop[1], ycrop[1]),
                (0, 0, 255),
                50,
            )
            blank = self.draw_profiles(blank, hp, vp)
            blank = self.draw_bboxes(blank)
            cv2.line(
                blank,
                (xcrop[0] + xcut, 0),
                (xcrop[0] + xcut, blank.shape[0]),
                (0, 255, 255),
                2,
            )
            cv2.line(
                blank,
                (0, ycrop[0] + ycut),
                (blank.shape[1], ycrop[0] + ycut),
                (0, 255, 255),
                2,
            )
            cv2.imshow("debug", blank)
            cv2.waitKey(0)

        tree[d]["c1"] = self._recursive_xy_cut(
            hp,
            vp,
            (xcrop[0], xcut),
            (ycrop[0], ycut),
            d + 1,
            max_depth=max_depth,
            debug=debug,
        )
        tree[d]["c2"] = self._recursive_xy_cut(
            hp,
            vp,
            (xcrop[0], xcut),
            (ycut, ycrop[1]),
            d + 1,
            max_depth=max_depth,
            debug=debug,
        )
        tree[d]["c3"] = self._recursive_xy_cut(
            hp,
            vp,
            (xcut, xcrop[1]),
            (ycrop[0], ycut),
            d + 1,
            max_depth=max_depth,
            debug=debug,
        )
        tree[d]["c4"] = self._recursive_xy_cut(
            hp,
            vp,
            (xcut, xcrop[1]),
            (ycut, ycrop[1]),
            d + 1,
            max_depth=max_depth,
            debug=debug,
        )

        return tree

    def _draw_tree(self, im, tree, level, d=0, debug=False):
        xcrop = tree[d]["xcrop"]
        ycrop = tree[d]["ycrop"]

        if d == level:
            im = cv2.rectangle(
                im,
                (xcrop[0], ycrop[0]),
                (xcrop[1], ycrop[1]),
                (0, 0, 255),
                2,
            )
            if debug:
                cv2.imshow("debug", im)
                cv2.waitKey(0)
            return im

        im = self._draw_tree(im, tree[d]["c1"], level, d + 1)
        im = self._draw_tree(im, tree[d]["c2"], level, d + 1)
        im = self._draw_tree(im, tree[d]["c3"], level, d + 1)
        im = self._draw_tree(im, tree[d]["c4"], level, d + 1)

        return im


if __name__ == "__main__":
    blank = np.zeros((1080, 1920, 3), dtype=np.uint8)

    bboxes = [
        [20, 20, 1880, 50],
        [20, 100, 300, 500],
        [20, 700, 300, 300],
        [400, 100, 300, 900],
        [800, 100, 1090, 900],
    ]

    xycut = XYCut(bboxes, (1080, 1920))
    xycut.cut(max_depth=2, debug=True)
    # blank = xycut.draw_bboxes(blank)
    blank = xycut.draw(blank, 2, debug=False)
    # cv2.imshow("aze", blank)
    # cv2.waitKey(0)
