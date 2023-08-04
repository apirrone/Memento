import pygame
from pmr.query_db import Query


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
        self.input_changed = False

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
        print("start query")
        self.frame_getter.clear_annotations()
        query_input = self.input

        results = Query().query_db(query_input, nb_results=5)
        self.frame_getter.set_annotation(results)
        if len(results) > 0:
            self.found = True
            self.frame_getter.nb_results=len(results)
        else:
            self.found = False
            self.frame_getter.nb_results=-1



    def event(self, event):
        ret = False
        if event.type == pygame.KEYDOWN:
            if event.mod & pygame.KMOD_CTRL and event.key == pygame.K_f:
                self.activate()
                self.input_changed = False
            elif event.key == pygame.K_ESCAPE:
                self.deactivate()
            elif event.key == pygame.K_BACKSPACE:
                self.input = self.input[:-1]
                self.input_changed = True
            elif event.key == pygame.K_RETURN:
                if self.active and len(self.input) > 0:
                    if self.input_changed or not self.found:
                        self.start_query()
                    ret = True
                self.input_changed = False
            elif self.active:
                try:
                    self.input_changed = True
                    self.input += chr(event.key)
                except Exception:
                    pass
        return ret
