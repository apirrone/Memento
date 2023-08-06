import pygame
from pmr.OCR import Tesseract
import cv2


class RegionSelector:
    def __init__(self):
        self.s = None
        self.e = None
        self.ongoing = False
        self.ocr = Tesseract(resize_factor=3, conf_threshold=50)

    def start(self, mouse_pos):
        self.s = mouse_pos
        self.e = None
        self.ongoing = True

    def end(self, mouse_pos):
        if self.ongoing:
            self.e = mouse_pos
            self.ongoing = False

    def reset(self):
        self.s = None
        self.e = None
        self.ongoing = False

    def get_region(self):
        if self.s is None or self.e is None:
            return None
        else:
            x1 = min(self.s[0], self.e[0])
            y1 = min(self.s[1], self.e[1])
            x2 = max(self.s[0], self.e[0])
            y2 = max(self.s[1], self.e[1])
            return (x1, y1, x2, y2)

    def draw(self, screen, mouse_pos):
        if self.s is not None and self.ongoing:
            pygame.draw.rect(
                screen,
                (0, 255, 255),
                (
                    *self.s,
                    mouse_pos[0] - self.s[0],
                    mouse_pos[1] - self.s[1],
                ),
                2,
            )

    def region_ocr(self, frame):
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        region = self.get_region()
        if region is None:
            return
        region_area = (region[2] - region[0]) * (region[3] - region[1])
        if region_area < 1:
            return
        crop = frame[region[1] : region[3], region[0] : region[2]]
        results = self.ocr.process_image(crop)
        res = []
        for r in results:
            entry = {
                "bb": {
                    "x": r["x"] + region[0],
                    "y": r["y"] + region[1],
                    "w": r["w"],
                    "h": r["h"],
                },
                "text": r["text"],
            }
            res.append(entry)

        return res
