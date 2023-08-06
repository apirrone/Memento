import av
from pmr.utils import FPS, SECONDS_PER_REC, FRAME_CACHE_SIZE
import time
import os
import json


class Reader:
    def __init__(self, filename, offset=0):
        self.container = av.open(filename)
        self.stream = self.container.streams.video[0]
        self.frames = []
        for i, frame in enumerate(self.container.decode(self.stream)):
            self.frames.append(frame)
        self.offset = offset

    def get_frame(self, frame_i):
        if (frame_i - self.offset) < len(self.frames):
            return self.frames[frame_i - self.offset].to_ndarray(format="bgr24")
        else:
            return None


class ReadersCache:
    def __init__(self, cache_path):
        self.readers = {}
        self.readers_ids = []  # in order to know the oldest reader
        self.cache_path = cache_path
        self.cache_size = FRAME_CACHE_SIZE

    def select_video_id(self, frame_id):
        return int(frame_id // (FPS * SECONDS_PER_REC))

    def get_reader(self, frame_id):
        video_id = self.select_video_id(frame_id)
        offset = int(video_id * (FPS * SECONDS_PER_REC))
        if video_id not in self.readers:  # Caching reader
            start = time.time()
            self.readers[video_id] = Reader(
                os.path.join(self.cache_path, str(video_id) + ".mp4"), offset=offset
            )
            self.readers_ids.append(video_id)
            # print(
            #     "Caching reader",
            #     video_id,
            #     "at",
            #     offset,
            #     "offset frames took",
            #     time.time() - start,
            #     "seconds",
            # )
            if len(self.readers) > self.cache_size:
                dumped_id = self.readers_ids[0]
                self.readers_ids = self.readers_ids[1:]
                # print("Dumping reader with id", dumped_id, "from cache")
                del self.readers[dumped_id]
        return self.readers[video_id]

    # Shorthand
    def get_frame(self, frame_id):
        return self.get_reader(frame_id).get_frame(frame_id)


class Metadata:
    def __init__(self, file_path):
        self.file_path = file_path
        if not os.path.exists(self.file_path):
            self.metadata = {}
        else:
            self.metadata = json.load(open(self.file_path))

    def get_frame(self, frame_id):
        return self.metadata[str(frame_id)]

    def write(self, frame_id, data):
        self.metadata[str(frame_id)] = data
        json.dump(self.metadata, open(self.file_path, "w"))


class MetadataCache:
    def __init__(self, cache_path):
        self.cache_path = cache_path
        self.cache = {}
        self.cache_size = FRAME_CACHE_SIZE
        self.cache_ids = []

    def select_metadata_id(self, frame_id):
        return int(int(frame_id) // (FPS * SECONDS_PER_REC))

    def get_metadata(self, frame_id):
        metadata_id = self.select_metadata_id(frame_id)
        if metadata_id not in self.cache:
            start = time.time()
            self.cache[metadata_id] = Metadata(
                os.path.join(self.cache_path, str(metadata_id) + ".json")
            )
            # print(
            #     "Caching metadata",
            #     metadata_id,
            #     "took",
            #     time.time() - start,
            #     "seconds",
            # )
            self.cache_ids.append(metadata_id)
            if len(self.cache) > self.cache_size:
                dumped_id = self.cache_ids[0]
                self.cache_ids = self.cache_ids[1:]
                # print("Dumping metadata with id", dumped_id, "from cache")
                del self.cache[dumped_id]
        return self.cache[metadata_id]

    def get_frame_metadata(self, frame_id):
        metadata = self.get_metadata(frame_id)
        return metadata.get_frame(frame_id)
    
    def write(self, frame_id, data):
        metadata = self.get_metadata(frame_id)
        metadata.write(frame_id, data)
