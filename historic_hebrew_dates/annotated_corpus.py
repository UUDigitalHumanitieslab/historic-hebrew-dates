#!/usr/bin/env python3
import re
import os

import pandas as pd
from bidi.algorithm import get_display


pd.set_option('display.max_colwidth', -1)


class AnnotatedCorpus:
    def __init__(self):
        self.tags = pd.read_csv(os.path.join(
            os.path.dirname(__file__), 'tags.csv'))

        self.raw_df = pd.read_excel(os.path.join(
            os.getcwd(), 'data/Inscription DB for Time Project.xlsx'), header=0)

        self.cleaned = self.clean_transcriptions(self.raw_df)
        self.infixed = self.infix_transcriptions(self.cleaned)
        self.parsed = self.parse_transcriptions(self.infixed)

    def clean_transcriptions(self, dataframe):
        cleaned_df = dataframe.copy(deep=True)
        cleaned_df['Transcription'] = dataframe['Transcription'] \
            .str.replace('\n', ' ') \
            .str.replace('[', '') \
            .str.replace(']', '') \
            .str.replace('  ', ' ')
        return cleaned_df

    def infix_transcriptions(self, dataframe):
        """ Rewrite transcriptions of the form {text}(tag) to {text(tag)}"""
        pattern = r'(})(\(.+?\))'
        infixed_df = dataframe.copy(deep=True)
        infixed_df['Transcription'].replace(
            to_replace=pattern, value=r'\2\1', regex=True, inplace=True)
        return infixed_df

    def parse_transcriptions(self, dataframe):
        dataframe = self.parse_column(dataframe, 'Transcription')
        dataframe = self.parse_column(dataframe, 'T_date')
        dataframe = self.parse_column(dataframe, 'T_age')
        dataframe = self.parse_column(dataframe, 'T_date_type')
        return dataframe

    def parse_column(self, dataframe, column_name):
        tag_pattern = r'(^.+)\((.+)\)$'
        c_name = 'T' if column_name == 'Transcription' else column_name
        for i, row in enumerate(dataframe[column_name]):
            try:
                parsed_level = parse_level_parentheses(row)
                if parsed_level:
                    for annotation in parsed_level:
                        match = re.match(tag_pattern, annotation)
                        if match:
                            text, tag = match.groups()
                            full_tag = '_'.join(
                                [c_name, self.translate_tag(tag)])
                            if full_tag not in dataframe.columns:
                                dataframe[full_tag] = None
                            dataframe.loc[i, full_tag] = text
                            if full_tag + '_raw' not in dataframe.columns:
                                dataframe[full_tag+'_raw'] = None
                            dataframe.loc[i, full_tag+'_raw'] = strip_annotations(
                                text)
            except:
                pass
        return dataframe

    def translate_tag(self, input_tag):
        return self.tags[self.tags.tag == input_tag]['translation'].values[0]

    def write_test_standards(self):
        # age (all)
        age_df = pd.concat(
            [
                self.parsed['T_age_raw'],
                self.parsed['Age at Death']
                    .str.replace('\n', ' ')
            ], axis=1).dropna()

        age_df.to_csv('data/age_all.csv', header=[
                      'text', 'age at death'], index=False)

        # age (only clear numbers)
        age_df = age_df[pd.to_numeric(
            age_df['Age at Death'], errors='coerce').notnull()]
        age_df.to_csv('data/age_clear.csv', header=[
                      'text', 'age at death'], index=False)

        # date (all)
        date_df = self.parsed[['T_date_raw', 'Date', 'Year', 'Type']]
        date_df = date_df.replace('\n', ' ', regex=True).dropna()
        date_df.to_csv('data/date_all.csv', header=[
            'text', 'date', 'year', 'type'], index=False)

        # date (clear)
        date_df = date_df[
            (pd.to_numeric(date_df['Date'], errors='coerce').notnull()) &
            (pd.to_numeric(date_df['Year'], errors='coerce').notnull())
        ]
        date_df.to_csv('data/date_clear.csv', header=[
            'text', 'date', 'year', 'type'], index=False)


def parse_level_parentheses(string, open='{', close='}'):
    """ Parse a single level of matching brackets """
    stack = []
    parsed = []
    for i, c in enumerate(string):
        if c == open:
            stack.append(i)
        elif c == '}' and stack:
            start = stack.pop()
            if len(stack) == 0:
                parsed.append((string[start + 1: i]))
    return parsed


def strip_annotations(string):
    string = string.replace('{', '')
    string = string.replace('}', '')
    string = re.sub(r'\(.+?\)', '', string)
    return string
