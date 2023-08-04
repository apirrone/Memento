import pygame
from pmr.timeline.frame_getter import FrameGetter
from pmr.timeline.time_bar import TimeBar
from pmr.timeline.search_bar import SearchBar
import pmr.utils as utils
from pmr.OCR import Tesseract
import cv2


class Timeline:
    def __init__(self):
        self.window_size = utils.RESOLUTION

        # Faster than pygame.init()
        pygame.display.init()
        pygame.font.init()

        self.screen = pygame.display.set_mode(self.window_size, flags=pygame.SRCALPHA)
        # +pygame.HIDDEN
        pygame.key.set_repeat(500, 50)
        self.clock = pygame.time.Clock()
        self.frame_getter = FrameGetter(self.window_size)
        self.time_bar = TimeBar(self.frame_getter)
        self.search_bar = SearchBar(self.frame_getter)
        self.region_selector = utils.RegionSelector()
        self.ocr = Tesseract(resize_factor=5, conf_threshold=50)
        self.t = 0
        self.dt = 0

    def draw_current_frame(self):
        frame = self.frame_getter.get_frame(self.time_bar.current_frame_i)
        surf = pygame.surfarray.make_surface(frame).convert()
        self.screen.blit(surf, (0, 0))

    def handle_inputs(self):
        found = False
        for event in pygame.event.get():
            found = self.search_bar.event(event)
            if event.type == pygame.MOUSEWHEEL:
                # TODO keep that ? navigate fast with scroll and use arrow keys to navigate frame per frame ?
                self.time_bar.move_cursor((event.x - event.y) * 2)
                self.region_selector.reset()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if self.time_bar.hover(event.pos):
                        self.time_bar.set_current_frame_i(
                            self.time_bar.get_frame_i(event.pos)
                        )
                    else:
                        self.region_selector.start(event.pos)
            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    self.region_selector.end(event.pos)
                    self.region_ocr()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    self.time_bar.move_cursor(-1)
                if event.key == pygame.K_RIGHT:
                    self.time_bar.move_cursor(1)
                if event.key == pygame.K_ESCAPE:
                    self.region_selector.reset()
                if event.key == pygame.K_RETURN:
                    pass

        if found:
            self.time_bar.set_current_frame_i(
                self.frame_getter.get_next_annotated_frame_i()
            )

    def region_ocr(self):
        # TODO handle this better
        # maybe no need to re run ocr
        frame = self.frame_getter.get_frame(self.time_bar.current_frame_i).swapaxes(
            0, 1
        )
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        region = self.region_selector.get_region()
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
        self.frame_getter.clear_annotations()
        self.frame_getter.add_annotation(self.time_bar.current_frame_i, res)

    def handle_region_query(self):
        region = self.region_selector.get_region()
        if region is not None:
            x = region[0]
            y = region[1]
            w = region[2] - region[0]
            h = region[3] - region[1]
            pygame.draw.rect(self.screen, (0, 255, 255), (x, y, w, h), 2)

    def run(self):
        while True:
            self.screen.fill((255, 255, 255))
            self.draw_current_frame()
            self.time_bar.draw(self.screen, pygame.mouse.get_pos())
            self.search_bar.draw(self.screen)
            self.handle_inputs()
            self.handle_region_query()

            self.region_selector.draw(self.screen, pygame.mouse.get_pos())
            pygame.display.update()
            self.dt = self.clock.tick() / 1000.0
            self.t += self.dt
