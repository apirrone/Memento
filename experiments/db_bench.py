import numpy as np
import chromadb
import os
import time

NB_WORDS = 100

word_file = "/usr/share/dict/words"
WORDS = open(word_file).read().splitlines()


def random_word():
    return WORDS[np.random.randint(len(WORDS))]


cache_path = "/tmp/cache_db_bench/"
os.system("rm -rf " + cache_path + "/*")
client = chromadb.PersistentClient(path=os.path.join(cache_path, "db_bench"))

collection = client.get_or_create_collection(name="db_bench")

# =========================
# Option 1 : one word = 1 document

docs = []
ids = []
for i in range(NB_WORDS):
    docs.append(random_word())
    ids.append(str(i))

start = time.time()
collection.add(documents=docs, ids=ids)
print(
    "Added",
    NB_WORDS,
    "words as independant documents in",
    time.time() - start,
    "seconds",
)

# Does it take the same time as the db gets bigger ?
# No
# 8-10 seconds for 200 independant words
# =========================

# =========================
# Option 2 : same number of words, but a few paragraphs
NB_PARAGRAPHS = 20
words = []
docs = []
ids = []
for i in range(NB_WORDS):
    words.append(random_word())

# merge into NB_PARAGRAPHS paragraphs
for i in range(NB_PARAGRAPHS):
    docs.append(
        " ".join(
            words[i * NB_WORDS // NB_PARAGRAPHS : (i + 1) * NB_WORDS // NB_PARAGRAPHS]
        )
    )
    ids.append(str(i + NB_WORDS))

start = time.time()
collection.add(documents=docs, ids=ids)
print(
    "Added",
    NB_WORDS,
    "words as",
    NB_PARAGRAPHS,
    "paragraphs in",
    time.time() - start,
    "seconds",
)
