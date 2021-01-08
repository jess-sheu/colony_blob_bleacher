from typing import List

import numpy as np
from skimage.feature import peak_local_max
from skimage.filters import rank
from skimage.morphology import disk

DEFAULT = object()
def bleach_location(pre_pixels: np.array,
                    post_pixels: np.array,
                    expected_position = DEFAULT,
                    half_roi_size = DEFAULT):
    """
    Finds the location of a bright spot in the post_pixels image
    The pre_pixel image will be subtracted from the pos_pixel image (after adding
    an offset to account for noise), mean filtered, and the position of the maximum in the image will
    be returned.  To speed up finding the location provide the estimated location and an roi
    within which the real maximum should be located
    :param pre_pixels:
    :param post_pixels:
    :param expected_position:
    :param half_roi_size:
    :return:
    """
    # assume pre and post are the same size
    if expected_position==DEFAULT or half_roi_size==DEFAULT :
        pre_roi = pre_pixels
        post_roi = post_pixels
    else:
        if (expected_position[0] - half_roi_size[0] < 0) or \
                (expected_position[1] - half_roi_size[1] < 0) or \
                (expected_position[0] + half_roi_size[0] > post_pixels.shape[0]) or \
                (expected_position[1] + half_roi_size[1] > post_pixels.shape[1]) :
            pre_roi = pre_pixels
            post_roi = post_pixels
        else:
            cc = post_pixels.shape[1] - expected_position[1]
            ep_rc = [expected_position[0], cc]
            pre_roi = pre_pixels[ep_rc[0] - half_roi_size[0]:ep_rc[0] + half_roi_size[0], ep_rc[1] - half_roi_size[1]:ep_rc[1] + half_roi_size[1]]
            post_roi = post_pixels[ep_rc[0] - half_roi_size[0]:ep_rc[0] + half_roi_size[0], ep_rc[1] - half_roi_size[1]:ep_rc[1] + half_roi_size[1]]
    subtracted = post_roi + 100 - pre_roi
    selem = disk(2)
    subtracted_mean = rank.mean(subtracted, selem=selem)
    peaks_rc_roi = peak_local_max(subtracted_mean, min_distance=20, threshold_rel=0.6, num_peaks=1, indices=True)
    peaks_rc = peaks_rc_roi + [ep_rc[0] - half_roi_size[0], ep_rc[1] - half_roi_size[1]]
    peaks = [peaks_rc[0][0], post_pixels.shape[1] - peaks_rc[0][1]]
    return peaks