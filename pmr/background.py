import mss
import numpy as np
import cv2
import chromadb
import json
import datetime
from pmr.process import process_image, draw_results
import pmr.utils as utils
import asyncio
import os
import queue
import threading
import time


class Background:
    def __init__(self):
        self.cache_path = os.path.join(os.environ["HOME"], ".cache", "pmr")
        os.makedirs(self.cache_path, exist_ok=True)
        self.client = chromadb.PersistentClient(
            path=os.path.join(self.cache_path, "pmr_db")
        )
        self.collection = self.client.get_or_create_collection(name="pmr_db")
        self.sct = mss.mss()
        self.metadata = {}
        self.nb_rec = 0
        self.rec = utils.Recorder(
            os.path.join(self.cache_path, str(self.nb_rec) + ".mp4")
        )
        self.rec.start()

        self.running = True
        self.i = 0
        self.done_processing = 0

        self.images_queue = queue.Queue()
        threading.Thread(target=self.process_images, daemon=True).start()

    def process_images(self):
        # Infinite worker
        while True:
            data = self.images_queue.get()
            im = data["im"]
            window_title = data["window_title"]
            t = data["t"]
            start = time.time()
            results = process_image(im)
            print("Processing time :", time.time() - start)
            start = time.time()
            self.collection.add(
                documents=[json.dumps(results)],
                metadatas=[
                    {
                        "source": window_title,
                        "time": t,
                    }
                ],
                ids=[str(self.i)],
            )
            print("Adding to db time :", time.time() - start)
            self.done_processing += 1
            self.images_queue.task_done()

    def run(self):
        print("Running in background ...")
        while self.running:
            window_title = utils.get_active_window()

            # Get screenshot and add it to recorder
            im = np.array(self.sct.grab(self.sct.monitors[1]))
            im = im[:, :, :-1]
            im = cv2.resize(im, utils.RESOLUTION)
            asyncio.run(self.rec.new_im(im))

            # Create metadata
            t = json.dumps(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            self.metadata[str(self.i)] = {
                "source": window_title,
                "time": t,
                # "index": self.i,
            }
            json.dump(
                self.metadata, open(os.path.join(self.cache_path, "metadata.json"), "w")
            )

            self.images_queue.put(
                {"im": im, "window_title": window_title, "t": t, "i": self.i}
            )
            print(
                "Frames processed in queue :",
                str(self.done_processing) + "/" + str(self.i),
            )

            self.i += 1
            if (self.i % (utils.FPS * utils.SECONDS_PER_REC)) == 0:
                print("CLOSE")
                self.rec.stop()
                self.nb_rec += 1
                self.rec = utils.Recorder(
                    os.path.join(self.cache_path, str(self.nb_rec) + ".mp4")
                )
