import pygame
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from langchain.chat_models import ChatOpenAI
from langchain.vectorstores import Chroma
from pmr.query_db import Query
from langchain.embeddings import OpenAIEmbeddings
import os


# Chat window on the right of the screen
class Chat:
    def __init__(self, frame_getter):
        self.cache_path = os.path.join(os.environ["HOME"], ".cache", "pmr")

        ws = frame_getter.window_size
        self.w = ws[0] // 5
        self.x = ws[0] - self.w
        self.y = 0
        self.h = ws[1]

        self.active = False
        self.input = ""
        self.font_size = 20
        self.font = pygame.font.SysFont("Arial", self.font_size)

        self.input_box_borders = 10

        self.y_offset = 0
        self.chat_history = []

        self.chromadb = Chroma(
            persist_directory=self.cache_path,
            embedding_function=OpenAIEmbeddings(),
            collection_name="pmr_db",
        )

        self.memory = ConversationBufferMemory(
            memory_key="chat_history", return_messages=True
        )
        self.qa = ConversationalRetrievalChain.from_llm(
            ChatOpenAI(model_name="gpt-4", temperature=0.8),
            self.chromadb.as_retriever(),
            memory=self.memory,
            verbose=False,
        )

    def scroll(self, dir):
        self.y_offset = min(0, self.y_offset+dir*10)
        # self.y_offset += dir * 10

    def activate(self):
        self.active = True

    def deactivate(self):
        self.active = False
        self.input = ""

    def event(self, event):
        if not self.active:
            return
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.deactivate()
            elif event.key == pygame.K_BACKSPACE:
                self.input = self.input[:-1]
            elif event.key == pygame.K_RETURN:
                self.query_llm()
            else:
                try:
                    self.input_changed = True
                    self.input += chr(event.key)
                except Exception:
                    pass
        if event.type == pygame.MOUSEWHEEL:
            self.scroll(event.y)

    def query_llm(self):
        if len(self.input) > 0:
            chat_history_entry = {}
            chat_history_entry["question"] = self.input
            print("Query:", self.input)
            result = self.qa({"question": self.input})
            print("Answer:", result["answer"])
            chat_history_entry["answer"] = result["answer"]
            self.input = ""

            self.chat_history.append(chat_history_entry)

    def wrap_text(self, text, max_width):
        words = text.split(" ")
        lines = []
        line = ""
        for word in words:
            if self.font.size(line + word)[0] > max_width - self.input_box_borders * 2:
                lines.append(line)
                line = ""
            line += word + " "
        lines.append(line)
        return lines

    def draw_chat_history(self, screen):
        prev_height = 0
        for i, chat_history_entry in enumerate(self.chat_history):
            question = chat_history_entry["question"]
            answer = chat_history_entry["answer"]
            question_lines = self.wrap_text(question, self.w)
            answer_lines = self.wrap_text(answer, self.w)
            question_height = len(question_lines) * self.font_size
            answer_height = len(answer_lines) * self.font_size

            question_color = (0, 255, 0)
            answer_color = (0, 0, 255)
            distance_between_questions_and_answers = 20

            for j, line in enumerate(question_lines):
                text = self.font.render(line, True, question_color)
                screen.blit(
                    text,
                    (
                        self.x + self.input_box_borders,
                        self.y
                        + j * self.font_size
                        + i * self.font_size
                        + prev_height
                        + self.y_offset,
                    ),
                )

            for j, line in enumerate(answer_lines):
                text = self.font.render(line, True, answer_color)
                screen.blit(
                    text,
                    (
                        self.x + self.input_box_borders,
                        self.y
                        + j * self.font_size
                        + i * self.font_size
                        + question_height
                        + distance_between_questions_and_answers
                        + prev_height
                        + self.y_offset,
                    ),
                )
            prev_height += (
                question_height + answer_height + distance_between_questions_and_answers
            )

    def draw_input_box(self, screen):
        # at the bottom of the chatbox
        # The text should wrap relative to the width of the input box
        # The height of the input box should be adapted to the height of the text
        text_lines = self.wrap_text(self.input, self.w)
        text_height = len(text_lines) * self.font_size

        pygame.draw.rect(
            screen,
            (0, 0, 0),
            (
                self.x,
                self.y - self.input_box_borders * 2 + self.h - text_height,
                self.w,
                text_height + self.input_box_borders * 2,
            ),
        )

        for i, line in enumerate(text_lines):
            text = self.font.render(line, True, (255, 255, 255))
            screen.blit(
                text,
                (
                    self.x + self.input_box_borders,
                    self.y
                    + self.h
                    - text_height
                    - self.input_box_borders
                    + i * self.font_size,
                ),
            )
        cursor_x = self.font.size(text_lines[-1])[0] + 10
        pygame.draw.rect(
            screen,
            (255, 255, 255),
            (
                self.x + cursor_x,
                self.y
                + self.h
                - text_height
                - self.input_box_borders
                + (len(text_lines) - 1) * self.font_size,
                2,
                self.font_size,
            ),
        )

    # Draw chatbox with input region at the bottom
    def draw(self, screen):
        if not self.active:
            return

        pygame.draw.rect(
            screen,
            (255, 255, 255),
            (self.x, self.y, self.w, self.h),
            border_radius=10,
        )

        self.draw_chat_history(screen)
        self.draw_input_box(screen)
