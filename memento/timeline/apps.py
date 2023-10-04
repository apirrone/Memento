import numpy as np
from memento.timeline.icon_getter import IconGetter
import time

COLOR_PALETTE = [
    [244, 67, 54],
    [233, 30, 99],
    [156, 39, 176],
    [103, 58, 183],
    [63, 81, 181],
    [33, 150, 243],
    [3, 169, 244],
    [0, 188, 212],
    [0, 150, 136],
    [76, 175, 80],
    [139, 195, 74],
    [205, 220, 57],
    [255, 235, 59],
    [255, 193, 7],
    [255, 152, 0],
    [255, 87, 34],
]
# TODO add more colors if needed ?


class Apps:
    def __init__(self, frame_getter):
        self.apps = {}
        self.frame_getter = frame_getter
        ws = self.frame_getter.window_size
        self.h = ws[1] // 40

        self.metadata_cache = self.frame_getter.metadata_cache
        self.nb_frames = self.frame_getter.nb_frames
        self.ig = IconGetter(size=self.h)

        # Hacky solution for faster timeline startup
        stride = 100
        if len(self.ig.icon_cache) == 0 or self.nb_frames < 1000:
            stride = 1
        for i in range(0, self.nb_frames, stride):
            app = self.metadata_cache.get_frame_metadata(i)["window_title"]
            if app not in self.apps:
                self.apps[app] = {}
                if len(self.apps) < len(COLOR_PALETTE):
                    self.apps[app]["color"] = tuple(COLOR_PALETTE[len(self.apps)])
                else:
                    self.apps[app]["color"] = tuple(np.random.randint(0, 255, size=3))
                icon_small, icon_big = self.ig.lookup_icon(app)
                self.apps[app]["icon_small"] = icon_small
                self.apps[app]["icon_big"] = icon_big

    def get_color(self, app):
        return self.apps[app]["color"]

    def get_icon(self, app, small=True):
        if small:
            return self.apps[app]["icon_small"]
        else:
            return self.apps[app]["icon_big"]
