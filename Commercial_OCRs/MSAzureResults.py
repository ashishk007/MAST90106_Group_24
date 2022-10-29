import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import math
import os

cwd = os.getcwd()
os.chdir("/Users/ashishkumar/Documents/MDS/MAST90106_SM1/Comparison/Output")
cwd= os.getcwd()
 

# type(data.loc[:,['Text']])   # df
# type(data.loc[Tex:,'t'])  # series
# type(data['Text'])  # series

# numpy tricks:
# np.repeat([1,2,3], [2,3,2]),  # to repeat each entry of a list/array by how many times
# np.concatenate([[1],[2],[3]]) # to concatenate a list of lists of a multi-dimension array;
                                # for a Series of lists, use .values to change it to a multi-dimension array

# pandas tricks:
# Shiv_TF_3['Dates'].values    # return an array of entries of a Series
# Shiv_TF_3['Dates'].index     # return an array of index
# Shiv_TF_3.keys().to_list()   # return a list of all column names of a DataFrame

def center_coord_x(row):
    ## input the row of a text as a dataframe
    ## return its x center coordinate
    
    x_coord = round((row['box_left']+row['box_right'])/2, 4)

    return x_coord


def center_coord_y(row):
    ## input the row of a text as a dataframe
    ## return its y center coordinate
    
    y_coord = round((row['box_top']+row['box_bottom'])/2, 4)

    return y_coord


def rotate(row, x_name, y_name, coord_type):
    ## input a pair of column names (e.g.'x_three', 'y_three') 
    ## input a coord_type ('x' or 'y')
    ## rotate the input x or y (follow coord_type) index stored in this row

    if coord_type=='x':
        x_rot = 1 - row[y_name]  
        return x_rot
    
    elif coord_type=='y':
        y_rot = row[x_name]
        return y_rot
    
    else:
        print('A wrong coord_type entered; restart again.')
        return -1.0

    
def prepare_row_df(file_name):
    ## input an raw output file
    ## correct the coordinates into the normal orientation for an incorrectly oriented file
    ## and add center coordinates of all extracted texts
    
    # x-y coord pairs in the incorrectly oriented output files
    pairs = [('x_one','y_one'), ('x_two','y_two'), ('x_three','y_three'), ('x_four','y_four'), 
             ('box_left','box_bottom'), ('box_right','box_top')]
    data = pd.read_csv(file_name)
    
    if '270' in file_name:  # an incorrectly oriented output files
        for pair in pairs:
            x = pair[0]  # x coord
            y = pair[1]  # y coord
            data[x] = data.apply(rotate, args=(x, y, 'x'), axis=1)  # convert coord in each row
            data[y] = data.apply(rotate, args=(x, y, 'y'), axis=1)
    
    # create center coords of the extracted text in each row
    data['center_coord_x'] = data.apply(center_coord_x, axis=1)
    data['center_coord_y'] = data.apply(center_coord_y, axis=1)
        
    return data


def zone_one_df(df):
    ## input the full dataframe of an image
    ## return a dataframe containing rows of patient information

    index_0 = 0    # first row of zone 1
    index_1 = 0    # last row of zone 1
    ref_coord = 0  # the ref coord that separate left (patient info) and right
    
    ## crude filter
    for index, row in (df.loc[:,['Text']]).iterrows():
        
        if "affix" in row['Text'].lower():
            index_0 = index
            ref_coord = df.loc[index_0,'center_coord_x']
            
        elif "fir" in row['Text'].lower():
            index_1 = index
            
    if index_0 == index_1:
        print("Failed to extract zone 1\n")
        return None
    
    zone_1_df = df[index_0:index_1].copy(deep=True)
    
    ## fine filter
    zone_1_df = zone_1_df[zone_1_df['center_coord_x'] < ref_coord]
    
    return zone_1_df.copy(deep=True)


def extract_zone_one(df):
    ## input the filtered zone one dataframe
    ## match the variables and extracted texts
    
    # fixtures in this zone
    printed = ['urn', 'family', 'name',  'given', 'names', 
               'address', 'date', 'of', 'birth']
    # target variables in zone 1
    variables = {'URN':'', 'Family':'', 'Given':'', 'Address':'', 'DOB':'', 'Sex':''}
    
    # concatenate and then tokenize all texts 
    texts = df.loc[:,'Text'].to_list()
    scores = df.loc[:,'Confidence'].to_list()
    # print(texts)
    for index, text in enumerate(texts):  # 2nd part to prevent e.g. 'Address: Springuale'
        if "address" in text.lower() and len(text.split(' '))==1 and ((index+1)!=len(texts)): # 3rd part
            address = texts[index+1]      # in case an address has multiple words,            # to prevent OBE
            address = address.split(' ')  # e.g. change port melbourne to port_melbourne
            address = '_'.join(address)
            texts[index+1] = address
    long_str = ' '.join(texts).lower()
    long_str = long_str.replace(':','')
    tokens = long_str.split(' ')
    # print(tokens)
    
    # overly simplified way to assign values to variables
    # may need extra work for formal application
    for index, token in enumerate(tokens):
        if ('urn' in token) and (tokens[index+1] not in printed): # 2nd part is for empty feedback
            variables['URN'] = tokens[index+1]                    # e.g. no URN extracted
            
        elif 'name' == token and (tokens[index+1] not in printed):
            variables['Family'] = tokens[index+1]
        elif 'names' == token and (tokens[index+1] not in printed):
            variables['Given'] = tokens[index+1]

        elif 'address' in token:
            try: 
                if tokens[index+1] not in printed:
                    variables['Address'] = tokens[index+1]
            except IndexError:  # to prevent OBE
                print("no address found")
            
        elif sum(c.isdigit() for c in token) > 4:
            variables['DOB'] = token
            
    return variables

'''test file names'''

name = 'output_1.csv'
data = prepare_row_df(name)

zone_1_df = zone_one_df(data); # zone_1_df
print(extract_zone_one(zone_1_df))


def zone_2three_df(df):
    ## input the full dataframe of an image
    ## return two dataframes containing rows of medication (zone 2) and dosage information (zone 3)

    index_0 = 0    # first row of zone 1
    index_1 = 0    # last row of zone 1
    ref_coord = 0  # the ref coord that separate left (medication) and right (dosage)
    
    ## crude filter
    count = 0  # only texts between the first two "generic"s
    for index, row in (df.loc[:,['Text']]).iterrows():
        
        if "gen" in row['Text'].lower() and count == 0:
            index_0 = index
            count += 1
            
        elif "gen" in row['Text'].lower() and count == 1:
            index_1 = index
            count += 1
            break
            
    if index_0 == index_1:
        print("Failed to extract zone 2 and 3\n")
        return None
    
    zone_23_df = df[index_0:index_1+1].copy(deep=True)  # dataframe contains both zone 2 & 3
    
    ## fine filter
    for index, row in (zone_23_df.loc[:,['Text']]).iterrows():
        
        if "contact" in row['Text'].lower():  # use "contact" to separate two zones
            ref_coord = zone_23_df.loc[index,'box_right']
        if "yes" in row['Text'].lower():  # use "continue" to limit zone 3
            zone3end_coord = zone_23_df.loc[index,'center_coord_x']
        else:
            zone3end_coord  = 0.7
    
    zone_2_df = zone_23_df[zone_23_df['center_coord_x'] <= ref_coord]  # zone 2
    zone_3_df_t = zone_23_df[zone_23_df['box_left'] > ref_coord]  # zone 3 lower x cordinate limit
    zone_3_df = zone_3_df_t[zone_3_df_t['center_coord_x'] < zone3end_coord]  # zone 3 upper x cordinate limit
    
    return zone_2_df.copy(deep=True), zone_3_df.copy(deep=True)
    
    
def extract_zone_three(df):
    ## input the filtered zone three dataframe
    ## match the variables and extracted texts
    
    # fixtures in this zone
    printed = ['date', 'time', 'dose',  'route', 'sign']
    # find texts between these pairs
    pairs = [('date', 'time'), ('time', 'dose'), ('dose',  'route'), ('route', 'sign')]
    # target variables in zone 1
    variables = {'Date':[], 'Time':[], 'Dose':[], 'Route':[]}
    
    #
    texts = df.loc[:,'Text'].to_list()
    long_str = ' '.join(texts).lower()
    tokens = long_str.split(' ')
    # print(tokens)
    
    for pair in pairs:
        top = pair[0]
        bottom = pair[1]
        top_index = bottom_index = -1
    
        for index, text in enumerate(tokens):
            if top in text:
                top_index = index
            elif bottom in text:
                bottom_index = index
                
        if (top_index < bottom_index) and top_index != -1:
            variables[top.capitalize()] = tokens[top_index+1:bottom_index].copy()
        else:
            print(f"{top.capitalize()} extraction failed\n")
    
    return variables
    
    
'''test file names'''

name = "output_1.csv"


data = prepare_row_df(name)

'''test zone 3'''
zone_2_df, zone_3_df = zone_2three_df(data); # zone_3_df
extract_zone_three(zone_3_df)



def extract_zone_two(df):
    ## input the filtered zone two dataframe
    ## match the variables and extracted texts
    
    df = df.reset_index(drop=True)
    
    # fixtures in this zone
    printed = ['date', 'medicine', 'print',  'generic', 'name', 
               'route', 'dose', 'hourly', 'frequency', 'max', 'prn',
               '24', 'hrs', 'indication', 'pharmacy', 'prescriber', 'signature',
               'print', 'your', 'name', 'contact']
    # target variables in zone 1
    variables = {'Date':'', 'Medicine':'', 'Route':'', 'Dose':'', 'Indication':'', 'Prescriber':''}
    
    texts = df.loc[:,'Text'].to_list()
    long_str = ' '.join(texts).lower()
    tokens = long_str.split(' ')
    # print(tokens)
    
    ## 1 & 2
    candidates = texts[1:3].copy()
    digit_1 = sum(c.isdigit() for c in candidates[0])
    digit_2 = sum(c.isdigit() for c in candidates[1])
    
    if (digit_1 > 0):
        variables['Medicine'] = candidates[1]
        variables['Date'] = candidates[0]
    elif (digit_2 > 0):
        variables['Medicine'] = candidates[0]
        variables['Date'] = candidates[1]
    
    elif len(candidates[0]) > len(candidates[1]):
        variables['Medicine'] = candidates[0]
        variables['Date'] = candidates[1]
    else:
        variables['Medicine'] = candidates[1]
        variables['Date'] = candidates[0]
    
    ## 3 & 4
    for index, row in df.iterrows():
        if 'max' in row['Text'].lower():
            candidate1 = df.loc[index+1,:]
            candidate2 = df.loc[index+2,:]
            if candidate1['center_coord_x'] < candidate2['center_coord_x']:
                variables['Route'] = candidate1['Text']
                variables['Dose'] = candidate2['Text']
            else:
                variables['Route'] = candidate2['Text']
                variables['Dose'] = candidate1['Text']
            break
            
    ## 5
    index_0 = index_1 = -1
    for index, token in enumerate(tokens):
        if 'indica' in token:
            index_0 = index
        elif 'pres' in token:
            index_1 = index
            
    candidates = tokens[index_0+1 : index_1].copy()
    # print(index_1)
    for candidate in candidates:
        if candidate in printed:
            candidates.remove(candidate)
            
    variables['Indication'] = ' '.join(candidates)
    
    ## 6
    ps_name = []
    for index, text in enumerate(texts):
        if text == 'Date':
            i = 1
            while texts[index-i].lower() != 'contact':
                ps_name.append(texts[index-i])
                i = i+1
    ps_name.reverse()
    variables['Prescriber'] = ' '.join(ps_name)
            
    return variables

    
'''test file names'''

name = "../Output/output_1.csv"


data = prepare_row_df(name)

'''test zone 2'''
zone_2_df, zone_3_df = zone_2three_df(data)
extract_zone_two(zone_2_df)

# zone_2_df#.loc[35,:]



zone_1 = pd.DataFrame({'URN': [], 'Family': [], 'Given': [], 'Address': [], 'DOB': [], 'Sex': []} )


zone_2 = pd.DataFrame({'Date': [], 'Medicine': [], 'Route': [], 'Dose': [], 'Indication': [], 'Prescriber': []})


zone_3 = pd.DataFrame({'Dates': [], 'Times': [], 'Doses': [], 'Routes': []})


for i in range(1,11):
    name = f"../Output/output_{i}.csv"
    data = prepare_row_df(name)
    zone_1_df = zone_one_df(data)
    zone_2_df, zone_3_df = zone_2three_df(data)
    
    # 1
    new_row = extract_zone_one(zone_1_df)
    zone_1.loc[-1] = new_row  # adding a row
    zone_1.index = zone_1.index + 1  # shifting index
    zone_1 = zone_1.reset_index(drop=True)
    # Jessika_zone_1 = Jessika_zone_1.sort_index()  # sorting by index
    
    # 2
    new_row = extract_zone_two(zone_2_df)
    zone_2.loc[-1] = new_row  # adding a row
    zone_2.index = zone_2.index + 1  # shifting index
    zone_2 = zone_2.reset_index(drop=True)
    
    # 3
    new_row = extract_zone_three(zone_3_df)
    zone_3.loc[-1] = new_row  # adding a row
    zone_3.index = zone_3.index + 1  # shifting index
    zone_3 = zone_3.reset_index(drop=True)




