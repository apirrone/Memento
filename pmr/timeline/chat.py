import pygame
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from langchain.chat_models import ChatOpenAI
from langchain.vectorstores import Chroma
from langchain.prompts import PromptTemplate
from pmr.query_db import Query
from langchain.embeddings import OpenAIEmbeddings
import os


# Chat window on the right of the screen
class Chat:
    def __init__(self, frame_getter):
        self.cache_path = os.path.join(os.environ["HOME"], ".cache", "pmr")

        ws = frame_getter.window_size
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
        self.bubbles_space = 10
        self.q_color = (121, 189, 139)
        self.a_color = (113, 157, 222)

        # for i in range(20):
        #     self.chat_history.append(
        #         {
        #             "question": "What is the meaning of life ? alze jalzke jazle kjazlek ajzel akzej alzkej alzekjalze kjalzek jalzek ajzel kajezl akejalze ",
        #             "answer": "42 aaakze azke az lekajzelajze alzkej alzek jalzekajel kajzelakzej alzekj alzkejaz e azj ejhalze jalze kjazle kazje",
        #         }
        #     )
        # answer = """Answer: To use ConversationalRetrievalChain in LangChain, you may follow the steps below:

        # 1. Create a conversation history variable: `chat_history = []`

        # 2. Create a query: `query = "what did the president say about Ketanji Brown Jackson"`

        # 3. Perform retrieval using the ConversationRetrievalChain:
        # """
        # self.chat_history.append(
        #     {
        #         "question": "How to use ConversationalRetrievalChain in LangChain ?",
        #         "answer": answer,
        #     }
        # )

        self.chromadb = Chroma(
            persist_directory=self.cache_path,
            embedding_function=OpenAIEmbeddings(),
            collection_name="pmr_db",
        )

        self.memory = ConversationBufferMemory(
            memory_key="chat_history", return_messages=True
        )
        self.retriever = self.chromadb.as_retriever()

        # Define prompt
        template = """Use the following pieces of context to answer the question at the end.
        If you don't know the answer, just say that you don't know, don't try to make up an answer.
        Use three sentences maximum and keep the answer as concise as possible.
        Always start your answer with "Understood Sir: ".
        At the end of your answer you will tell the following informations from the relevant context:
        "date: "
        "window name: ".
        {context}
        Question: {question}
        Helpful Answer:"""

        prompt = PromptTemplate.from_template(template)

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

    def scroll(self, dir):
        self.y_offset = min(0, self.y_offset + dir * 10)

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
            docs = self.retriever.get_relevant_documents(self.input)
            print("Relevant documents:", docs)

            result = self.qa({"question": self.input})
            print("Answer:", result["answer"])
            chat_history_entry["answer"] = result["answer"]
            self.input = ""

            self.chat_history.append(chat_history_entry)

    # TODO do better, need to take into account '\n'
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

    def draw_bubble(self, screen, lines, y, question=True):
        color = (0, 0, 0)
        if question:
            x = self.x + self.input_box_borders * 2
        else:
            x = self.x + self.input_box_borders * 3

        pygame.draw.rect(
            screen,
            self.q_color if question else self.a_color,
            (
                x - self.input_box_borders,
                y - self.input_box_borders,
                self.w - 20 - self.input_box_borders,
                len(lines) * self.font_size + self.input_box_borders * 3,
            ),
            border_radius=10,
        )

        for i, line in enumerate(lines):
            text = self.font.render(line, True, color)
            screen.blit(text, (x, y + self.input_box_borders + i * self.font_size))

    def draw_chat_history(self, screen):
        prev_height = 0
        for i, chat_history_entry in enumerate(self.chat_history):
            question = chat_history_entry["question"]
            answer = chat_history_entry["answer"]
            question_lines = self.wrap_text(question, self.w)
            answer_lines = self.wrap_text(answer, self.w)
            question_height = len(question_lines) * self.font_size * 2
            answer_height = len(answer_lines) * self.font_size * 2

            q_y = prev_height + self.y_offset + self.y + self.input_box_borders
            a_y = (
                prev_height
                + question_height
                + self.y_offset
                + self.y
                + self.input_box_borders
                + self.bubbles_space * 2
            )

            self.draw_bubble(screen, question_lines, q_y, question=True)
            self.draw_bubble(screen, answer_lines, a_y, question=False)

            prev_height += question_height + answer_height + self.bubbles_space * 6

    def draw_input_box(self, screen):
        text_lines = self.wrap_text(self.input, self.w)
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

        surf = pygame.Surface((self.w, self.h))
        surf.set_alpha(200)
        surf.fill((255, 255, 255))

        pygame.draw.rect(surf, (255, 255, 255), (self.x, self.y, self.w, self.h))
        screen.blit(surf, (self.x, self.y))

        self.draw_chat_history(screen)
        self.draw_input_box(screen)
