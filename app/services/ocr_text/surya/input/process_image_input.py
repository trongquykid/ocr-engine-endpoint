import cv2
import numpy as np
# from app.common.config import settings

PARAMETER_GRAY = (55, 55)
BINARY_INV_1 = 11
BINARY_INV_2 = 9

def process_image_v2(image):
    image_np = np.array(image)

    gray = cv2.cvtColor(image_np, cv2.COLOR_RGB2GRAY)

    blurred_background = cv2.GaussianBlur(gray, PARAMETER_GRAY, 0)

    binary = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, BINARY_INV_1, BINARY_INV_2)

    binary_inv = cv2.bitwise_not(binary)

    result = cv2.bitwise_and(blurred_background, blurred_background, mask=binary_inv)
    result = cv2.bitwise_or(result, cv2.bitwise_and(gray, gray, mask=binary))

    result_rgb = cv2.cvtColor(result, cv2.COLOR_GRAY2RGB)

    return result_rgb