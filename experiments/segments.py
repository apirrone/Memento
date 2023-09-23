from memento.timeline.frame_getter import FrameGetter
from memento import utils
from PIL import Image
import cv2
from thefuzz import fuzz
import numpy as np

frame_getter = FrameGetter(utils.RESOLUTION)


class ContentSegment:
    def __init__(self):
        self.frames = {}
        self.last_text = None

    def add(self, frame_i, text):
        self.frames[frame_i] = text
        self.last_text = text

    def get_last_text(self):
        return self.last_text

    def compile(self):
        # TODO compile texts, remove redundency, make a coherent segment
        pass


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
            print("DISSIMILAR")
            # dissimilar texts ? new segment
            # TODO tune threshold
            self.current_segment.compile()
            self.current_segment = ContentSegment()
            self.segments.append(self.current_segment)
        else:
            print("SIMILAR")

        self.current_segment.add(frame_i, text)


class AppSegment:
    def __init__(self, app_name):
        self.app_name = app_name
        self.frames = {}
        self.content_segments = ContentSegments()

    def add(self, frame_i, text):
        self.frames[frame_i] = text

    def compute(self):
        # print(list(self.frames.keys()))
        for frame, text in self.frames.items():
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

    def add(self, app_name, frame_i, text):
        if self.current_segment is None:
            self.current_segment = AppSegment(app_name)
            self.segments.append(self.current_segment)
        elif self.current_segment.app_name != app_name:
            self.current_segment.compute()
            self.current_segment.show()
            input()
            self.current_segment = AppSegment(app_name)
            self.segments.append(self.current_segment)

        self.current_segment.add(frame_i, text)


app_segments = AppSegments()

for i in range(0, frame_getter.nb_frames // 10):
    frame_metadata = frame_getter.metadata_cache.get_frame_metadata(i)
    app_name = frame_metadata["window_title"]
    all_text = ""

    if "text" not in frame_metadata:
        # print("AAAAAAAAAAA")
        continue
    for j in range(len(frame_metadata["text"])):
        text = frame_metadata["text"][j]
        all_text += text + " "

    app_segments.add(app_name, i, all_text)

    # print(app)
    # frame = frame_getter.get_frame(i)
    # frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
    # frame = cv2.flip(frame, 1)
    # frame = Image.fromarray(frame)
    # frame.show("aze")
    # input("...")
