from pmr.timeline.icon_getter import IconGetter
import pmr.utils as utils
import cv2
import numpy as np
import pygame
import datetime


# TODO metada cache too
class TimeBar:
    def __init__(self, frame_getter):
        self.frame_getter = frame_getter
        self.nb_frames = self.frame_getter.nb_frames
        self.metadata = self.frame_getter.metadata
        self.show_bar = True

        # Actual graphical window size
        ws = self.frame_getter.window_size
        self.h = ws[1] // 40
        self.x = 20
        self.y = ws[1] - self.h - ws[1] // 10
        self.w = ws[0] - self.x * 2

        # Time window size
        self.tws = min(utils.TIME_WINDOW_SIZE, self.nb_frames)
        self.frame_offset = 0  # from the right
        self.compute_time_window()  # To be called when frame_offset changes

        self.current_frame_i = self.tw_end - 1

        self.ig = IconGetter(size=self.h)

        self.apps = {}
        self.today = datetime.datetime.now().strftime("%Y-%m-%d")

        self.build()

    def compute_time_window(self):
        self.tw_end = self.nb_frames - self.frame_offset
        self.tw_start = self.tw_end - self.tws

    def get_friendly_date(self, date):
        day = date.split(" ")[0]
        hr = date.split(" ")[1]
        if day == self.today:
            return "Today" + " " + hr
        elif day == (datetime.datetime.now() - datetime.timedelta(days=1)).strftime(
            "%Y-%m-%d"
        ):
            return "Yesterday" + " " + hr
        elif day == (datetime.datetime.now() - datetime.timedelta(days=2)).strftime(
            "%Y-%m-%d"
        ):
            return "2 days ago" + " " + hr
        else:
            return date

    def build(self):
        for i in range(self.nb_frames):
            app = self.metadata[str(i)]["window_title"]
            if app not in self.apps:
                self.apps[app] = {}
                self.apps[app]["color"] = tuple(np.random.randint(0, 255, size=3))
                icon_small, icon_big = self.ig.lookup_icon(app)
                self.apps[app]["icon_small"] = icon_small
                self.apps[app]["icon_big"] = icon_big

    # TODO adjust time bar so that the cursor is visible when jumping that way
    def set_current_frame_i(self, frame_i):
        # nb_moves = frame_i - self.current_frame_i
        # dir = 1 if nb_moves > 0 else -1
        # print(self.current_frame_i, frame_i, nb_moves)
        # for _ in range(nb_moves):
        #     self.move_cursor(dir)
        # # self.move_cursor(nb_moves)
        self.current_frame_i = frame_i

    def move_cursor(self, delta):
        self.current_frame_i = max(
            self.tw_start, min(self.tw_end - 1, self.current_frame_i + delta)
        )

        if self.current_frame_i < self.tw_start + 20:
            self.frame_offset = min(self.nb_frames - self.tws, self.frame_offset + 1)
            self.compute_time_window()

        if self.current_frame_i > self.tw_end - 20:
            self.frame_offset = max(0, self.frame_offset - 1)
            self.compute_time_window()

    def get_frame_i(self, mouse_pos):
        return int((mouse_pos[0] - self.x) / self.w * self.tws) + self.tw_start

    def hover(self, mouse_pos):
        return utils.in_rect((self.x, self.y, self.w, self.h), mouse_pos)

    def draw_cursor(self, screen):
        cursor_x = self.x + ((self.current_frame_i - self.tw_start) / self.tws) * self.w
        pygame.draw.line(
            screen,
            (255, 255, 255),
            (cursor_x, self.y - self.h),
            (cursor_x, self.y + self.h * 2),
            5,
        )

    def draw_bar(self, screen, mouse_pos):
        segments = []

        # Warning, it's backwards
        last_app = self.metadata[str(self.tw_end)]["window_title"]
        segments.append({"app": last_app, "start": 0, "end": self.tw_end})
        for i in range(self.tw_end, self.tw_start, -1):
            app = self.metadata[str(i)]["window_title"]

            segments[-1]["start"] = i  # current segment
            if app != last_app:
                segments.append({"app": app, "start": i, "end": i})
            last_app = app

        for segment in segments:
            app = segment["app"]
            start = segment["start"] - self.tw_start
            end = segment["end"] - self.tw_start
            middle = (start + end) / 2
            seg_x = self.x + (start / self.tws) * self.w
            seg_w = (end - start) / self.tws * self.w

            pygame.draw.rect(
                screen,
                self.apps[app]["color"],
                (seg_x, self.y, seg_w, self.h),
                border_radius=self.h // 4,
            )

        for segment in segments:
            app = segment["app"]
            start = segment["start"] - self.tw_start
            end = segment["end"] - self.tw_start
            middle = (start + end) / 2
            seg_x = self.x + (start / self.tws) * self.w
            seg_w = (end - start) / self.tws * self.w

            if self.apps[app]["icon_small"] is not None:
                if start <= self.current_frame_i <= end or utils.in_rect(
                    (seg_x, self.y, seg_w, self.h), mouse_pos
                ):
                    screen.blit(
                        self.apps[app]["icon_big"],
                        (
                            self.x + (middle / self.tws) * self.w - self.ig.size,
                            self.y - self.ig.size // 2,
                        ),
                    )

                else:
                    screen.blit(
                        self.apps[app]["icon_small"],
                        (
                            self.x + (middle / self.tws) * self.w - self.ig.size // 2,
                            self.y,
                        ),
                    )

    def draw_preview(self, screen, mouse_pos):
        if not self.hover(mouse_pos):
            return
        frame_i = self.get_frame_i(mouse_pos)
        frame = self.frame_getter.get_frame(frame_i, raw=True)

        frame = cv2.resize(frame, (0, 0), fx=0.2, fy=0.2)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB).swapaxes(0, 1)

        surf = pygame.surfarray.make_surface(frame)
        screen.blit(
            surf,
            [mouse_pos[0], self.y] - np.array([frame.shape[0] // 2, frame.shape[1]]),
        )

    def draw_time(self, screen, mouse_pos):
        if not self.hover(mouse_pos):
            return
        frame_i = self.get_frame_i(mouse_pos)
        time = self.metadata[str(frame_i)]["time"].strip('"')
        time = self.get_friendly_date(time)
        font = pygame.font.SysFont("Arial", 20)
        text = font.render(time, True, (0, 0, 0))
        text_size = text.get_size()
        border = 10
        pygame.draw.rect(
            screen,
            (255, 255, 255),
            (
                mouse_pos[0] - text_size[0] // 2 - border,
                self.y + text_size[1] + self.h - border,
                text_size[0] + border * 2,
                text_size[1] + border * 2,
            ),
            border_radius=self.h // 2,
        )

        screen.blit(
            text, [mouse_pos[0] - text_size[0] // 2, self.y + text_size[1] + self.h]
        )
        pygame.draw.line(
            screen,
            (255, 255, 255),
            (mouse_pos[0], self.y),
            (mouse_pos[0], self.y + self.h),
            5,
        )

    def show(self):
        self.show_bar = True

    def hide(self):
        self.show_bar = False

    def draw(self, screen, mouse_pos):
        if self.show_bar:
            self.draw_preview(screen, mouse_pos)
            self.draw_bar(screen, mouse_pos)
            self.draw_cursor(screen)
            self.draw_time(screen, mouse_pos)
