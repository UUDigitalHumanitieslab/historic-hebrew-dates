#!/usr/bin/env python3
import re
import os
import csv

import pandas as pd
from bidi.algorithm import get_display

from .grammars.annotation_grammar import get_patterns
from .date_type_parser import DateTypeParser
from .numeral_parser import NumeralParser

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
            .str.replace('(\?)', ' ') \
            .str.replace('  ', ' ') \
            .str.replace('…', '...')
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

    def translate_tag_hebrew(self, english):
        return self.tags[self.tags.translation == english]['tag'].values[0]

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

    def aggr_row_patterns(self, aggr_patterns, patterns, row):
        for context, tag, tag_type, pattern in patterns:
            translated_tag = self.translate_tag(tag)
            if not translated_tag:
                print(f'Unknown tag: {tag}')
            elif pattern:
                if translated_tag in ['age', 'date']:
                    subtags = list(map(lambda match: match.groups()[0], re.finditer(r'\{(\w+)(:\w+|)\}', pattern)))
                    if len(subtags) != len(set(subtags)):
                        print(f"Duplicate tags in {pattern}")
                        print(row)
                    else:
                        value ='[' + ', '.join(map(lambda tag: f'{tag}: \'{tag}\'', subtags)) + ']'
                        aggr_patterns[translated_tag][pattern] = value
                elif translated_tag == 'year':
                    value = row['Year'] if context == 'date' else row['Age at Death']
                    if re.match(r'^\d+$', str(value)):
                        aggr_patterns['number'][pattern] = value
                    else:
                        if pattern not in aggr_patterns['number']:
                            # mark that it exists
                            aggr_patterns['number'][pattern] = None
                elif translated_tag == 'type':
                    if not re.match(r'[\{\}]', pattern):
                        # type patterns with some dependency aren't supported
                        value = row['Type']
                        if not ';' in value:
                            aggr_patterns['type'][pattern] = value
                elif translated_tag == 'month':
                    aggr_patterns[translated_tag][pattern] = row['Month']
                else:
                    raise Exception(f'Unknown tag: {translated_tag} in {pattern}')

    def aggr_patterns(self):
        date_df = pd.concat(
            [
                self.cleaned['Transcription'],
                self.cleaned['Age at Death'],
                self.parsed['Year'],
                self.parsed['Month'],
                self.parsed['Day'],
                self.parsed['Type']
            ], axis=1)

        aggr_patterns = {}
        for index, tag in self.tags.iterrows():
            aggr_patterns[tag['translation']] = {}

        for index, row in date_df.iterrows():
            transcription = row['Transcription']
            if transcription != None:
                try:
                    patterns = get_patterns(transcription, {
                        self.translate_tag_hebrew('day'): self.translate_tag_hebrew('number'),
                        self.translate_tag_hebrew('year'): self.translate_tag_hebrew('number')
                    })
                except Exception as error:
                    print(f'Error parsing: {transcription}')
                    print(error)
                else:
                    self.aggr_row_patterns(aggr_patterns, patterns, row)

        return aggr_patterns

    def write_patterns(self):
        aggr_patterns = self.aggr_patterns()

        #
        # Dates
        max_number, known_date_patterns = self.load_known_patterns('hebrew_dates.csv')
        new_date_patterns = []

        for date_pattern, value in aggr_patterns['date'].items():
            if not date_pattern in known_date_patterns:
                new_date_patterns += [(max_number + 1, date_pattern, value)]

        #
        # Months
        max_number, known_month_patterns = self.load_known_patterns('hebrew_months.csv')
        new_month_patterns = []

        for month_pattern, value in aggr_patterns['month'].items():
            if not month_pattern in known_month_patterns:
                new_month_patterns += [(max_number + 1, month_pattern, value)]

        #
        # Numbers
        numeral_parser = NumeralParser()
        new_number_patterns = []
        for number_pattern, value in aggr_patterns['number'].items():
            if not numeral_parser.parse(number_pattern.replace('\\w*', '')):
                new_number_patterns += [('?', number_pattern, value)]

        #
        # Date type
        date_type_parser = DateTypeParser()
        new_date_type_patterns = []
        for date_type_pattern, value in aggr_patterns['type'].items():
            if not date_type_parser.parse(date_type_pattern.replace('\\w*', '')):
                if value != 'From the destruction of the Temple':
                    raise Exception(f"Unknown date type {value}")
                new_date_type_patterns += [('Destruction temple', date_type_pattern, 'קדש')]

        self.append_patterns('hebrew_date_types.csv', new_date_type_patterns)
        self.append_patterns('hebrew_dates.csv', new_date_patterns)
        self.append_patterns('hebrew_months.csv', new_month_patterns)
        self.append_patterns('hebrew_numerals.csv', new_number_patterns)

        return {
            'new_dates': new_date_patterns,
            'new_date_types': new_date_type_patterns,
            'new_numbers': new_number_patterns,
            'new_month_patterns': new_month_patterns
        }

    def load_known_patterns(self, filename):
        patterns = set()
        max_type = 0
        with open(os.path.join(os.path.dirname(__file__), 'patterns', filename), encoding='utf8') as f:
            reader = csv.reader(f, delimiter=',', quotechar='"')
            next(reader)  # skip header

            for row in reader:
                if re.match(r'^\d+$', row[0]):
                    row_type = int(row[0])
                    if row_type > max_type:
                        max_type = row_type
                patterns.add(row[1])
        return max_type, patterns

    def append_patterns(self, filename, patterns):
        def escape_cell(value):
            str_value = str(value)
            if ',' in str_value:
                return f'"{str_value}"'
            else:
                return str_value

        with open(os.path.join(os.path.dirname(__file__), 'patterns', filename), mode='a', encoding='utf8') as f:
            f.write('\n'.join(map(lambda  row: ','.join(map(lambda cell: escape_cell(cell), row)), patterns)))

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
