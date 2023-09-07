import sqlite3
import os


class Db:
    def __init__(self):
        self.cache_path = os.path.join(os.environ["HOME"], ".cache", "memento")
        db_path = os.path.join(self.cache_path, "memento.db")
        create_tables = False
        if not os.path.isfile(db_path):
            create_tables = True

        self.conn = sqlite3.connect(db_path)

        if not create_tables:
            return

        self.conn.execute(
            """CREATE TABLE FRAME
                (id INT PRIMARY KEY NOT NULL,
                window_title TEXT NOT NULL,
                time DATETIME NOT NULL);
        """
        )
        self.conn.execute(
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
        self.conn.execute(
            """CREATE VIRTUAL TABLE CONTENT_FTS USING fts5(frame_id, text, x, y, w, h)"""
        )

        self.conn.execute(
            """CREATE TRIGGER insert_content 
                    AFTER INSERT ON CONTENT 
                    BEGIN
                    INSERT INTO CONTENT_FTS (frame_id, text, x, y, w, h) 
                    VALUES (new.frame_id, new.text, new.x, new.y, new.w, new.h);
                    end;
                    """
        )

    def add_texts(self, texts, bbs, frame_i, window_title, time):
        self.conn.execute(
            "INSERT INTO FRAME (id, window_title, time) VALUES (?, ?, ?)",
            (str(frame_i), window_title, time),
        )

        for i in range(len(texts)):
            self.conn.execute(
                "INSERT INTO CONTENT (frame_id, text, x, y, w, h) VALUES (?, ?, ?, ?, ?, ?)",
                (frame_i, texts[i], bbs[i]["x"], bbs[i]["y"], bbs[i]["w"], bbs[i]["h"]),
            )

        self.conn.commit()

    def search(self, query):
        cursor = self.conn.execute(
            "SELECT rank, frame_id, text, x, y, w, h FROM CONTENT_FTS WHERE text MATCH ? ORDER BY rank DESC",
            (query,),
        )

        results = {}
        for row in cursor:
            print(row)
            rank = row[0]
            frame_id = str(row[1])
            if frame_id not in results:
                results[frame_id] = []

            results[frame_id].append(
                {
                    "text": row[2],
                    "bb": {"x": row[3], "y": row[4], "w": row[5], "h": row[6]},
                    "score": 1.0,
                }
            )

        return results
