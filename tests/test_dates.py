"""
Unit test for converting Hebrew numbers to Hindu-Arabic numerals.
"""

import csv
import os
import unittest
import yaml

from historic_hebrew_dates.date_parser import DateParser
from historic_hebrew_dates.date_type_parser import DateTypeParser

class TestNumerals(unittest.TestCase):
    """
    Unit test class.
    """

    def test_date_types(self):
        parser = DateTypeParser()
        with open(os.path.join(os.path.dirname(__file__), 'hebrew_date_types.csv'), encoding='utf8') as date_types:
            reader = csv.reader(date_types)
            for row in reader:
                [text, expected] = row
                parsed = parser.parse(text)
                if not parsed:
                    self.fail(f'Parse failed for: {text}, expected: {expected}')
                else:
                    self.assertEqual(parsed, expected)

    def test_dates(self):
        def test_lang(lang, expected_filename):
            parser = DateParser(lang=lang)
            skipped = 0
            with open(os.path.join(os.path.dirname(__file__), expected_filename), encoding='utf8') as dates:
                reader = csv.reader(dates)
                for row in reader:
                    [text, expected, skip] = row
                    if skip:
                        skipped += 1
                        continue
                    expression = parser.parse(text)
                    if not expression:
                        self.fail(f'Parse failed for: {text}, expected: {expected}')
                    else:
                        self.assertDictEqual(yaml.safe_load(expected), parser.eval(expression),
                            text)
            if skipped > 0:
                print(f'SKIPPED {skipped} rows for {lang}!')
        
        test_lang('dutch', 'dutch_dates.csv')
        test_lang('hebrew', 'hebrew_dates.csv')
