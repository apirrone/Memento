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
        self.metadata = json.load(open(os.path.join(self.cache_path, "metadata.json")))

    def query_db(self, input, nb_results=10):
        results = self.collection.query(query_texts=[input], n_results=nb_results)
        final_results = {}
        ids = results["ids"][0]
        text = results["documents"][0]
        for i, id in enumerate(ids):
            frame_id = id.split("-")[0]
            bb_id = id.split("-")[1]
            bb = self.metadata[frame_id]["bbs"][int(bb_id)]
            if frame_id not in final_results:
                final_results[frame_id] = []
            final_results[frame_id].append({"bb": bb, "text": text[i]})

        return final_results

    def _query_db(self, input, nb_results=1):
        results = self.collection.query(query_texts=[input], n_results=nb_results)
        frames_ids = results["ids"][0]
        documents = results["documents"][0]
        final_results = []
        print(results)
        tmp_client = chromadb.Client()
        for i, frame_id in enumerate(frames_ids):
            frame = self.readers_cache.get_frame(int(frame_id))
            final_results.append({"id": frame_id, "results": []})

            doc = json.loads(documents[i])
            col = tmp_client.create_collection(name="tmp_" + str(i))
            for j, s in enumerate(doc):
                col.add(documents=[json.dumps(s)], ids=[str(j)])
            print("ID : " + str(frame_id))
            res = col.query(query_texts=[input], n_results=nb_results)

            items_ids = res["ids"][0]
            items_docs = res["documents"][0]
            for j, item_id in enumerate(items_ids):
                txt = json.loads(items_docs[j])
                if frame is None:
                    print("Frame not found")
                    print(res)
                    continue
                final_results[-1]["results"].append(txt)
                im = draw_results([txt], frame)
                print("Writing query_" + str(i * j) + ".png")
            cv2.imwrite("query_" + str(i * j) + ".png", im)
            tmp_client.delete_collection(name="tmp_" + str(i))
        return final_results
