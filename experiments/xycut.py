import numpy as np
import cv2


class XYCut:
    # bboxes : list of bounding boxes [x, y, w, h]
    def __init__(self, bboxes, im_shape):
        self.bboxes = bboxes
        self.im_shape = im_shape
        self.tree = None

    def cut(self, max_depth=2):
        hp, vp = self._profiles()
        self.tree = self._recursive_xy_cut(
            hp, vp, (0, self.im_shape[1]), (0, self.im_shape[0]), max_depth=max_depth
        )

    def draw_bboxes(self, im):
        for bbox in self.bboxes:
            im = cv2.rectangle(
                im,
                (bbox[0], bbox[1]),
                (bbox[0] + bbox[2], bbox[1] + bbox[3]),
                (255, 0, 255),
                2,
            )
        return im

    def draw(self, im, level):
        return self._draw_tree(im, self.tree, level)

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
        hp *= 10
        vp *= 10
        for i, p in enumerate(hp):
            im[i, im.shape[1] - p :] = (255, 255, 255)

        for i, p in enumerate(vp):
            im[im.shape[0] - p :, i] = (255, 255, 255)
        return im

    # Find the biggest valley and return its index in profile
    def _profile_cut(self, profile, valley_window_size=100):
        kernel = cv2.getGaussianKernel(valley_window_size, 1)

        min_val = 100000000
        min_idx = 0
        for i in range(valley_window_size, len(profile) - valley_window_size):
            window = profile[i - valley_window_size : i]

            res = sum(sum(window * kernel))
            if res < min_val:
                min_val = res
                min_idx = i

        return min_idx

    def _recursive_xy_cut(self, hp, vp, xcrop, ycrop, d=0, max_depth=2):
        tree = {}
        tree[d] = {}

        tree[d]["xcrop"] = xcrop
        tree[d]["ycrop"] = ycrop

        xcut = self._profile_cut(vp[xcrop[0] : xcrop[1]])
        ycut = self._profile_cut(hp[ycrop[0] : ycrop[1]])

        if d == max_depth:
            print("max depth reached,", d)
            return tree

        tree[d]["c1"] = self._recursive_xy_cut(
            hp, vp, (xcrop[0], xcut), (ycrop[0], ycut), d + 1, max_depth=max_depth
        )
        tree[d]["c2"] = self._recursive_xy_cut(
            hp, vp, (xcrop[0], xcut), (ycut, ycrop[1]), d + 1, max_depth=max_depth
        )
        tree[d]["c3"] = self._recursive_xy_cut(
            hp, vp, (xcut, xcrop[1]), (ycrop[0], ycut), d + 1,  max_depth=max_depth
        )
        tree[d]["c4"] = self._recursive_xy_cut(
            hp, vp, (xcut, xcrop[1]), (ycut, ycrop[1]), d + 1, max_depth=max_depth
        )

        return tree

    def _draw_tree(self, im, tree, level, d=0):
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
            return im

        im = self._draw_tree(im, tree[d]["c1"], level, d + 1)
        im = self._draw_tree(im, tree[d]["c2"], level, d + 1)
        im = self._draw_tree(im, tree[d]["c3"], level, d + 1)
        im = self._draw_tree(im, tree[d]["c4"], level, d + 1)

        return im
