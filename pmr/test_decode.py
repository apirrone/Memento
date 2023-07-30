import av
import cv2

container = av.open("test.mp4")
stream = container.streams.video[0]
i = 0
for frame in container.decode(stream):
    i += 1
    print(frame.pts, frame.time_base)
    cvframe = frame.to_ndarray(format="bgr24")
    print(cvframe.shape)
    cv2.imwrite(str(i) + ".png", cvframe)