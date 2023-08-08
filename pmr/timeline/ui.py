import pygame
import time


class PopUp:
    def __init__(self, text, pos, lifetime):
        self.text = text
        self.pos = pos
        self.lifetime = lifetime
        self.start_time = time.time()

    def draw(self, screen):
        font = pygame.font.SysFont("Arial", 30)

        # fade out effect
        alpha = max(0, 255 - int((time.time() - self.start_time) * 255 / self.lifetime))
        text = font.render(self.text, True, (255, 0, 0))
        surface = pygame.Surface(text.get_size())
        surface.blit(text, (0, 0))
        surface.set_alpha(alpha)
        screen.blit(surface, self.pos)

        if time.time() - self.start_time > self.lifetime:
            return False
        else:
            return True


class PopUpManager:
    def __init__(self):
        self.popups = {}

    def add_popup(self, text, pos, lifetime):
        if text not in self.popups.keys():
            self.popups[text] = PopUp(text, pos, lifetime)
        else:
            self.popups[text].start_time = time.time()

    def tick(self, screen):
        todelete = []
        for p in self.popups.values():
            if not p.draw(screen):
                todelete.append(p.text)

        for p in todelete:
            del self.popups[p]


class Plot:
    def __init__(self, time_window_size, x, y, w, h, color=(0, 255, 0)):
        self.time_window_size = time_window_size
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.color = color
        self.data = []

    def add_point(self, point):
        self.data.append(point)
        if len(self.data) > self.time_window_size:
            self.data.pop(0)

    def draw(self, screen):
        if len(self.data) == 0:
            return
        pygame.draw.rect(screen, (0, 0, 0), (self.x, self.y, self.w, self.h))
        max_val = max(self.data)
        min_val = min(self.data)
        if max_val == min_val:
            max_val = min_val + 1
        for i in range(len(self.data) - 1):
            x1 = self.x + int(i * self.w / self.time_window_size)
            x2 = self.x + int((i + 1) * self.w / self.time_window_size)
            y1 = (
                self.y
                + self.h
                - int((self.data[i] - min_val) * self.h / (max_val - min_val))
            )
            y2 = (
                self.y
                + self.h
                - int((self.data[i + 1] - min_val) * self.h / (max_val - min_val))
            )
            pygame.draw.line(screen, self.color, (x1, y1), (x2, y2), 2)
