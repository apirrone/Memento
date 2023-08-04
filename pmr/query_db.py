import chromadb
import json
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
        # print(results)
        final_results = {}
        ids = results["ids"][0]
        text = results["documents"][0]
        for i, id in enumerate(ids):
            frame_id = id.split("-")[0]
            bb_id = id.split("-")[1]
            distance = results["distances"][0][i]
            bb = self.metadata[frame_id]["bbs"][int(bb_id)]
            if frame_id not in final_results:
                final_results[frame_id] = []
            final_results[frame_id].append({"bb": bb, "text": text[i], "distance": distance})

        return final_results
