import mss
import numpy as np
import cv2
import chromadb
import json
import datetime
import pmr.process as process
import pmr.utils as utils
import asyncio
import os
import time
import multiprocessing
from multiprocessing import Queue
# import easyocr


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

        self.images_queue = Queue()
        self.nb_workers = 2
        self.workers = []
        for i in range(self.nb_workers):
            self.workers.append(
                multiprocessing.Process(target=self.process_images, args=())
            )
            self.workers[-1].start()
            print("started worker", i)

    def process_images(self):
        # Infinite worker
        # easyocr_reader = easyocr.Reader(["fr", "en"], gpu=True)
        # print("Done initializing easyocr")
        while True:
            data = self.images_queue.get()
            i = data["i"]
            im = data["im"]
            window_title = data["window_title"]
            t = data["t"]
            start = time.time()
            results = process.process_image(im, ocr="tesseract")
            # results = process.process_image(im, ocr="easyocr", reader=easyocr_reader)
            print("Processing time :", time.time() - start)
            self.collection.add(
                documents=[json.dumps(results)],
                metadatas=[
                    {
                        "source": window_title,
                        "time": t,
                    }
                ],
                ids=[str(i)],
            )
            cv2.imwrite(str(i)+".png", process.draw_results(results, im))

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
            print("QUEUE SIZE", self.images_queue.qsize())

            self.i += 1
            if (self.i % (utils.FPS * utils.SECONDS_PER_REC)) == 0:
                print("CLOSE")
                self.rec.stop()
                self.nb_rec += 1
                self.rec = utils.Recorder(
                    os.path.join(self.cache_path, str(self.nb_rec) + ".mp4")
                )
