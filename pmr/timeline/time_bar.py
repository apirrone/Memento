from pmr.timeline.icon_getter import IconGetter
import pmr.utils as utils
import cv2
import numpy as np
import pygame
import datetime


class TimeBar:
    def __init__(self, frame_getter):
        self.frame_getter = frame_getter
        self.nb_frames = self.frame_getter.nb_frames
        self.metadata = self.frame_getter.metadata
        ws = self.frame_getter.window_size
        self.w = ws[0] - ws[0] // 5
        self.h = ws[1] // 40
        self.x = ws[0] // 10
        self.y = ws[1] - self.h - ws[1] // 10

        self.ig = IconGetter(size=self.h)

        self.apps = {}
        self.today = datetime.datetime.now().strftime("%Y-%m-%d")

        self.build()

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

    def get_frame_i(self, mouse_pos):
        return int((mouse_pos[0] - self.x) / self.w * self.nb_frames)

    def draw_cursor(self, screen, cursor_pos):
        pygame.draw.line(
            screen,
            (255, 255, 255),
            (self.x + (cursor_pos / self.nb_frames) * self.w, self.y - self.h),
            (self.x + (cursor_pos / self.nb_frames) * self.w, self.y + self.h * 2),
            5,
        )

    def draw_bar(self, screen, mouse_pos, current_frame_i):
        segments = []
        last_app = self.metadata[str(0)]["window_title"]
        segments.append({"app": last_app, "start": 0, "end": 0})
        for i in range(self.nb_frames):
            app = self.metadata[str(i)]["window_title"]

            segments[-1]["end"] = i
            if app != last_app:
                segments.append({"app": app, "start": i, "end": i})
            last_app = app

        for segment in segments:
            app = segment["app"]
            start = segment["start"]
            end = segment["end"]
            middle = (start + end) / 2
            seg_x = self.x + (start / self.nb_frames) * self.w
            seg_w = (end - start) / self.nb_frames * self.w

            pygame.draw.rect(
                screen,
                self.apps[app]["color"],
                (seg_x, self.y, seg_w, self.h),
                border_radius=self.h // 4,
            )

        for segment in segments:
            app = segment["app"]
            start = segment["start"]
            end = segment["end"]
            middle = (start + end) / 2
            seg_x = self.x + (start / self.nb_frames) * self.w
            seg_w = (end - start) / self.nb_frames * self.w

            if self.apps[app]["icon_small"] is not None:
                if start <= current_frame_i <= end or utils.in_rect(
                    (seg_x, self.y, seg_w, self.h), mouse_pos
                ):
                    screen.blit(
                        self.apps[app]["icon_big"],
                        (
                            self.x + (middle / self.nb_frames) * self.w - self.ig.size,
                            self.y - self.ig.size // 2,
                        ),
                    )

                else:
                    screen.blit(
                        self.apps[app]["icon_small"],
                        (
                            self.x
                            + (middle / self.nb_frames) * self.w
                            - self.ig.size // 2,
                            self.y,
                        ),
                    )

    def draw_preview(self, screen, mouse_pos):
        if not utils.in_rect((self.x, self.y, self.w, self.h), mouse_pos):
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
        if not utils.in_rect((self.x, self.y, self.w, self.h), mouse_pos):
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

    def draw(self, screen, current_frame_i, mouse_pos):
        self.draw_preview(screen, mouse_pos)
        self.draw_bar(screen, mouse_pos, current_frame_i)
        self.draw_cursor(screen, current_frame_i)
        self.draw_time(screen, mouse_pos)
