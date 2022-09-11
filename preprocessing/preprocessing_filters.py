import cv2
def filtering(OpenCVread,filter='median'):
    '''
    Add a filter to the whole picture (may add more than one, not yet determined)
    depend on the quality of the import!!!
    if the input is already clear enough then just use filter='none' to skip this part

    :param:
        OpenCVread (OpenCV read data): the imported image
        filter: has to be median, gaussian, both, sobel, or none. default to be median

    :return:
        RGB images, OpenCV read

    :raise:
        NameError: if the filter doesn't exist.
    '''
    if filter=='median':
        median=cv2.medianBlur(OpenCVread, 3) # choose ksize=3
        return median
    elif filter=='gaussian':
        Gaussian=cv2.GaussianBlur(OpenCVread, (3,3), 0) # ksize is not sure, needed to be tested
        return Gaussian
    elif filter=='both':
        median = cv2.medianBlur(OpenCVread, 3)  # choose ksize=3
        Gaussian = cv2.GaussianBlur(median, (3, 3), 0)# ksize is not sure, needed to be tested
        return Gaussian
    elif filter=='sobel' or filter=='hpf':
        x = cv2.Sobel(OpenCVread, cv2.CV_16S, 1, 0)
        y = cv2.Sobel(OpenCVread, cv2.CV_16S, 0, 1)
        absx = cv2.convertScaleAbs(x)
        absy = cv2.convertScaleAbs(y)
        dist = cv2.addWeighted(absx, 0.5, absy, 0.5, 0)# weighted sum
        return dist
    elif filter=='none':
        return OpenCVread
    else:
        raise NameError("The filter doesn't exist")