import Xlib.display
import av
import fractions
import time
import asyncio
import cv2
import numpy as np
import os

FPS = 0.5
SECONDS_PER_REC = 10
VIDEO_CLOCK_RATE = 90000
VIDEO_PTIME = 1 / FPS
VIDEO_TIME_BASE = fractions.Fraction(1, VIDEO_CLOCK_RATE)
# RESOLUTION = (2560, 1440)
# RESOLUTION = (1280, 720)
RESOLUTION = (1920, 1080)
MAX_TWS = 10000 * FPS * SECONDS_PER_REC
FRAME_CACHE_SIZE = int((MAX_TWS / FPS / SECONDS_PER_REC))


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
        self.stream.bit_rate = 8500e1

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


def in_rect(rect, pos):
    x, y, w, h = rect
    return x <= pos[0] <= x + w and y <= pos[1] <= y + h


def rect_in_rect(rect1, rect2):
    x1, y1, w1, h1 = rect1
    x2, y2, w2, h2 = rect2
    return x1 >= x2 and y1 >= y2 and x1 + w1 <= x2 + w2 and y1 + h1 <= y2 + h2


def draw_results(res, frame):
    for entry in res:
        x = int(entry["x"])
        y = int(entry["y"])
        w = int(entry["w"])
        h = int(entry["h"])
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
            (x, y + 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (0, 0, 0),
            2,
        )
    return frame


def _draw_results(res, image):
    for entry in res:
        x = int(entry["x"])
        y = int(entry["y"])
        w = int(entry["w"])
        h = int(entry["h"])
        text = entry["text"]

        cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cv2.putText(
            image, text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 200), 2
        )

    return image


def bb_center(entry):
    x = int(entry["x"])
    y = int(entry["y"])
    w = int(entry["w"])
    h = int(entry["h"])

    return np.array([x + w / 2, y + h / 2])


def init_paragraph():
    p = {}
    p["text"] = ""
    p["x"] = 100000
    p["y"] = 100000
    p["w"] = 0
    p["h"] = 0
    p["center"] = bb_center(p)
    return p


def update_paragraph(p, entry):
    p["text"] += " " + entry["text"]
    p["x"] = min(p["x"], entry["x"])
    p["y"] = min(p["y"], entry["y"])
    entry_x2 = entry["x"] + entry["w"]
    entry_y2 = entry["y"] + entry["h"]
    p_x2 = p["x"] + p["w"]
    p_y2 = p["y"] + p["h"]

    p["w"] = max(p_x2, entry_x2) - p["x"]
    p["h"] = max(p_y2, entry_y2) - p["y"]
    p["center"] = bb_center(p)
    return p


def make_paragraphs(res, tol=500):
    paragraphs = []
    for entry in res[1:]:
        center = bb_center(entry)
        merged = False
        for i, p in enumerate(paragraphs):
            if np.linalg.norm(p["center"] - center) < tol:
                paragraphs[i] = update_paragraph(p, entry)
                merged = True
                break
        if not merged:
            paragraphs.append(init_paragraph())
            paragraphs[-1] = update_paragraph(paragraphs[-1], entry)

    return paragraphs


def imgdiff(im1, im2):
    diff = np.bitwise_xor(im1, im2)
    return np.sum(diff) / (im1.shape[0] * im1.shape[1] * im1.shape[2])


def recording():
    res = os.popen("ps aux | grep memento-bg").read()
    # > 3 because ps and grep themselves are included in the output (2) and if memento-bg is running (and not waiting for starting prompt), there are at least two processes
    return len(res.splitlines()) > 3
