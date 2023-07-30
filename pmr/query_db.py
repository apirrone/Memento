import chromadb
import json
from pmr.process import draw_results
import cv2
import os
import pmr.utils as utils


class Query:
    def __init__(self):
        self.cache_path = os.path.join(os.environ["HOME"], ".cache", "pmr")
        self.client = chromadb.PersistentClient(
            path=os.path.join(self.cache_path, "pmr_db")
        )
        self.collection = self.client.get_collection(name="pmr_db")
        self.readers_cache = utils.ReadersCache(self.cache_path)

    def query_db(self, input):
        results = self.collection.query(query_texts=[input], n_results=2)
        tmp_client = chromadb.Client()
        for i, id in enumerate(results["ids"][0]):
            doc = results["documents"][0][i]
            doc = json.loads(doc)

            col = tmp_client.create_collection(name="tmp_" + str(i))
            for i, s in enumerate(doc):
                col.add(documents=[json.dumps(s)], ids=[str(i)])

            print("ID : " + str(id))
            reader = self.readers_cache.get_reader(int(id))

            n_results = 5
            res = col.query(query_texts=[input], n_results=n_results)
            n_results = len(res["ids"][0])
            for i in range(n_results):
                r = json.loads(res["documents"][0][i])
                frame = reader.get_frame(int(id))
                if frame is None:
                    print("Frame not found")
                    print(res)
                    continue
                im = draw_results([r], frame)
                cv2.imwrite("query_" + str(i) + ".png", im)
