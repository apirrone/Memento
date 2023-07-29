import time
import os
import mss
import numpy as np
import utils
from process import process_image, draw_results
import cv2
import chromadb
import json

client = chromadb.PersistentClient(path="pmr")
collection = client.get_or_create_collection(name="pmr")

os.makedirs("screenshots", exist_ok=True)
sct = mss.mss()

i = 0
while True:
    window_title = utils.get_active_window()
    im = np.array(sct.grab(sct.monitors[1]))
    results = process_image(im)

    collection.add(
        documents=[json.dumps(results)],
        metadatas=[{"source": window_title}],
        ids=[str(i)],
    )

    cv2.imwrite("screenshots/" + str(i) + ".png", im)
    i += 1
    time.sleep(1)
