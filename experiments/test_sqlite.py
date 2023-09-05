import sqlite3
import datetime
import numpy as np

conn = sqlite3.connect("test.db")

NB_WORDS = 100

word_file = "/usr/share/dict/words"
WORDS = open(word_file).read().splitlines()


def random_word():
    return WORDS[np.random.randint(len(WORDS))]


def create_db():
    conn.execute(
        """CREATE TABLE FRAME
            (id INT PRIMARY KEY NOT NULL,
            video_id INT NOT NULL,
            window_title TEXT NOT NULL,
            time DATETIME NOT NULL);
    """
    )
    conn.execute(
        """CREATE TABLE CONTENT
            (id INTEGER PRIMARY KEY AUTOINCREMENT,
            frame_id INT NOT NULL,
            text TEXT NOT NULL,
            x INT NOT NULL,
            y INT NOT NULL,
            w INT NOT NULL,
            h INT NOT NULL
            );
    """
    )
    for i in range(100):
        conn.execute(
            "INSERT INTO FRAME (id, video_id, window_title, time) VALUES (?, ?, ?, ?)",
            (str(i), 1, "google-chrome", datetime.datetime.now()),
        )

    for i in range(100):
        word = str(random_word())
        conn.execute("INSERT INTO CONTENT (frame_id, text, x, y, w, h) VALUES (?, ?, ?, ?, ?, ?)", (0, word, 1, 2, 3, 4))

    conn.execute("""CREATE VIRTUAL TABLE CONTENT_FTS USING fts5(frame_id, text, x, y, w, h)""")
    conn.execute("""INSERT INTO CONTENT_FTS SELECT frame_id, text, x, y, w, h FROM CONTENT""")

    conn.execute("""CREATE TRIGGER insert_content 
                 AFTER INSERT ON CONTENT 
                 BEGIN
                 INSERT INTO CONTENT_FTS (frame_id, text, x, y, w, h) 
                 VALUES (new.frame_id, new.text, new.x, new.y, new.w, new.h);
                 end;
                 """)

    conn.commit()
    print("DB created and populated")


# create_db()
cursor = conn.execute("SELECT * FROM CONTENT_FTS WHERE text MATCH ?", ("a*", ))
for row in cursor:
    print(row)
