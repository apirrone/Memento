import pygame
from memento.timeline.frame_getter import FrameGetter
from memento.timeline.time_bar import TimeBar
from memento.timeline.search_bar import SearchBar
from memento.timeline.region_selector import RegionSelector
from memento.timeline.chat import Chat
import memento.utils as utils
import pyperclip
from memento.timeline.ui import PopUpManager, Plot
import time


class Timeline:
    def __init__(self):
        self.window_size = utils.RESOLUTION

        # Faster than pygame.init()
        pygame.display.init()
        pygame.font.init()

        self.screen = pygame.display.set_mode(
            self.window_size, flags=pygame.SRCALPHA + pygame.NOFRAME
        )  # +pygame.FULLSCREEN)
        # +pygame.HIDDEN
        pygame.key.set_repeat(500, 50)
        self.clock = pygame.time.Clock()

        self.ctrl_pressed = False

        self.update()

        self.t = 0
        self.dt = 1
        self.fps = 0
        self.fps_plot = Plot(300, self.window_size[0] - 310, 50, 300, 100, (255, 0, 0))

        self.is_recording = False
        self.last_is_recording_update = 0

    def update(self):
        self.frame_getter = FrameGetter(self.window_size)
        self.time_bar = TimeBar(self.frame_getter)
        self.search_bar = SearchBar(self.frame_getter)
        self.region_selector = RegionSelector()
        self.popup_manager = PopUpManager()
        self.chat = Chat(self.frame_getter)

    def draw_current_frame(self):
        frame = self.frame_getter.get_frame(self.time_bar.current_frame_i)
        surf = pygame.surfarray.make_surface(frame).convert()
        self.screen.blit(surf, (0, 0))

    # TODO This is a mess
    def handle_inputs(self):
        found = False
        ret_frame = None
        mouse_wheel = 0
        events = pygame.event.get()
        found = self.search_bar.events(events)
        ret_frame = self.chat.events(events)
        for event in events:
            if event.type == pygame.MOUSEWHEEL:
                mouse_wheel = event.x - event.y
                if not self.ctrl_pressed:
                    if self.chat.active and self.chat.hover(pygame.mouse.get_pos()):
                        self.chat.scroll(event.y)
                    else:
                        self.time_bar.move_cursor((mouse_wheel))
                    self.region_selector.reset()
                    self.frame_getter.clear_annotations()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if self.time_bar.hover(event.pos):
                        self.time_bar.set_current_frame_i(
                            self.time_bar.get_frame_i(event.pos)
                        )
                        self.region_selector.reset()
                    elif not self.chat.hover(pygame.mouse.get_pos()):
                        self.search_bar.deactivate()
                        self.region_selector.start(event.pos)
                        self.time_bar.hide()
            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    if self.time_bar.hover(event.pos):
                        continue
                    self.time_bar.show()
                    if self.search_bar.active:
                        continue
                    self.region_selector.end(event.pos)
                    frame = self.frame_getter.get_frame(
                        self.time_bar.current_frame_i
                    ).swapaxes(0, 1)
                    res = self.region_selector.region_ocr(frame)
                    if res is None:
                        continue
                    self.frame_getter.clear_annotations()
                    self.frame_getter.add_annotation(self.time_bar.current_frame_i, res)
                    if not self.time_bar.hover(event.pos):
                        self.popup_manager.add_popup(
                            "Ctrl + C to copy text",
                            (50, 70),
                            2,
                        )
            if event.type == pygame.KEYDOWN:
                if not self.chat.active and not self.search_bar.active:
                    if event.key == pygame.K_LEFT:
                        self.time_bar.move_cursor(-1)
                    if event.key == pygame.K_RIGHT:
                        self.time_bar.move_cursor(1)
                if event.key == pygame.K_ESCAPE:
                    self.region_selector.reset()
                    self.frame_getter.clear_annotations()
                    self.chat.deactivate()
                if event.key == pygame.K_RETURN:
                    pass
                if event.key == pygame.K_d:
                    if self.search_bar.active or self.chat.active:
                        continue
                    self.frame_getter.toggle_debug_mode()
                    self.popup_manager.add_popup(
                        "DEBUG MODE ON"
                        if self.frame_getter.debug_mode
                        else "DEBUG MODE OFF",
                        (50, 70),
                        2,
                    )
                if event.mod & pygame.KMOD_CTRL:
                    self.ctrl_pressed = True
                    if event.key == pygame.K_c:
                        text = self.frame_getter.get_annotations_text()
                        pyperclip.copy(text)
                        self.popup_manager.add_popup(
                            "Text copied to clipboard",
                            (50, 70),
                            2,
                        )

                    if event.key == pygame.K_t:
                        self.chat.activate()
                        self.search_bar.deactivate()
            if event.type == pygame.KEYUP:
                self.ctrl_pressed = False

        if self.ctrl_pressed:
            if mouse_wheel != 0:
                self.time_bar.zoom(mouse_wheel)
                self.popup_manager.add_popup(
                    "Zoom : " + str(self.time_bar.tws * 1 / utils.FPS) + "s",
                    (50, 70),
                    2,
                )

        if found:
            self.time_bar.set_current_frame_i(
                self.frame_getter.get_next_annotated_frame_i()
            )

        if ret_frame is not None:
            self.time_bar.set_current_frame_i(int(ret_frame))

        if self.frame_getter.debug_mode:
            self.popup_manager.add_popup(
                "Frame : " + str(self.time_bar.current_frame_i),
                (50, self.window_size[1] - 70),
                0.1,
            )

    def draw_and_update_is_recording(self):
        if time.time() - self.last_is_recording_update > 2:
            self.last_is_recording_update = time.time()
            self.is_recording = utils.recording()

        if self.is_recording:
            if pygame.time.get_ticks() % 1000 < 500:
                radius = 5
                pygame.draw.circle(
                    self.screen,
                    (255, 0, 0),
                    (self.window_size[0] - radius, radius),
                    radius,
                )

    def draw_and_compute_fps(self):
        self.fps = int(1 / self.dt)
        self.fps_plot.add_point(self.fps)

        if self.frame_getter.debug_mode:
            self.popup_manager.add_popup(
                "FPS : " + str(self.fps),
                (self.window_size[0] - 150, 10),
                0.1,
            )

            self.fps_plot.draw(self.screen)

    def run(self):
        while True:
            self.screen.fill((255, 255, 255))
            self.draw_current_frame()
            self.time_bar.draw(self.screen, pygame.mouse.get_pos())
            self.search_bar.draw(self.screen)
            self.chat.draw(self.screen)

            self.handle_inputs()
            self.popup_manager.tick(self.screen)

            if self.search_bar.active:
                self.region_selector.reset()

            self.region_selector.draw(self.screen, pygame.mouse.get_pos())

            self.draw_and_update_is_recording()
            self.draw_and_compute_fps()

            pygame.display.update()
            self.dt = self.clock.tick() / 1000.0
            self.t += self.dt
