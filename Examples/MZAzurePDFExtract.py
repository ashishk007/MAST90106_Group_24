#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May 10 23:39:05 2022

@author: ashishkumar
"""

import time, os
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from msrest.authentication import CognitiveServicesCredentials
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes

'''
Extract Text PDF - Computer Vision API
This sample will extract printed and handwritten text from images in a PDF.
The images include both printed and handwritten text, including signatures.        

Download the sample PDF here: 
https://github.com/Azure-Samples/cognitive-services-sample-data-files/blob/master/ComputerVision/Images/printed_handwritten.pdf

Place the PDF in your working directory.

Install the Computer Vision SDK:
pip install --upgrade azure-cognitiveservices-vision-computervision

Steps:
   - Authenticate
   - Read and extract from PDF
   - Display extracted text results in console

References: 
Computer Vision Batch Read File documentation: 
https://docs.microsoft.com/en-us/azure/cognitive-services/computer-vision/concept-recognizing-text
SDK: 
https://docs.microsoft.com/en-us/python/api/azure-cognitiveservices-vision-computervision/azure.cognitiveservices.vision.computervision?view=azure-python
API: 
https://westus.dev.cognitive.microsoft.com/docs/services/5cd27ec07268f6c679a3e641/operations/56f91f2e778daf14a499f21b 
'''

'''
Authenticate
'''
key = '545da291833e4c21b6af2376917b30f5'
endpoint = 'https://mcritextextract.cognitiveservices.azure.com/'

# Set credentials
credentials = CognitiveServicesCredentials(key)
# Create client
client = ComputerVisionClient(endpoint, credentials)


'''
Read and extract from the image
'''
dirpath = '/Users/ashishkumar/Documents/MDS/MAST90106_SM1/'
filename = 'chart_2'
file_extension = '.pdf'
    
def pdf_text():
    # Images PDF with text

    filepath = open(dirpath+filename+file_extension,'rb')

    # Async SDK call that "reads" the image
    response = client.read_in_stream(filepath, raw=True)

    # Don't forget to close the file
    filepath.close()

    # Get ID from returned headers
    operation_location = response.headers["Operation-Location"]
    operation_id = operation_location.split("/")[-1]

    # SDK call that gets what is read
    while True:
        result = client.get_read_result(operation_id)
        if result.status.lower () not in ['notstarted', 'running']:
            break
        print ('Waiting for result...')
        time.sleep(10)
    return result


'''
Display extracted text and bounding box
'''
# Displays text captured and its bounding box (position in the image)
result = pdf_text()
if result.status == OperationStatusCodes.succeeded:
    with open(dirpath+filename+'.txt', 'w') as f:
        for readResult in result.analyze_result.read_results:
            for line in readResult.lines:
                f.writelines(line.text)
                print(line.text)
                f.writelines('\n')
                f.writelines(str(line.bounding_box))
                print(line.bounding_box)
                f.writelines('\n')
                print()
        f.close()

    with open(dirpath+filename+'_CI.txt', 'w') as f:
        for readResult in result.analyze_result.read_results:
            for line in readResult.lines:
                for word in line.words:
                    f.write(word.text)
                    f.write('\t')
                    f.write(str(word.confidence))
                    print(word.text)
                    print(word.confidence)
                    f.write('\n')
                    print()
        f.close()
        