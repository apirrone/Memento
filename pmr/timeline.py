from pmr.utils import ReadersCache
import json
import os
import pygame
import cv2


class Timeline:
    def __init__(self, cache_path):
        self.cache_path = cache_path
        self.readers_cache = ReadersCache(self.cache_path)
        self.metadata = json.load(open(os.path.join(self.cache_path, "metadata.json")))
        self.window_size = (1920, 1080)
        self.running = True

    def run(self):
        pygame.init()
        self.screen = pygame.display.set_mode(self.window_size, pygame.RESIZABLE)
        clock = pygame.time.Clock()
        dt = 0
        i = 0
        t = 0
        while self.running:
            self.screen.fill((255, 255, 255))

            surf = pygame.surfarray.make_surface(cv2.cvtColor(self.readers_cache.get_frame(i), cv2.COLOR_BGR2RGB).swapaxes(0, 1))
            self.screen.blit(surf, (0, 0))
            pygame.display.flip()
            dt = clock.tick() / 1000.0
            t += dt
            print(t)
            if t > 0.5:
                i += 1
                t = 0
            if i > 29:
                i = 0


t = Timeline(os.path.join(os.environ["HOME"], ".cache", "pmr"))
t.run()
