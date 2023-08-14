import cv2


def preprocess_image(im, rf=1):
    im = cv2.resize(im, (0, 0), fx=rf, fy=rf)
    gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)

    thr2 = cv2.bitwise_not(gray)
    thr2 = cv2.adaptiveThreshold(
        thr2, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
    )

    thr = thr2
    cl = cv2.cvtColor(thr, cv2.COLOR_GRAY2BGR)
    return cl, thr


def extract_layout(thr):
    thr = cv2.erode(thr, (5, 5), iterations=10)

    return thr


for i in range(4):
    im = cv2.imread(str(i) + ".png")
    cl, thr = preprocess_image(im)
    # cv2.imwrite("thr"+str(i)+".png", thr)
    tmp = extract_layout(thr)
    cv2.imwrite("tmp" + str(i) + ".png", tmp)
