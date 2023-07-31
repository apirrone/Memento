from pmr.utils import ReadersCache
import pmr.utils as utils
from pmr.query_db import Query
import os
import json
import cv2
import numpy as np
import pygame


class FrameGetter:
    def __init__(self, window_size):
        self.window_size = window_size

        self.cache_path = os.path.join(os.environ["HOME"], ".cache", "pmr")
        self.readers_cache = ReadersCache(self.cache_path)
        self.metadata = json.load(open(os.path.join(self.cache_path, "metadata.json")))
        self.annotations = {}
        self.current_ret_annotated = 0
        self.nb_frames = (
            (len(self.metadata.keys()) // (utils.FPS * utils.SECONDS_PER_REC))
            * utils.FPS
            * utils.SECONDS_PER_REC
        )

    def get_frame(self, i, raw=False):
        im = self.readers_cache.get_frame(i)
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
                x = int(bb["x"]) // 2
                y = int(bb["y"]) // 2
                w = int(bb["w"]) // 2
                h = int(bb["h"]) // 2
                frame = cv2.rectangle(
                    frame,
                    (x, y),
                    (x + w, y + h),
                    (0, 0, 255),
                    5,
                )
        return frame

    def get_next_annotated_frame_i(self):
        frame_i = list(self.annotations.keys())[self.current_ret_annotated]
        self.current_ret_annotated += 1
        if self.current_ret_annotated >= len(self.annotations.keys()):
            self.current_ret_annotated = 0
        return int(frame_i)

    def set_annotation(self, annotations):
        self.annotations = annotations

    def clear_annotations(self):
        self.annotations = {}
        self.current_ret_annotated = 0


class TimeBar:
    def __init__(self, frame_getter):
        self.frame_getter = frame_getter
        self.nb_frames = self.frame_getter.nb_frames
        self.metadata = self.frame_getter.metadata
        ws = self.frame_getter.window_size
        self.w = ws[0] - ws[0] // 5
        self.h = ws[1] // 20
        self.x = ws[0] // 10
        self.y = ws[1] - self.h - ws[1] // 10

        self.apps_colors = {}

        self.build()

    def build(self):
        for i in range(self.nb_frames):
            app = self.metadata[str(i)]["window_title"]
            if app not in self.apps_colors:
                self.apps_colors[app] = tuple(np.random.randint(0, 255, size=3))

    def get_frame_i(self, mouse_pos):
        return int((mouse_pos[0] - self.x) / self.w * self.nb_frames)

    def draw_cursor(self, screen, cursor_pos):
        pygame.draw.rect(
            screen,
            (0, 0, 0),
            (
                self.x + (cursor_pos / self.nb_frames) * self.w,
                self.y,
                self.w / self.nb_frames,
                self.h,
            ),
            5,
        )

    def draw_bar(self, screen):
        for i in range(self.nb_frames):
            app = self.metadata[str(i)]["window_title"]
            pygame.draw.rect(
                screen,
                self.apps_colors[app],
                (
                    self.x + (i / self.nb_frames) * self.w,
                    self.y,
                    self.w / self.nb_frames + 1,
                    self.h,
                ),
            )

    def draw_preview(self, screen, mouse_pos):
        if utils.in_rect((self.x, self.y, self.w, self.h), mouse_pos):
            pygame.draw.rect(
                screen,
                (255, 0, 0),
                (
                    mouse_pos[0] - self.w / self.nb_frames / 2,
                    self.y,
                    self.w / self.nb_frames,
                    self.h,
                ),
                5,
            )
            frame_i = self.get_frame_i(mouse_pos)
            frame = self.frame_getter.get_frame(frame_i, raw=True)
            app = self.metadata[str(frame_i)]["window_title"]
            frame = cv2.putText(
                frame, app, (10, 200), cv2.FONT_HERSHEY_SIMPLEX, 6, (255, 255, 0), 20
            )
            frame = cv2.resize(frame, (0, 0), fx=0.2, fy=0.2)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB).swapaxes(0, 1)

            surf = pygame.surfarray.make_surface(frame)
            screen.blit(
                surf,
                [mouse_pos[0], self.y]
                - np.array([frame.shape[0] // 2, frame.shape[1]]),
            )

    def draw(self, screen, current_frame_i, mouse_pos):
        self.draw_bar(screen)
        self.draw_cursor(screen, current_frame_i)
        self.draw_preview(screen, mouse_pos)


class SearchBar:
    def __init__(self, frame_getter):
        self.frame_getter = frame_getter

        ws = self.frame_getter.window_size
        self.x = ws[0] // 10
        self.y = ws[1] // 10
        self.w = ws[0] - ws[0] // 5
        self.h = ws[1] // 20
        self.active = False
        self.input = ""
        self.found = False

    def activate(self):
        self.active = True

    def deactivate(self):
        self.active = False
        self.input = ""
        self.found = False

    def draw_bar(self, screen):
        pygame.draw.rect(
            screen,
            (255, 255, 255),
            (self.x, self.y, self.w, self.h),
            border_radius=self.h // 4,
        )

    def draw_text(self, screen):
        font = pygame.font.SysFont("Arial", self.h // 2)
        text = font.render(self.input, True, (0, 0, 0))
        screen.blit(text, (self.x + 10, self.y + 10))

        if len(self.input) > 0:
            cursor_pos = font.size(self.input)[0] + 10
        else:
            cursor_pos = 10

        if pygame.time.get_ticks() % 1000 < 500:
            pygame.draw.rect(
                screen,
                (0, 0, 0),
                (
                    self.x + cursor_pos,
                    self.y + 10,
                    2,
                    self.h - 20,
                ),
            )

    def draw(self, screen):
        if not self.active:
            return
        self.draw_bar(screen)
        self.draw_text(screen)

    def start_query(self):
        query_input = self.input
        results = Query().query_db(query_input, nb_results=20)
        self.frame_getter.set_annotation(results)
        self.found = True

    def event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.mod & pygame.KMOD_CTRL and event.key == pygame.K_f:
                if self.active and self.found:
                    return True
                elif self.active and not self.found:
                    self.start_query()
                else:
                    self.activate()
            elif event.key == pygame.K_ESCAPE:
                self.deactivate()
            elif event.key == pygame.K_BACKSPACE:
                self.input = self.input[:-1]
            elif event.key == pygame.K_RETURN:
                if not self.found and len(self.input) > 0:
                    self.start_query()
                elif self.found:
                    return True
            else:
                try:
                    self.input += chr(event.key)
                except Exception:
                    pass
        return False
