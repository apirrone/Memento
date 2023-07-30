import mss
import numpy as np
import av
import fractions
import cv2

AUDIO_PTIME = 0.020  # 20ms audio packetization
VIDEO_CLOCK_RATE = 90000
VIDEO_PTIME = 1 / 90  # 30fps
VIDEO_TIME_BASE = fractions.Fraction(1, VIDEO_CLOCK_RATE)

sct = mss.mss()

rec = open("rec.h264", "wb")
codec = av.CodecContext.create('h264', 'r')

i = 0
while True:
    i += 1
    print(i)
    im = np.array(sct.grab(sct.monitors[1]))
    im = im[:, :, :-1]
    im = cv2.cvtColor(im, cv2.COLOR_RGB2BGR)
    frame = av.video.frame.VideoFrame.from_ndarray(im, format="bgr24")
    # frame.to_file(rec)
    # packets = codec.parse(frame)
    # # packet = av.packet.Packet(frame)
    # packets.tofile(rec)
    if i > 20:
        break
rec.close()
