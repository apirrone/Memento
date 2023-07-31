from pmr.utils import ReadersCache
import json
import os
import pygame
import cv2
import pmr.utils as utils
import numpy as np


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
            app = self.metadata[str(i)]["source"]
            if app not in self.apps_colors:
                self.apps_colors[app] = tuple(np.random.randint(0, 255, size=3))

    def draw(self, screen, pos):
        pygame.draw.rect(screen, (0, 0, 0), (self.x, self.y, self.w, self.h), 2)
        for i in range(self.nb_frames):
            app = self.metadata[str(i)]["source"]
            pygame.draw.rect(
                screen,
                self.apps_colors[app],
                (
                    self.x + (i / self.nb_frames) * self.w,
                    self.y,
                    self.w / self.nb_frames,
                    self.h,
                ),
            )

        # draw a cursor at position i on the timeline
        pygame.draw.rect(
            screen,
            (0, 0, 0),
            (
                self.x + (pos / self.nb_frames) * self.w,
                self.y,
                self.w / self.nb_frames,
                self.h,
            ),
            5,
        )


class Timeline:
    def __init__(self, cache_path):
        self.cache_path = cache_path
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

    def run(self):
        pygame.init()
        self.screen = pygame.display.set_mode(self.window_size, pygame.RESIZABLE)
        clock = pygame.time.Clock()
        dt = 0
        i = self.nb_frames - 1
        t = 0
        while self.running:
            self.screen.fill((255, 255, 255))
            self.current_app = self.metadata[str(i)]["source"]

            for event in pygame.event.get():
                if event.type == pygame.MOUSEWHEEL:
                    i = max(0, min(self.nb_frames - 1, i + event.x - event.y))

            surf = pygame.surfarray.make_surface(
                cv2.cvtColor(
                    self.readers_cache.get_frame(i), cv2.COLOR_BGR2RGB
                ).swapaxes(0, 1)
            )
            self.screen.blit(surf, (0, 0))
            self.time_bar.draw(self.screen, i)

            pygame.display.flip()
            dt = clock.tick() / 1000.0
            t += dt


t = Timeline(os.path.join(os.environ["HOME"], ".cache", "pmr"))
t.run()
