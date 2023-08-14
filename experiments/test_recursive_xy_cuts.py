# Important Imports
import numpy as np
from PIL import Image
from scipy.signal import find_peaks


# image = PIL.Image, n = Number of Segments
# ignoreBottomTop = Segmentation of top and bottom of Image
# axis = 0 (for vertical-lines) or 1 (for horizontal-lines)
# Returns a gray image, PIL Image.
def recursiveXYCut(image, n, ignoreBottomTop=True, axis=1):
    image = image.convert("L")
    image_arr = np.asarray(image)
    # distance for peaks
    distance = image_arr.shape[0 if axis == 1 else 1] / n

    # Sum the pixels along given axis
    sum_vals = image_arr.sum(axis=axis)
    # Get the indices of the peaks
    peaks, _ = find_peaks(sum_vals, distance=distance)

    # Temp variable to create segment lines i.e. 0 out the required values.
    temp = np.ones(image_arr.shape)
    # Skip top and bottom segmentation or not (depends on the param)
    # for peak in peaks[1:-1 if ignoreBottomTop else ]:
    for peak in peaks[1:-1] if ignoreBottomTop else peaks:
        if axis == 1:
            temp[range(peak - 2, peak + 2)] = 0
        else:
            temp[:, range(peak - 2, peak + 2)] = 0
    return Image.fromarray(np.uint8(image_arr * temp))

im = Image.open("test.png")
im = recursiveXYCut(im, 3)
im.save("out.png")