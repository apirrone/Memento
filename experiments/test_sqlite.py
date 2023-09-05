import sqlite3

conn = sqlite3.connect("test.db")

conn.execute(
    """CREATE TABLE FRAME
        (ID INT PRIMARY KEY NOT NULL,
        VIDEO_ID INT NOT NULL,
        WINDOW_TITLE TEXT NOT NULL,
        TIME DATETIME NOT NULL);
"""
)
conn.execute(
    """CREATE TABLE CONTENT
        (ID INT PRIMARY KEY NOT NULL,
        TEXT TEXT NOT NULL);
"""
)
print("ok")

# cursor = conn.cursor()
# cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
# print(cursor.fetchall())
