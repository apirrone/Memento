import chromadb
import json
from pmr.process import draw_results
import cv2
from pmr.utils import Reader
import os


class Query:
    def __init__(self):
        self.cache_path = os.path.join(os.environ["HOME"], ".cache", "pmr")
        self.client = chromadb.PersistentClient(
            path=os.path.join(self.cache_path, "pmr_db")
        )
        self.collection = self.client.get_collection(name="pmr_db")
        self.reader = Reader(os.path.join(self.cache_path, "0.mp4"))

    def query_db(self, input):
        results = self.collection.query(query_texts=[input], n_results=2)
        tmp_client = chromadb.Client()
        for i, id in enumerate(results["ids"][0]):
            doc = results["documents"][0][i]
            doc = json.loads(doc)

            col = tmp_client.create_collection(name="tmp_" + str(i))
            for i, s in enumerate(doc):
                col.add(documents=[json.dumps(s)], ids=[str(i)])

            n_results = 5
            res = col.query(query_texts=[input], n_results=n_results)
            n_results = len(res["ids"][0])
            for i in range(n_results):
                r = json.loads(res["documents"][0][i])
                frame = self.reader.get_frame(int(id))
                im = draw_results([r], frame)
                cv2.imwrite("query_" + str(i) + ".png", im)
