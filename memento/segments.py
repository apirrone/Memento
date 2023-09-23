from memento import utils
from thefuzz import fuzz
import difflib

from PIL import Image
import cv2
import numpy as np


# https://stackoverflow.com/questions/37263682/how-to-find-union-of-two-strings-and-maintain-the-order
def _merge(l, r):
    m = difflib.SequenceMatcher(None, l, r)
    for o, i1, i2, j1, j2 in m.get_opcodes():
        if o == "equal":
            yield l[i1:i2]
        elif o == "delete":
            yield l[i1:i2]
        elif o == "insert":
            yield r[j1:j2]
        elif o == "replace":
            yield l[i1:i2]
            yield r[j1:j2]


def merge(a, b):
    merged = list(_merge(a.lower().split(), b.lower().split()))
    merged = " ".join(" ".join(x) for x in merged)
    return merged


class ContentSegment:
    def __init__(self):
        self.frames = {}
        self.last_text = None
        self.merged_text = "abc"

    def add(self, frame_i, text):
        self.frames[frame_i] = text
        self.last_text = text

    def get_last_text(self):
        return self.last_text

    def get_frames(self):
        return list(self.frames.keys())

    def get_merged_text(self):
        return self.merged_text

    def compile(self):
        for text in self.frames.values():
            self.merged_text = merge(self.merged_text, text)


class ContentSegments:
    def __init__(self):
        self.segments = []
        self.current_segment = None

    def add(self, frame_i, text):
        if self.current_segment is None:
            self.current_segment = ContentSegment()
            self.segments.append(self.current_segment)
        elif (
            fuzz.ratio(self.current_segment.get_last_text(), text) < 80
            and len(text) > 0
        ):
            # dissimilar texts ? new segment
            # TODO tune threshold
            self.current_segment.compile()
            self.current_segment = ContentSegment()
            self.segments.append(self.current_segment)

        self.current_segment.add(frame_i, text)


class AppSegment:
    def __init__(self, app_name, time):
        self.app_name = app_name
        self.time = time
        self.frames = {}
        self.content_segments = ContentSegments()

    def add(self, frame_i, text):
        self.frames[frame_i] = text

    def compute(self):
        # The frames are not guaranteed to arrive in order
        for frame_i in sorted(self.frames.keys()):
            frame = frame_i
            text = self.frames[frame_i]
            self.content_segments.add(frame, text)

    def show(self):
        max_x = len(self.content_segments.segments)
        max_y = 0
        for content_segment in self.content_segments.segments:
            if len(content_segment.frames.keys()) > max_y:
                max_y = len(content_segment.frames.keys())

        mosaic_size = (2560, 1440)
        tile_size = (mosaic_size[0] // max_x, mosaic_size[1] // max_y)
        mosaic = np.zeros((mosaic_size[1], mosaic_size[0], 3), dtype=np.uint8)

        x = 0
        for content_segment in self.content_segments.segments:
            y = 0
            for frame_i in content_segment.frames:
                im = frame_getter.get_frame(frame_i)
                im = cv2.rotate(im, cv2.ROTATE_90_CLOCKWISE)
                im = cv2.flip(im, 1)
                im = cv2.resize(im, tile_size)
                mosaic[y : y + tile_size[1], x : x + tile_size[0], :] = im
                y += tile_size[1]
            x += tile_size[0]
        mosaic = Image.fromarray(mosaic)
        mosaic.show()


class AppSegments:
    def __init__(self):
        self.segments = []
        self.current_segment = None
        self.done_segments = []

    def add(self, app_name, frame_i, text, time):
        if self.current_segment is None:
            self.current_segment = AppSegment(app_name, time)
            self.segments.append(self.current_segment)
        elif self.current_segment.app_name != app_name:
            self.current_segment.compute()
            self.done_segments.append(self.current_segment)
            # self.current_segment.show()
            self.current_segment = AppSegment(app_name, time)
            self.segments.append(self.current_segment)

        self.current_segment.add(frame_i, text)

    def get_done_segments(self):
        ret = self.done_segments
        self.done_segments = []
        return ret


if __name__ == "__main__":
    from memento.timeline.frame_getter import FrameGetter

    app_segments = AppSegments()
    frame_getter = FrameGetter(utils.RESOLUTION)

    for i in range(0, frame_getter.nb_frames):
        print(i)
        frame_metadata = frame_getter.metadata_cache.get_frame_metadata(i)
        app_name = frame_metadata["window_title"]
        all_text = ""

        if "text" not in frame_metadata:
            continue
        for j in range(len(frame_metadata["text"])):
            text = frame_metadata["text"][j]
            all_text += text + " "

        app_segments.add(app_name, i, all_text, "aze")
