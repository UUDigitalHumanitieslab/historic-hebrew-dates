import pandas as pd
import numpy as np
import re
from bidi.algorithm import get_display
# from googletrans import Translator
# from pyparsing import nestedExpr
# translator = Translator()

pd.set_option('display.max_colwidth', -1)


def return_bidi_or_empty(text):
    if isinstance(text, float):
        return ''
    else:
        return get_display(text)


def character_removal(text, removal_characters):
    for char in removal_characters:
        text = text.replace(char, '')
    return text


def tag_pattern(tag):
    return r'(\{{.*\}}\({}\))'.format(tag)


# read excel into pandas DataFrame
excel_df = pd.read_excel(
    '/Users/3248526/git/historic-hebrew-dates/golden-standard/Inscription DB for Time Project.xlsx', header=0)

excel_df['Transcription'] = excel_df['Transcription'].str.replace('\n', '')

# Cleaning transcription
# remove newlines and square brackets
excel_df['Transcription_cleaned'] = excel_df['Transcription'].apply(
    character_removal, removal_characters=['\n', '[', ']'])
# hebrew_pattern = r'([\u0590-\u05fe]|\W)'
# latin_letters = '\s[\u0041-\u007A]+\s'

# print(excel_df['Transcription_cleaned'].apply(
#     lambda x: print(''.join(re.findall(latin_letters, x)))))

# re.findall(hebrew_pattern)

# extract date annotation
date_pattern = r'(\{.*\}\(תאריך\))'
date_pattern_2 = tag_pattern('תאריך')
excel_df['Date_annotation'] = excel_df['Transcription'].str.extract(
    date_pattern, expand=False)
# print(excel_df['Date_annotation'])

# extract age annotation
age_pattern = r'(\{.*\}\(גיל\))'
excel_df['Age_annotation'] = excel_df['Transcription'].str.extract(
    age_pattern, expand=False)

# extract type annotation
# type_pattern = tag_pattern('טיפוס')
# type_pattern = r'(\{.*?\}\(טיפוס\))'
# type_pattern = r'(\{.*?\w+?}\(טיפוס\))'
# excel_df['Date_type_annotation'] = excel_df['Date_annotation'].str.extract(
#     type_pattern, expand=False)
# print(excel_df['Date_type_annotation'].str.replace('[\(.*\)|\{|\}|\[|\]]', ''))
# print(excel_df['Date_type_annotation'])

# print a bit
# print(excel_df['Age_annotation'].head())

# out = excel_df['Date_annotation'][0]
# print(out)
# nested = nestedExpr('{', '}').parseString(out).asList()
# print(nested)

# sub_pat = r"(\w+)(\})(\(.+\))"
# subbed = re.sub(sub_pat, r"\1\3\2", out)
