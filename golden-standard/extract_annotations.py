import pandas as pd
import numpy as np
import re
from bidi.algorithm import get_display


def return_bidi_or_empty(text):
    if isinstance(text, float):
        return ''
    else:
        return get_display(text)


# read excel into pandas DataFrame
excel_df = pd.read_excel(
    '/Users/3248526/git/historic-hebrew-dates/golden-standard/Inscription DB for Time Project.xlsx', header=0)

# remove newline characters from transctriptions
excel_df['Transcription'] = excel_df['Transcription'].str.replace('\n', '')

# extract date annotation
date_pattern = r'(\{.*\}\(תאריך\))'
excel_df['Date_annotation'] = excel_df['Transcription'].str.extract(
    date_pattern, expand=False).apply(return_bidi_or_empty)

# print a bit
pd.set_option('display.max_colwidth', -1)
print(excel_df['Date_annotation'].head())
