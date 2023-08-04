import os
import json
from glob import glob
import pmr.utils as utils
from pmr.utils import ReadersCache
import cv2


class FrameGetter:
    def __init__(self, window_size):
        self.window_size = window_size

        self.cache_path = os.path.join(os.environ["HOME"], ".cache", "pmr")
        self.readers_cache = ReadersCache(self.cache_path)
        self.metadata = json.load(open(os.path.join(self.cache_path, "metadata.json")))
        self.annotations = {}
        self.current_ret_annotated = 0
        self.nb_frames = (
            len(glob(os.path.join(self.cache_path, "*.mp4")))
            * utils.FPS
            * utils.SECONDS_PER_REC
        )
        self.nb_results=0

    def get_frame(self, i, raw=False):
        im = self.readers_cache.get_frame(min(self.nb_frames - 1, i))
        im = self.annotate_frame(i, im)
        if not raw:
            im = cv2.resize(im, self.window_size)
            im = cv2.cvtColor(im, cv2.COLOR_BGR2RGB).swapaxes(0, 1)
        return im

    def annotate_frame(self, frame_i, frame):
        if str(frame_i) in self.annotations.keys():
            entries = self.annotations[str(frame_i)]
            for entry in entries:
                bb = entry["bb"]
                x = int(bb["x"])
                y = int(bb["y"])
                w = int(bb["w"])
                h = int(bb["h"])
                text = entry["text"]
                frame = cv2.rectangle(
                    frame,
                    (x, y),
                    (x + w, y + h),
                    (0, 0, 255),
                    5,
                )
                frame = cv2.putText(
                    frame,
                    text,
                    (x, y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (0, 0, 255),
                    2,
                )
            frame = cv2.putText(
                    frame,
                    f'{self.nb_results} results',
                    (50, 50),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (0, 0, 255),
                    2,
                )

        elif self.nb_results==-1:
            frame = cv2.putText(
                    frame,
                    "No result",
                    (50, 50),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (0, 0, 255),
                    2,
                )

        return frame

    def get_next_annotated_frame_i(self):
        if len(self.annotations.keys()) > 0:

            frame_i = list(self.annotations.keys())[self.current_ret_annotated]
            self.current_ret_annotated += 1
            if self.current_ret_annotated >= len(self.annotations.keys()):
                self.current_ret_annotated = 0
            return int(frame_i)
        else:
            return 0
    def set_annotation(self, annotations):
        self.annotations = annotations

    def clear_annotations(self):
        self.annotations = {}
        self.current_ret_annotated = 0
        self.nb_results=0
