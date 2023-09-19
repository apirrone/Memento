import pygame
import pygame_textinput
from memento.db import Db
import numpy as np
import memento.timeline.text_utils as text_utils
from thefuzz import fuzz
import memento.utils as utils


class SearchBar:
    def __init__(self, frame_getter):
        self.frame_getter = frame_getter
        self.db = Db()

        self.ws = self.frame_getter.window_size
        # self.x = self.ws[0] // 10
        # self.y = self.ws[1] // 10
        # self.w = self.ws[0] - self.ws[0] // 5
        # self.h = self.ws[1] // 20

        self.x = 0
        self.y = 0
        self.w = self.ws[0] // 4
        self.h = self.ws[1] // 20
        self.active = False
        self.found = False
        self.input_changed = False

        self.list_entry_h = self.ws[1] // 20
        self.list_entry_border = 5
        self.selected_entry_frame_i = None
        self.font_size = 20
        self.font = pygame.font.SysFont("Arial", self.font_size)

        self.y_offset = self.h

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
        # draw a black border
        pygame.draw.rect(
            screen,
            (0, 0, 0),
            (self.x, self.y, self.w, self.h),
            width=5,
            # border_radius=self.h // 4,
        )

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

    # TODO too long to compute as is.
    # Should be better with segments
    def remove_similar_annotations(self, annotations):
        filtered_annotations = {}
        annotations_frames = []
        annotations_texts = []
        for key, annotations_list in annotations.items():
            for annotation in annotations_list:
                annot1 = annotation["text"]
                if len(annotations_texts) == 0:
                    annotations_frames.append(key)
                    annotations_texts.append(annotation["text"])
                    continue
                for annot2 in annotations_texts:
                    if fuzz.ratio(annot1, annot2) < 30:
                        annotations_frames.append(key)
                        annotations_texts.append(annotation["text"])

        print(annotations_frames)

    def draw_results_list(self, screen):
        annotations = self.frame_getter.get_annotations()
        # self.remove_similar_annotations(annotations)

        pygame.draw.rect(
            screen,
            (255, 255, 255),
            (self.x, self.y, self.w, self.ws[1]),
            border_radius=self.h // 4,
        )
        # draw a black border
        pygame.draw.rect(
            screen,
            (0, 0, 0),
            (self.x, self.y, self.w, self.ws[1]),
            width=5,
            # border_radius=self.h // 4,
        )
        index = 0
        for key, annotations_list in annotations.items():
            for annotation in annotations_list:
                text = annotation["text"]
                text = text.replace("\n", " ")
                rect = (
                    self.x,
                    self.y + self.y_offset + index * self.list_entry_h,
                    self.w,
                    self.list_entry_h,
                )
                if not utils.rect_in_rect(
                    rect, (0, 0, self.ws[0], self.ws[1] + rect[3])
                ):
                    index += 1
                    continue

                # y = self.y  + self.y_offset + index * self.list_entry_h,
                pygame.draw.rect(
                    screen,
                    (0, 0, 0),
                    rect,
                    width=2,
                )

                text_utils.render_text(
                    screen,
                    text[: self.w // 10],  # TODO compute this properly
                    self.font,
                    self.x + self.list_entry_border,
                    self.y
                    + self.y_offset
                    + index * self.list_entry_h
                    + self.list_entry_border,
                    1000000,
                    (0, 0, 0),
                )
                if int(key) == int(self.frame_getter.current_displayed_frame_i):
                    pygame.draw.rect(
                        screen,
                        (255, 0, 0),
                        rect,
                        width=2,
                    )

                if utils.in_rect(rect, pygame.mouse.get_pos()):
                    pygame.draw.rect(
                        screen,
                        (0, 255, 0),
                        rect,
                        width=5,
                    )
                    self.selected_entry_frame_i = int(key)

                index += 1
                # break

    def hover(self, mouse_pos):
        return utils.in_rect((self.x, self.y, self.w, self.ws[1]), mouse_pos)

    def scroll(self, dir):
        if len(self.frame_getter.annotations) > 0:
            self.y_offset = min(self.h, self.y_offset + dir * 10)

    def draw_app_filter(self, screen):
        pass

    def draw(self, screen):
        if not self.active:
            return
        self.draw_results_list(screen)
        self.draw_bar(screen)

    def start_query(self):
        print("start query")
        self.frame_getter.clear_annotations()
        self.y_offset = self.h
        query_input = self.textinput.value

        results = self.db.search(query_input)

        self.frame_getter.set_annotations(results)
        if len(results) > 0:
            self.found = True
            self.frame_getter.nb_results = len(results)
        else:
            self.found = False
            self.frame_getter.nb_results = -1

    def events(self, events):
        self.textinput.update(events)
        found = False
        frame_i = None
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
                            found = True
                    self.input_changed = False
                elif self.active:
                    self.input_changed = True
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    frame_i = self.selected_entry_frame_i
        return found, frame_i
