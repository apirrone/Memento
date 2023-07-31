import Xlib.display
import av
import fractions
import time
import asyncio
import os

FPS = 1
SECONDS_PER_REC = 10
AUDIO_PTIME = 0.020  # 20ms audio packetization
VIDEO_CLOCK_RATE = 90000
VIDEO_PTIME = 1 / FPS
VIDEO_TIME_BASE = fractions.Fraction(1, VIDEO_CLOCK_RATE)
# RESOLUTION = (2560, 1440)
RESOLUTION = (1920, 1080)


def get_active_window():
    display = Xlib.display.Display()
    window = display.get_input_focus().focus
    if isinstance(window, Xlib.xobject.drawable.Window):
        wmclass = window.get_wm_class()
        if wmclass is None:
            window = window.query_tree().parent
            wmclass = window.get_wm_class()
        if wmclass is None:
            return "None"
        winclass = wmclass[1]
        return winclass
    else:
        return "None"


# check that a y coordinate is within a line with a tolerance of y_tol
def is_within_line(y, line, y_tol):
    return abs(y - line) < y_tol


# check if there is already a line of coordinate y
def line_exists(y, lines, y_tol):
    for line in lines.keys():
        if is_within_line(y, line, y_tol):
            return line
    return None


def same_sentence(last_word, x, x_tol):
    l_x = last_word["x"]
    l_w = last_word["w"]

    return not (x > l_x + l_w + x_tol)


class Recorder:
    _start: float
    _timestamp: int

    def __init__(self, filename):
        self.output = av.open(filename, "w")
        self.stream = self.output.add_stream("h264", str(FPS))
        self.stream.height = RESOLUTION[1]
        self.stream.width = RESOLUTION[0]
        self.stream.bit_rate = 8500e3

    def start(self):
        self._start = time.time()

    async def next_timestamp(self):
        if hasattr(self, "_timestamp"):
            self._timestamp += int(VIDEO_PTIME * VIDEO_CLOCK_RATE)
            wait = self._start + (self._timestamp / VIDEO_CLOCK_RATE) - time.time()
            await asyncio.sleep(wait)
        else:
            self._start = time.time()
            self._timestamp = 0
        return self._timestamp, VIDEO_TIME_BASE

    async def new_im(self, im):
        pts, time_base = await self.next_timestamp()
        frame = av.video.frame.VideoFrame.from_ndarray(im, format="bgr24")
        frame.pts = pts
        frame.time_base = time_base
        packet = self.stream.encode(frame)
        self.output.mux(packet)

    def stop(self):
        packet = self.stream.encode(None)
        self.output.mux(packet)
        self.output.close()


class Reader:
    def __init__(self, filename, offset=0):
        self.container = av.open(filename)
        self.stream = self.container.streams.video[0]
        self.frames = []
        for i, frame in enumerate(self.container.decode(self.stream)):
            self.frames.append(frame)
        self.offset = offset

    # TODO there is a bug here, the found frame does not correspond to the ocr data
    def get_frame(self, frame_i):
        if (frame_i - self.offset) < len(self.frames):
            return self.frames[frame_i - self.offset].to_ndarray(format="bgr24")
        else:
            return None


# TODO remove from cache (smartly)
class ReadersCache:
    def __init__(self, cache_path):
        self.readers = {}
        self.cache_path = cache_path

    def select_video(self, frame_id):
        return frame_id // (FPS * SECONDS_PER_REC)

    def get_reader(self, frame_id):
        video_id = self.select_video(frame_id)
        offset = video_id * (FPS * SECONDS_PER_REC)
        if video_id not in self.readers:  # Caching reader
            start = time.time()
            self.readers[video_id] = Reader(
                os.path.join(self.cache_path, str(video_id) + ".mp4"), offset=offset
            )
            print(
                "Caching reader",
                video_id,
                "at",
                offset,
                "offset frames took",
                time.time() - start,
                "seconds",
            )
        return self.readers[video_id]

    # Shorthand
    def get_frame(self, frame_id):
        return self.get_reader(frame_id).get_frame(frame_id)


def in_rect(rect, pos):
    x, y, w, h = rect
    return x <= pos[0] <= x + w and y <= pos[1] <= y + h
