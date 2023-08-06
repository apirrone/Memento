import chromadb
import os
from thefuzz import fuzz
from pmr.caching import MetadataCache


class Query:
    def __init__(self):
        self.cache_path = os.path.join(os.environ["HOME"], ".cache", "pmr")
        self.client = chromadb.PersistentClient(
            path=os.path.join(self.cache_path, "pmr_db")
        )
        self.collection = self.client.get_collection(name="pmr_db")
        self.metadata_cache = MetadataCache(self.cache_path)

    # TODO score threshold seems high
    def query_db(self, input, nb_results=10, score_threshold=50):
        results = self.collection.query(query_texts=[input], n_results=nb_results)
        final_results = {}
        ids = results["ids"][0]
        docs = results["documents"][0]
        for i, frame_id in enumerate(ids):
            frame_data = self.metadata_cache.get_frame_metadata(frame_id)
            scores = []
            matches = []
            matches_bbs = []
            if "bbs" not in frame_data:
                continue
            for j, bb_id in enumerate(frame_data["bbs"]):
                txt = str(frame_data["text"][j])
                scores.append(fuzz.ratio(input.lower(), txt.lower()))

                matches.append(txt)
                matches_bbs.append(frame_data["bbs"][j])

            zipped = zip(scores, matches, matches_bbs)
            zipped = sorted(zipped, key=lambda x: x[0], reverse=True)
            scores, matches, matches_bbs = zip(*zipped)

            frame_has_result = False
            final_results[frame_id] = []
            for j in range(len(scores[:10])):
                if scores[j] > score_threshold:
                    final_results[frame_id].append(
                        {
                            "bb": matches_bbs[j],
                            "text": matches[j],
                            "score": scores[j],
                        }
                    )
                    frame_has_result = True
            if not frame_has_result:
                final_results = {}
        # print(f"query: {input} query results: {final_results}\n allresults: {results}")

        return final_results
