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
import signal

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
        self.frame_i = 0

        self.images_queue = Queue()
        self.results_queue = Queue()
        self.nb_workers = 2
        self.workers = []
        self.pids = []
        for i in range(self.nb_workers):
            w = multiprocessing.Process(target=self.process_images, args=())
            self.workers.append(w)
            self.pids.append(w.pid)
        for i in range(self.nb_workers):
            self.workers[i].start()
            print("started worker", i)

    def process_images(self):
        # Infinite worker
        # easyocr_reader = easyocr.Reader(["fr", "en"], gpu=True)
        # print("Done initializing easyocr")

        signal.signal(signal.SIGINT, self.stop_process)
        while True:
            data = self.images_queue.get()
            frame_i = data["frame_i"]
            im = data["im"]
            window_title = data["window_title"]
            t = data["time"]
            start = time.time()
            results = process.process_image(im, ocr="tesseract")
            # results = process.process_image(im, ocr="easyocr", reader=easyocr_reader)
            print("Processing time :", time.time() - start)

            self.results_queue.put(
                {
                    "frame_i": frame_i,
                    "results": results,
                    "time": t,
                    "window_title": window_title,
                }
            )

            texts = []
            ids = []
            for i in range(len(results)):
                texts.append(results[i]["text"])
                ids.append(str(frame_i) + "-" + str(i))

            self.collection.add(
                documents=texts,
                ids=ids,
            )

            # cv2.imwrite(str(i)+".png", process.draw_results(results, im))

    def stop_rec(self, sig, frame):
        self.rec.stop()
        print("STOPPING MAIN", os.getpid())
        exit()

    def stop_process(self, sig, frame):
        print("STOPPING PROCESS", os.getpid())
        exit()

    def run(self):
        signal.signal(signal.SIGINT, self.stop_rec)
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
            self.images_queue.put(
                {
                    "im": im,
                    "window_title": window_title,
                    "time": t,
                    "frame_i": self.frame_i,
                }
            )

            self.metadata[str(self.frame_i)] = {
                "window_title": window_title,
                "time": t,
            }

            try:
                result = self.results_queue.get(False)
                bbs = []
                for i in range(len(result["results"])):
                    bb = {}
                    bb["x"] = result["results"][i]["x"]
                    bb["y"] = result["results"][i]["y"]
                    bb["w"] = result["results"][i]["w"]
                    bb["h"] = result["results"][i]["h"]
                    bbs.append(bb)

                self.metadata[str(result["frame_i"])]["bbs"] = bbs
                print("GOT RESULT")
            except Exception:
                print("results queue empty")
                pass

            json.dump(
                self.metadata,
                open(os.path.join(self.cache_path, "metadata.json"), "w"),
            )

            print("QUEUE SIZE", self.images_queue.qsize())

            self.frame_i += 1
            if (self.frame_i % (utils.FPS * utils.SECONDS_PER_REC)) == 0:
                print("CLOSE")
                self.rec.stop()
                self.nb_rec += 1
                self.rec = utils.Recorder(
                    os.path.join(self.cache_path, str(self.nb_rec) + ".mp4")
                )
