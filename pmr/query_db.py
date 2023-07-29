import chromadb
import json
from pmr.process import draw_results
import cv2


def query_db():
    client = chromadb.PersistentClient(path="pmr_db")
    collection = client.get_collection(name="pmr_db")
    q = input("query : ")
    results = collection.query(query_texts=[q], n_results=2)

    tmp_client = chromadb.Client()
    for i, id in enumerate(results["ids"][0]):
        print("===", id)
        doc = results["documents"][0][i]
        doc = json.loads(doc)

        col = tmp_client.create_collection(name="tmp_" + str(i))
        for i, s in enumerate(doc):
            col.add(documents=[json.dumps(s)], ids=[str(i)])

        n_results = 5
        res = col.query(query_texts=[q], n_results=n_results)
        n_results = len(res["ids"][0])
        for i in range(n_results):
            r = json.loads(res["documents"][0][i])
            im = draw_results([r], cv2.imread("screenshots/" + id + ".png"))
            cv2.imshow("im", im)
            cv2.waitKey(0)
