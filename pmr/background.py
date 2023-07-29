import time
import os
import mss
import numpy as np
import cv2
import chromadb
import json
import datetime
from pmr.process import process_image
import pmr.utils as utils


def background():
    client = chromadb.PersistentClient(path="pmr_db")
    collection = client.get_or_create_collection(name="pmr_db")

    os.makedirs("screenshots", exist_ok=True)
    sct = mss.mss()

    screenshots_metadata = {}

    # TODO run process_image in a subprocess (asynchronously)
    i = 0
    while True:
        window_title = utils.get_active_window()

        im = np.array(sct.grab(sct.monitors[1]))
        cv2.imwrite("screenshots/" + str(i) + ".png", im)
        t = json.dumps(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        screenshots_metadata[str(i)] = {"source": window_title, "time": t}
        json.dump(screenshots_metadata, open("screenshots_metadata.json", "w"))

        start = time.time()
        results = process_image(im)
        collection.add(
            documents=[json.dumps(results)],
            metadatas=[
                {
                    "source": window_title,
                    "time": t,
                }
            ],
            ids=[str(i)],
        )
        print("time taken", time.time() - start)

        i += 1
        time.sleep(1)
