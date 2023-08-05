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
        self.popups = []

    def add_popup(self, text, pos, lifetime):
        self.popups.append(PopUp(text, pos, lifetime))

    def tick(self, screen):
        for p in self.popups:
            if not p.draw(screen):
                self.popups.remove(p)
