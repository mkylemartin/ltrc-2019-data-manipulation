"""
get <head sortkey="">
get candidate info
- language
- age
- score
question number
exam score


remove all <c> tags
"""

import re
from bs4 import BeautifulSoup as soup
from glob import glob
import pandas as pd

dataset = glob('/Users/Kyle/Downloads/Kyle Martin'
               '/fce-released-dataset/Data/*')


def get_xml(dataset):
    """ pass in the directory of xml files and this will
        select all the data that is an xml file.
        `dataset` is a glob object. """
    filelist = []
    for directory in dataset:
        dates = glob(directory + r'/*')
        for date in dates:
            files = glob(date + r'/*')
            for file in files:
                filelist.append(file)

    print('len(filelist): ', len(filelist))
    return filelist


def get_info(soup_object):
    """`soup_object` is an xml file that has had the `soup` method called
        on it.

        This function gets all the desired info out of the given xml file"""
    try:
        sortkey = soup_object.head.attrs['sortkey']
    except AttributeError:
        sortkey = 'n/a'
    # language
    try:
        language = soup_object.language.string
    except AttributeError:
        language = 'n/a'
    # age
    try:
        age = soup_object.age.string
    except AttributeError:
        age = 'n/a'
    # score
    try:
        overall_score = float(soup_object.score.string)
    except AttributeError:
        overall_score = 'n/a'

    info = [('sortkey', sortkey),
            ('language', language),
            ('age', age),
            ('overall_score', overall_score)]

    q1 = get_question_data(soup_object.answer1, q_num='1')
    q2 = get_question_data(soup_object.answer2, q_num='2')

    data = dict(info + q1 + q2)

    return data


def get_question_data(dirty_answer, q_num='n/a'):
    """ `dirty_answer` is a soup object.
        Take the raw responses from the FCE data and:
        1. remvoe the corrections
        2. get the question number
        3. get the exam score
        4. return the cleaned text"""
    question_number = dirty_answer.question_number.string
    try:
        exam_score = dirty_answer.exam_score.string
    except AttributeError:
        exam_score = 'ERROR'

    # remove corrections i.e. `<c>this</c>`
    [c.decompose() for c in dirty_answer('c')]
    # remove all other xml
    clean = dirty_answer.coded_answer.get_text()

    info = [(f'{q_num}-question_number', question_number),
            (f'{q_num}-exam_score', exam_score),
            (f'{q_num}-just_text', clean)]

    return info


# get all the file locations
filelist = get_xml(dataset)

do_not_do = [
'/Users/Kyle/Downloads/Kyle Martin/fce-released-dataset/Data/dataset/0102_2000_6/doc1884.xml',
'/Users/Kyle/Downloads/Kyle Martin/fce-released-dataset/Data/dataset/0102_2000_6/doc2671.xml',
'/Users/Kyle/Downloads/Kyle Martin/fce-released-dataset/Data/dataset/0100_2000_6/doc593.xml',
'/Users/Kyle/Downloads/Kyle Martin/fce-released-dataset/Data/dataset/0100_2000_6/doc268.xml',
'/Users/Kyle/Downloads/Kyle Martin/fce-released-dataset/Data/dataset/0100_2000_6/doc2436.xml',
'/Users/Kyle/Downloads/Kyle Martin/fce-released-dataset/Data/dataset/0100_2000_12/doc451.xml',
'/Users/Kyle/Downloads/Kyle Martin/fce-released-dataset/Data/dataset/0100_2000_12/doc2077.xml',
]

all_data = pd.DataFrame()
for file in filelist:
    if file in do_not_do:
        pass
    else:
        with open(file) as f:
            raw = soup(f, 'xml')
            processed = get_info(raw)
            all_data = all_data.append(processed, ignore_index=True)
    print('.', end='', flush=True)

# print(all_data)
writer = pd.ExcelWriter('CFE_dataset.xlsx')
all_data.to_excel(writer, 'Sheet1')
writer.save()
# all_data.to_excel('CFE_dataset.xlsx', encoding='utf-8', index=False)
