import pickle
import numpy as np
import cv2


class ProfileSeg:
    def __init__(self, bboxes, im_size):
        self.bboxes = bboxes
        self.im_size = im_size

    def _compute_profiles(self):
        # crop : (x, y, w, h)

        hp = np.zeros(self.im_size[0], np.uint8)
        vp = np.zeros(self.im_size[1], np.uint8)

        for bbox in self.bboxes:
            x, y, w, h = bbox

            hp[y : y + h] += 1
            vp[x : x + w] += 1

        return hp, vp

    # Find the biggest valley and return its index in profile
    def _profile_cut(self, profile, nb=2):
        vws = 100
        if vws < 3:
            return None, None

        kernel = cv2.getGaussianKernel(vws, 1)

        valleys_scores = []
        valleys_indices = []
        for i in range(vws, len(profile) - vws):
            window = profile[i - vws : i]

            res = sum(sum(window * kernel))
            valleys_scores.append(res)
            valleys_indices.append(i)

        ret = [
            id
            for score, id in sorted(zip(valleys_scores, valleys_indices), reverse=False)
        ]
        return ret[:nb]

    def _profile_cut2(self, profile, nb=2):
        grad = np.gradient(profile)
        print(len(grad))
        cv2.imshow("gradient", self.draw_profile(np.gradient(profile)))
        # cv2.waitKey(0)

    def draw_profile(self, profile):
        blank = np.zeros((*self.im_size, 3), np.uint8)
        for i, p in enumerate(profile):
            blank[self.im_size[0] - int(p) : self.im_size[0], i] = (255, 255, 255)

        return blank

    def draw_profiles(self, blank):
        hp, vp = self._compute_profiles()
        hp *= 10
        vp *= 10

        for i, p in enumerate(hp):
            blank[i, self.im_size[1] - p : self.im_size[1]] = (255, 255, 255)

        for i, p in enumerate(vp):
            blank[self.im_size[0] - p : self.im_size[0], i] = (255, 255, 255)

        return blank

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


for bboxes in [pickle.load(open("bboxes" + str(i) + ".pkl", "rb")) for i in range(5)]:
    blank = np.zeros((1080, 1920, 3), np.uint8)
    profile_seg = ProfileSeg(bboxes, blank.shape[:2])
    # im = profile_seg.draw_bboxes(blank)
    im = profile_seg.draw_profiles(blank)
    hp, vp = profile_seg._compute_profiles()
    # h_idx = profile_seg._profile_cut(hp, nb=1)
    # v_idx = profile_seg._profile_cut(vp, nb=1)
    profile_seg._profile_cut2(vp * 100)
    # for h_id in h_idx:
    #     im = cv2.line(im, (0, h_id), (1920, h_id), (0, 0, 255), 1)

    # for v_id in v_idx:
    #     im = cv2.line(im, (v_id, 0), (v_id, 1080), (0, 0, 255), 1)

    # exit()
    cv2.imshow("im", im)
    cv2.waitKey(0)
