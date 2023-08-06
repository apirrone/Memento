import os
import json
from glob import glob
import pmr.utils as utils
from pmr.utils import ReadersCache
import cv2
import numpy as np


class FrameGetter:
    def __init__(self, window_size):
        self.window_size = window_size

        self.cache_path = os.path.join(os.environ["HOME"], ".cache", "pmr")
        self.readers_cache = ReadersCache(self.cache_path)
        self.metadata = json.load(open(os.path.join(self.cache_path, "metadata.json")))
        self.annotations = {}
        self.current_ret_annotated = 0
        self.nb_frames = int(
            (
                len(glob(os.path.join(self.cache_path, "*.mp4")))
                * utils.FPS
                * utils.SECONDS_PER_REC
            )
        )
        self.nb_results = 0
        self.debug_mode = False

        self.current_displayed_frame_i = 0
        self.current_displayed_frame = None

    def toggle_debug_mode(self):
        self.debug_mode = not self.debug_mode
        self.clear_annotations()
        self.current_displayed_frame = None

    def get_frame(self, frame_i):
        im = self.current_displayed_frame

        # Avoid resizing and converting the same frame each time
        if (
            frame_i != self.current_displayed_frame_i
            or self.current_displayed_frame is None
        ):
            im = self.readers_cache.get_frame(min(self.nb_frames - 1, frame_i))
            self.process_debug(frame_i)
            im = self.annotate_frame(frame_i, im)
            im = cv2.resize(im, self.window_size)
            im = cv2.cvtColor(im, cv2.COLOR_BGR2RGB).swapaxes(0, 1)
            self.current_displayed_frame = im
            self.current_displayed_frame_i = frame_i
        return im

    def process_debug(self, frame_i):
        if self.debug_mode:
            self.clear_annotations()
            frame_metadata = self.metadata[str(frame_i)]
            if "bbs" in frame_metadata:
                res = []
                for i in range(len(frame_metadata["bbs"])):
                    entry = {}
                    bb = frame_metadata["bbs"][i]
                    text = frame_metadata["text"][i]
                    entry["bb"] = {
                        "x": bb["x"],
                        "y": bb["y"],
                        "w": bb["w"],
                        "h": bb["h"],
                    }
                    entry["text"] = text
                    res.append(entry)
                self.add_annotation(frame_i, res)

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

                red_rect = np.ones((h, w, 3), dtype=np.uint8)
                red_rect[:, :, 2] = 0
                red_rect *= 200
                sub_img = frame[y : y + h, x : x + w]
                res = cv2.addWeighted(sub_img, 0.5, red_rect, 0.5, 1.0)
                if res is None:
                    continue
                frame[y : y + h, x : x + w] = res
                frame = cv2.putText(
                    frame,
                    text,
                    (x, y+10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (0, 0, 0),
                    2,
                )
            frame = cv2.putText(
                frame,
                f"{self.nb_results} results",
                (50, 50),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 0, 255),
                2,
            )

        elif self.nb_results == -1:
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

    def get_annotations_text(self):
        text = ""
        for entries in self.annotations.values():
            for entry in entries:
                text += entry["text"] + "\n"
        return text

    def add_annotation(self, frame_i, annotations):
        if str(frame_i) not in self.annotations.keys():
            self.annotations[str(frame_i)] = []
        for annotation in annotations:
            self.annotations[str(frame_i)].append(annotation)
            self.nb_results += 1
        self.current_displayed_frame = None

    def is_annotated(self, frame_i):
        return str(frame_i) in self.annotations.keys()

    def clear_annotations(self):
        self.annotations = {}
        self.current_ret_annotated = 0
        self.nb_results = 0
