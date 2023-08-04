import pygame
from pmr.timeline_utils import FrameGetter, TimeBar, SearchBar
import pmr.utils as utils


# TODO auto scroll the time bar, because when too long the zones become too small and the cursor too
class Timeline:
    def __init__(self):
        self.window_size = utils.RESOLUTION
        self.frame_getter = FrameGetter(self.window_size)
        self.time_bar = TimeBar(self.frame_getter)
        self.search_bar = SearchBar(self.frame_getter)
        self.current_frame_i = self.frame_getter.nb_frames-1
        self.t = 0
        self.dt = 0

    def draw_current_frame(self):
        frame = self.frame_getter.get_frame(self.current_frame_i)
        surf = pygame.surfarray.make_surface(frame)
        self.screen.blit(surf, (0, 0))

    def handle_inputs(self):
        found = False
        for event in pygame.event.get():
            found = self.search_bar.event(event)
            if event.type == pygame.MOUSEWHEEL:
                self.current_frame_i = max(
                    0,
                    min(
                        self.frame_getter.nb_frames - 1,
                        self.current_frame_i + event.x - event.y,
                    ),
                )
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.current_frame_i = self.time_bar.get_frame_i(event.pos)
        if found:
            self.current_frame_i = self.frame_getter.get_next_annotated_frame_i()

    def run(self):
        pygame.init()
        pygame.key.set_repeat(500, 50)
        self.screen = pygame.display.set_mode(self.window_size, pygame.RESIZABLE)
        self.clock = pygame.time.Clock()
        while True:
            self.screen.fill((255, 255, 255))
            self.draw_current_frame()
            self.time_bar.draw(
                self.screen, self.current_frame_i, pygame.mouse.get_pos()
            )
            self.search_bar.draw(self.screen)
            self.handle_inputs()

            pygame.display.flip()
            self.dt = self.clock.tick() / 1000.0
            self.t += self.dt
