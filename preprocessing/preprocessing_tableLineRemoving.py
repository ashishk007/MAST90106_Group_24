'''
    Attention!!!
    The actual result of this part is not very good, so I manually processed a small part of the image before feeding it to the model.
    That's why I didn't add this part of the code to the main! If you need to reproduce it, it is recommended to run this part of the code separately
'''
import cv2
def table_line_remove(img):
    '''
    this function is for removing the table lines. Grayscaling is also done in this step
    :param img: an OpenCV imread input
    :return: 2-d array representing the image without table line
    '''
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    ret, binary = cv2.threshold(gray, 200, 255, 0)
    # assuming, b_w is the binary image
    inv = 255 - binary
    horizontal_img = inv
    vertical_img = inv

    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (100, 1))
    horizontal_img = cv2.erode(horizontal_img, kernel, iterations=1)
    horizontal_img = cv2.dilate(horizontal_img, kernel, iterations=1)

    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 100))
    vertical_img = cv2.erode(vertical_img, kernel, iterations=1)
    vertical_img = cv2.dilate(vertical_img, kernel, iterations=1)

    mask_img = horizontal_img + vertical_img
    # no_border = np.bitwise_or(binary, mask_img)
    no_border = cv2.bitwise_or(binary, mask_img)
    return no_border