from pdf2image import convert_from_path
import os
def pdf2png(importDir,filename,datatype='pdf'):
    '''
    Transfer the pdf input into png format

    :param:
        importDir (str): the path of the import
        filename (str): the name of the output(temp) file
        datatype (str): the datatype of the import, default to be .png
    :return:
        PNG file
    :raise:
        NameError: if the datatype doesn't exist or unable to import.
    '''
    if datatype.lower()=='pdf':
        images_from_path = convert_from_path(importDir)
        current_directory = os.path.dirname(os.path.abspath(__file__))
        imagePath=current_directory+'/tempImage'
        for image in images_from_path:
            if not os.path.exists(imagePath):
                os.makedirs(imagePath)
            image.save(imagePath + '/' + filename + '_%s.png' % images_from_path.index(image), 'PNG')
    else:
        raise NameError("The datatype doesn't exist or unable to import")

if __name__ == "__main__":
    path='C:/Users/84446/Desktop/testingset'
    files = os.listdir(path)
    for file in files:
        if not os.path.isdir(file):
            f = path + "/" + file
            print(f)
            namelist=file.split(".")
            pdf2png(f,namelist[0])
