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
