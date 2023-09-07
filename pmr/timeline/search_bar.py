import pygame
import pygame_textinput
from pmr.db import Db


class SearchBar:
    def __init__(self, frame_getter):
        self.frame_getter = frame_getter
        self.db = Db()

        ws = self.frame_getter.window_size
        self.x = ws[0] // 10
        self.y = ws[1] // 10
        self.w = ws[0] - ws[0] // 5
        self.h = ws[1] // 20
        self.active = False
        self.found = False
        self.input_changed = False

        self.textinput = pygame_textinput.TextInputManager()

    def activate(self):
        self.active = True
        self.textinput.value = ""

    def deactivate(self):
        self.active = False
        self.textinput.value = ""
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
        text = font.render(self.textinput.value, True, (0, 0, 0))
        screen.blit(text, (self.x + 10, self.y + 10))

        if len(self.textinput.value) > 0:
            cursor_pos = font.size(self.textinput.value)[0] + 10
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
        print("start query")
        self.frame_getter.clear_annotations()
        query_input = self.textinput.value

        results = self.db.search(query_input)

        self.frame_getter.set_annotation(results)
        if len(results) > 0:
            self.found = True
            self.frame_getter.nb_results = len(results)
        else:
            self.found = False
            self.frame_getter.nb_results = -1

    def events(self, events):
        self.textinput.update(events)
        ret = False
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.mod & pygame.KMOD_CTRL and event.key == pygame.K_f:
                    self.activate()
                    self.input_changed = False
                elif event.key == pygame.K_ESCAPE:
                    self.deactivate()
                elif event.key == pygame.K_BACKSPACE:
                    self.input_changed = True
                elif event.key == pygame.K_RETURN:
                    if self.active and len(self.textinput.value) > 0:
                        if self.input_changed or not self.found:
                            self.start_query()
                        if self.found:
                            ret = True
                    self.input_changed = False
                elif self.active:
                    self.input_changed = True
        return ret
