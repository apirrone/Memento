import pygame
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from langchain.chat_models import ChatOpenAI
from langchain.vectorstores import Chroma
from langchain.prompts import PromptTemplate
from langchain.embeddings import OpenAIEmbeddings
import os
import multiprocessing
from multiprocessing import Queue
import json
import pmr.timeline.text_utils as text_utils
import pmr.utils as utils
import cv2


# Chat window on the right of the screen
class Chat:
    def __init__(self, frame_getter):
        self.cache_path = os.path.join(os.environ["HOME"], ".cache", "pmr")

        self.frame_getter = frame_getter

        ws = self.frame_getter.window_size
        self.w = ws[0] // 3
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
        self.bubbles_vertical_space = 10
        self.bubble_inner_margin = 10
        self.chatbox_margin = 10
        self.q_color = (121, 189, 139)
        self.a_color = (113, 157, 222)

        self.frame_peek_w = int(self.w / 3 - self.chatbox_margin * 2)
        self.frames_peeks_rects = {}
        self.frame_peek_hovered_id = None

        # For debug
        # for i in range(1):
        #     frames = {"1": None, "2": None, "3": None}  # , "4": None, "5": None}
        #     for frame_id in frames.keys():
        #         frame = cv2.resize(
        #             self.frame_getter.get_frame(int(frame_id)),
        #             (self.frame_peek_w, self.frame_peek_w),
        #         )
        #         frame = pygame.surfarray.make_surface(frame)
        #         frames[frame_id] = frame
        #     self.chat_history.append(
        #         {
        #             "question": "What is the meaning of life ? alze jalzke jazle kjazlek ajzel akzej alzkej alzekjalze kjalzek jalzek ajzel kajezl akejalze ",
        #             "answer": "42 aaakze azke az lekajzelajze alzkej alzek jalzekajel kajzelakzej alzekj alzkejaz e azj ejhalze jalze kjazle kazje",
        #             "frames": frames,
        #         }
        #     )

        # answer = """Answer: To use ConversationalRetrievalChain in LangChain, you may follow the steps below:

        # 1. Create a conversation history variable: `chat_history = []`

        # 2. Create a query: `query = "what did the president say about Ketanji Brown Jackson"`

        # 3. Perform retrieval using the ConversationRetrievalChain:
        # """
        # for i in range(20):
        #     self.chat_history.append(
        #         {
        #             "question": "How to use ConversationalRetrievalChain in LangChain ?",
        #             "answer": answer,
        #         }
        #     )

        self.chromadb = Chroma(
            persist_directory=self.cache_path,
            embedding_function=OpenAIEmbeddings(),
            collection_name="pmr_db",
        )

        self.memory = ConversationBufferMemory(
            memory_key="chat_history", return_messages=True, input_key="question"
        )
        self.retriever = self.chromadb.as_retriever()

        # Define prompt
        template = """Use the following pieces of context and metadata to answer the question at the end. Answer in the same language the question was asked.
        If you don't know the answer, just say that you don't know, don't try to make up an answer.
        You will format your answer in json, with the keys "answer" and "frames_ids". 
        The value of "answer" will be the answer to the question, and the value of "frames_ids" will be a list of frame_ids from which you got the information from using the metadata.
        Use three sentences maximum and keep the answer as concise as possible.

        Context: {context}
        Question: {question}
        Metadata: {md}

        Helpful Answer:"""

        # prompt = PromptTemplate.from_template(template)

        prompt = PromptTemplate(
            input_variables=["question", "context", "md"], template=template
        )

        # self.qa = ConversationalRetrievalChain.from_llm(
        #     ChatOpenAI(model_name="gpt-4", temperature=0.8),
        #     self.retriever,
        #     memory=self.memory,
        #     verbose=True,
        # )
        self.qa = ConversationalRetrievalChain.from_llm(
            ChatOpenAI(model_name="gpt-4", temperature=0.8),
            self.retriever,
            memory=self.memory,
            verbose=True,
            combine_docs_chain_kwargs={"prompt": prompt},
        )

        self.query_queue = Queue()
        self.answer_queue = Queue()
        multiprocessing.Process(target=self.process_chat_query, args=()).start()

    def scroll(self, dir):
        if len(self.chat_history) > 0:
            self.y_offset = min(0, self.y_offset + dir * 10)

    def hover(self, mouse_pos):
        return utils.in_rect((self.x, self.y, self.w, self.h), mouse_pos)

    def activate(self):
        self.active = True

    def deactivate(self):
        self.active = False
        self.input = ""

    def process_chat_query(self):
        print("Starting chat query process")
        while True:
            q = self.query_queue.get()
            inp = q["input"]

            print("Query:", inp)
            print("Retrieving relevant documents")
            docs = self.retriever.get_relevant_documents(inp)
            print("done")
            md = {}
            for doc in docs:
                frame_metadata = json.loads(doc.metadata["frame_metadata"])
                frame_id = doc.metadata["id"]
                md[frame_id] = {
                    "window_title": frame_metadata["window_title"],
                    "date": frame_metadata["time"],
                }

            result = self.qa(inputs={"question": inp, "md": md})
            result = json.loads(result["answer"])
            print("Answer:", result["answer"])
            print("frames_ids:", result["frames_ids"])
            self.answer_queue.put(result)

    def event(self, event):
        if not self.active:
            return None
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
            return None
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.frame_peek_hovered_id is not None:
                return self.frame_peek_hovered_id

    def query_llm(self):
        if len(self.input) > 0:
            chat_history_entry = {}
            chat_history_entry["question"] = self.input
            chat_history_entry["answer"] = None
            chat_history_entry["frames"] = {}
            self.chat_history.append(chat_history_entry)
            self.query_queue.put({"input": self.input})
            self.input = ""

    def wrap_text_input(self, text, max_width):
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

    def handle_frames_peeks(self, screen):
        self.frame_peek_hovered_id = None
        for frame_id, frame_peek_rect in self.frames_peeks_rects.items():
            if utils.in_rect(frame_peek_rect, pygame.mouse.get_pos()):
                pygame.draw.rect(
                    screen,
                    self.a_color,
                    frame_peek_rect,
                    width=10,
                )
                self.frame_peek_hovered_id = frame_id

    def draw_frames_peeks(self, screen, frames, start_y):
        height = 0
        frames_peeks_rects = {}
        if frames is None or len(frames) == 0:
            return height, frames_peeks_rects

        i = 0
        x = self.x + self.chatbox_margin
        y = start_y
        for frame_id, frame_surf in frames.items():
            if i % 3 == 0 and i != 0:
                x = self.x + self.chatbox_margin
                height += self.frame_peek_w + self.bubble_inner_margin
                y += height
            elif i != 0:
                x += self.frame_peek_w + self.bubble_inner_margin

            screen.blit(frame_surf, (x, y))
            frames_peeks_rects[frame_id] = (x, y, self.frame_peek_w, self.frame_peek_w)
            i += 1
        height += self.frame_peek_w + self.bubble_inner_margin
        return height, frames_peeks_rects

    def draw_bubble(self, screen, text, y, question=True, frames=None):
        color = (0, 0, 0)
        if question:
            x = self.x + self.chatbox_margin
        else:
            x = self.x + self.chatbox_margin * 2

        text_w = self.w - self.bubble_inner_margin * 4 - self.chatbox_margin * 2
        bubble_w = self.w - self.chatbox_margin * 4
        text_height = text_utils.get_text_height(text, self.font, text_w)
        bubble_height = text_height + self.bubble_inner_margin * 4

        pygame.draw.rect(
            screen,
            self.q_color if question else self.a_color,
            (x, y, bubble_w, bubble_height),
            border_radius=10,
        )

        text_utils.render_text(
            screen,
            text,
            self.font,
            x + self.bubble_inner_margin,
            y + self.bubble_inner_margin,
            text_w,
            color,
        )

        peeks_height, frames_peeks_rects = self.draw_frames_peeks(
            screen, frames, y + bubble_height + self.bubble_inner_margin * 2
        )
        return (
            bubble_height + peeks_height + self.bubble_inner_margin * 2,
            frames_peeks_rects,
        )

    def draw_chat_history(self, screen):
        prev_height = 0
        self.frames_peeks_rects = {}
        for i, chat_history_entry in enumerate(self.chat_history):
            question = chat_history_entry["question"]

            if chat_history_entry["answer"] is None:
                if pygame.time.get_ticks() % 1000 < 333:
                    answer = "."
                elif 333 < pygame.time.get_ticks() % 1000 < 666:
                    answer = ".."
                else:
                    answer = "..."
            else:
                answer = chat_history_entry["answer"]
                # answer += "\n" + str(list(chat_history_entry["frames"].keys()))

            q_y = prev_height + self.y_offset + self.y + self.input_box_borders
            q_height, _ = self.draw_bubble(screen, question, q_y, question=True)
            a_y = q_y + q_height + self.bubbles_vertical_space
            a_height, frames_peeks_rects = self.draw_bubble(
                screen,
                answer,
                a_y,
                question=False,
                frames=chat_history_entry["frames"],
            )

            for frame_id, frame_peek_rect in frames_peeks_rects.items():
                self.frames_peeks_rects[frame_id] = frame_peek_rect

            prev_height += q_height + a_height + self.bubbles_vertical_space * 4

    def draw_input_box(self, screen):
        text_lines = self.wrap_text_input(self.input, self.w)
        text_height = len(text_lines) * self.font_size

        pygame.draw.rect(
            screen,
            (50, 50, 50),
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
        if pygame.time.get_ticks() % 1000 < 500:
            cursor_x = self.font.size(text_lines[-1])[0] + 5
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
        try:
            result = self.answer_queue.get(False)
            self.chat_history[-1]["answer"] = result["answer"]
            frames_ids = result["frames_ids"]
            for frame_id in frames_ids:
                frame = cv2.resize(
                    self.frame_getter.get_frame(int(frame_id)),
                    (self.frame_peek_w, self.frame_peek_w),
                )
                frame = pygame.surfarray.make_surface(frame)
                self.chat_history[-1]["frames"][frame_id] = frame

        except Exception:
            pass
        if not self.active:
            return

        surf = pygame.Surface((self.w, self.h))
        surf.set_alpha(200)
        surf.fill((255, 255, 255))

        pygame.draw.rect(surf, (255, 255, 255), (self.x, self.y, self.w, self.h))
        screen.blit(surf, (self.x, self.y))

        self.draw_chat_history(screen)
        self.handle_frames_peeks(screen)
        self.draw_input_box(screen)
