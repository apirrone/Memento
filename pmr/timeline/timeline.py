import pygame
from pmr.timeline.frame_getter import FrameGetter
from pmr.timeline.time_bar import TimeBar
from pmr.timeline.search_bar import SearchBar
import pmr.utils as utils


# TODO auto scroll the time bar, because when too long the zones become too small and the cursor too
class Timeline:
    def __init__(self):
        self.window_size = utils.RESOLUTION
        pygame.init()
        pygame.key.set_repeat(500, 50)
        self.screen = pygame.display.set_mode(self.window_size, pygame.SRCALPHA)
        self.clock = pygame.time.Clock()
        self.frame_getter = FrameGetter(self.window_size)
        self.time_bar = TimeBar(self.frame_getter)
        self.search_bar = SearchBar(self.frame_getter)
        self.t = 0
        self.dt = 0

    def draw_current_frame(self):
        frame = self.frame_getter.get_frame(self.time_bar.current_frame_i)
        surf = pygame.surfarray.make_surface(frame)
        self.screen.blit(surf, (0, 0))

    def handle_inputs(self):
        found = False
        for event in pygame.event.get():
            found = self.search_bar.event(event)
            if event.type == pygame.MOUSEWHEEL:
                # TODO keep that ? navigate fast with scroll and use arrow keys to navigate frame per frame ?
                self.time_bar.move_cursor((event.x - event.y) * 2)
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if self.time_bar.hover(event.pos):
                        self.time_bar.set_current_frame_i(
                            self.time_bar.get_frame_i(event.pos)
                        )
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    self.time_bar.move_cursor(-1)
                if event.key == pygame.K_RIGHT:
                    self.time_bar.move_cursor(1)
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    exit()
        if found:
            self.time_bar.set_current_frame_i(
                self.frame_getter.get_next_annotated_frame_i()
            )

    def run(self):
        while True:
            self.screen.fill((255, 255, 255))
            self.draw_current_frame()
            self.time_bar.draw(self.screen, pygame.mouse.get_pos())
            self.search_bar.draw(self.screen)
            self.handle_inputs()

            pygame.display.flip()
            self.dt = self.clock.tick() / 1000.0
            self.t += self.dt
