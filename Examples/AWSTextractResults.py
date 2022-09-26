#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep 26 19:45:17 2022

@author: ashishkumar
"""

import boto3
from PIL import Image, ImageDraw, ImageFont
import time, os

client = boto3.client('textract', region_name='ap-southeast-2')

def image_pdf_text(image_file):
    
    with open(image_file, 'rb') as document_file:
        document_bytes = document_file.read()

    response = client.detect_document_text(Document={'Bytes': document_bytes})

    return response


def apply_ocr(example):
    # get the image
    image = Image.open(example['image_path'])
    
    width, height = image.size
    
    # apply ocr to the image 
    response = image_pdf_text(example['image_path'])
    
    # get the words and actual (unnormalized) bounding boxes
    # words = [word  if str(word) != 'nan'])
    lines = []
    for item in response['Blocks']:
        if item['BlockType'] == 'LINE' and item['Text']!='':
            lines.append(item['Text'])
                    
   
    example['text'] = ' '.join(lines)
    
    #example['CI'] = confidence
    return example



import pandas as pd
import os
from collections import OrderedDict

dataset_path = "/Users/ashishkumar/Documents/MDS/MAST90106_SM1/Comparison/images/Chosen_Samples"

images = []

for _, _, image_names in os.walk(dataset_path):
    relative_image_names = []
    for image in image_names:
        if image[-3:] == "png":
            relative_image_names.append(dataset_path + "/" + image)
    images.extend(relative_image_names)

data = pd.DataFrame.from_dict({'image_path': images})
data.sort_values(by=['image_path'])
data['image_path'][5]



from datasets import Dataset
dataset = Dataset.from_pandas(data)
result_dataset = dataset.map(apply_ocr)

output_path = "/Users/ashishkumar/Documents/MDS/MAST90106_SM1/Comparison/Output/"
output = pd.DataFrame(result_dataset).drop('image_path', axis=1)
output.to_csv(output_path + 'chosen_samples_AWS_Textract.csv')