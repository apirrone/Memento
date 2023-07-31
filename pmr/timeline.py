from pmr.utils import ReadersCache
import json
import os
import pygame
import cv2
import pmr.utils as utils
import numpy as np
from pmr.query_db import Query


# TODO auto scroll the time bar, because when too long the zones become too small and the cursor too
# TODO refactor, there is duplicated code here
class TimeBar:
    def __init__(self, metadata, window_size):
        self.metadata = metadata
        self.nb_frames = (
            (len(self.metadata.keys()) // (utils.FPS * utils.SECONDS_PER_REC))
            * utils.FPS
            * utils.SECONDS_PER_REC
        )
        self.w = window_size[0] - window_size[0] // 5
        self.h = window_size[1] // 20
        self.x = window_size[0] // 10
        self.y = window_size[1] - self.h - window_size[1] // 10
        self.apps_colors = {}

        self.build()

    def build(self):
        for i in range(self.nb_frames):
            app = self.metadata[str(i)]["window_title"]
            if app not in self.apps_colors:
                self.apps_colors[app] = tuple(np.random.randint(0, 255, size=3))

    def get_frame_i(self, mouse_pos):
        return int((mouse_pos[0] - self.x) / self.w * self.nb_frames)

    def draw(self, screen, cursor_pos, mouse_pos, readers_cache):
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

        # draw a cursor at position i on the timeline
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
            app = self.metadata[str(frame_i)]["window_title"]
            frame = readers_cache.get_frame(frame_i)
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


class SearchBar:
    def __init__(self, window_size):
        self.x = window_size[0] // 10
        self.y = window_size[1] // 10
        self.w = window_size[0] - window_size[0] // 5
        self.h = window_size[1] // 20
        self.active = False
        self.input = ""

    def activate(self):
        self.active = True

    def deactivate(self):
        self.active = False

    def draw(self, screen):
        if self.active:
            pygame.draw.rect(
                screen,
                (255, 255, 255),
                (self.x, self.y, self.w, self.h),
                border_radius=self.h // 4,
            )

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

    def inputs(self, event):
        if event.key == pygame.K_BACKSPACE:
            self.input = self.input[:-1]
        elif event.key == pygame.K_RETURN:
            ret = self.input
            self.input = ""
            self.deactivate()
            return ret
        else:
            try:
                self.input += chr(event.key)
            except Exception:
                pass
        return None


class Timeline:
    def __init__(self):
        self.cache_path = os.path.join(os.environ["HOME"], ".cache", "pmr")
        self.readers_cache = ReadersCache(self.cache_path)
        self.metadata = json.load(open(os.path.join(self.cache_path, "metadata.json")))
        self.window_size = (1920, 1080)
        self.running = True
        self.nb_frames = (
            (len(self.metadata.keys()) // (utils.FPS * utils.SECONDS_PER_REC))
            * utils.FPS
            * utils.SECONDS_PER_REC
        )
        self.current_app = ""
        self.time_bar = TimeBar(self.metadata, self.window_size)
        self.search_bar = SearchBar(self.window_size)
        self.current_bbs = []

    def update(self):
        self.metadata = json.load(open(os.path.join(self.cache_path, "metadata.json")))
        self.nb_frames = (
            (len(self.metadata.keys()) // (utils.FPS * utils.SECONDS_PER_REC))
            * utils.FPS
            * utils.SECONDS_PER_REC
        )
        self.time_bar = TimeBar(self.metadata, self.window_size)

    def run(self):
        pygame.init()
        pygame.key.set_repeat(500, 50)
        self.screen = pygame.display.set_mode(self.window_size, pygame.RESIZABLE)
        clock = pygame.time.Clock()
        dt = 0
        i = self.nb_frames - 1
        t = 0
        while self.running:
            self.screen.fill((255, 255, 255))
            self.current_app = self.metadata[str(i)]["window_title"]
            im = self.readers_cache.get_frame(i)
            for bb in self.current_bbs:
                x = bb["x"]//2
                y = bb["y"]//2
                w = bb["w"]//2
                h = bb["h"]//2
                im = cv2.rectangle(
                    im,
                    (x, y),
                    (x + w, y + h),
                    (0, 0, 255),
                    5,
                )

            im = cv2.resize(im, self.window_size)
            im = cv2.cvtColor(im, cv2.COLOR_BGR2RGB).swapaxes(0, 1)
            surf = pygame.surfarray.make_surface(im)
            self.screen.blit(surf, (0, 0))
            self.time_bar.draw(
                self.screen, i, pygame.mouse.get_pos(), self.readers_cache
            )
            query_input = None
            for event in pygame.event.get():
                if event.type == pygame.MOUSEWHEEL:
                    i = max(0, min(self.nb_frames - 1, i + event.x - event.y))
                    self.search_bar.deactivate()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        i = self.time_bar.get_frame_i(event.pos)
                        self.search_bar.deactivate()

                if event.type == pygame.KEYDOWN:
                    if event.mod & pygame.KMOD_CTRL and event.key == pygame.K_f:
                        self.search_bar.activate()
                    elif event.key == pygame.K_ESCAPE:
                        self.search_bar.deactivate()
                    elif self.search_bar.active:
                        query_input = self.search_bar.inputs(event)

            self.search_bar.draw(self.screen)

            if query_input is not None:
                query = Query()
                results = query.query_db(query_input)
                print(results)
                print("QUERY : ", query_input)
                i = int(list(results.keys())[0])
                self.current_bbs = []
                for entry in results[list(results.keys())[0]]:
                    self.current_bbs.append(entry["bb"])
                query_input = None

            if t > utils.FPS * utils.SECONDS_PER_REC:
                print("UPDATE")
                self.update()
                t = 0

            pygame.display.flip()
            dt = clock.tick() / 1000.0
            t += dt
