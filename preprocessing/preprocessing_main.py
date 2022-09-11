from preprocessing_pdf2png import *
from preprocessing_filters import *

import os
if __name__ == "__main__":
    path='C:/Users/84446/Desktop/testingset'
    files = os.listdir(path)
    for file in files:
        if not os.path.isdir(file):
            f = path + "/" + file
            print(f)
            namelist=file.split(".")
            pdf2png(f,namelist[0])
    current_directory = os.path.dirname(os.path.abspath(__file__))
    imagePath = current_directory + '/tempImage'
    images_from_path=os.listdir(imagePath)
    for image in images_from_path:
        if not os.path.isdir(image):
            f = imagePath + '/' + image
            print(f)
            img=cv2.imread(f)
            img=filtering(img, filter='none')
            img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            savedir=imagePath+'/preprocessed/'+image+'.png'
            cv2.imwrite(savedir,img)
