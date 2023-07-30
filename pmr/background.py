import mss
import numpy as np
import cv2
import chromadb
import json
import datetime
from pmr.process import process_image
import pmr.utils as utils
import asyncio
from multiprocessing import Pool

class Background:
    def __init__(self):
        self.client = chromadb.PersistentClient(path="pmr_db")
        self.collection = self.client.get_or_create_collection(name="pmr_db")
        self.sct = mss.mss()
        self.metadata = {}
        self.seconds_per_rec = 60
        self.nb_rec = 0
        self.rec = utils.Recorder(str(self.nb_rec)+".mp4")
        self.rec.start()

        self.running = True
        self.i = 0

    def process(self, im, window_title, t):
        # Process image and add it to metadata.json
        results = process_image(im)
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

    def run(self):
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
                "index": self.i,
            }
            json.dump(self.metadata, open("metadata.json", "w"))

            pool = Pool(processes=1)
            pool.apply_async(self.process, [im, window_title, t])

            self.i += 1
            if (self.i % (utils.FPS * self.seconds_per_rec)) == 0:
                pool.close()
                pool.join()
                self.rec.stop()
                self.nb_rec += 1
                self.rec = utils.Recorder(str(self.nb_rec)+".mp4")
        self.rec.stop()
