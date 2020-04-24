"""
Unit test for converting Hebrew numbers to Hindu-Arabic numerals.
"""

import csv
import os
import unittest
import yaml

from historic_hebrew_dates import create_parsers

class TestDates(unittest.TestCase):
    """
    Unit test class.
    """

    def test_date_types(self):
        parser = create_parsers('hebrew')['date_types']
        with open(os.path.join(os.path.dirname(__file__), 'hebrew_date_types.csv'), encoding='utf8') as date_types:
            reader = csv.reader(date_types)
            for row in reader:
                [text, expected] = row
                parsed = parser.search(text)
                if not parsed:
                    self.fail(f'Parse failed for: {text}, expected: {expected}')
                else:
                    self.assertEqual(parsed[0]['matches'][0]['parsed'], expected)

    def test_dates(self):
        def test_lang(lang, expected_filename):
            parser = create_parsers(lang)['dates']
            skipped = 0
            with open(os.path.join(os.path.dirname(__file__), expected_filename), encoding='utf8') as dates:
                reader = csv.reader(dates)
                for row in reader:
                    [text, expected, skip] = row
                    if skip:
                        skipped += 1
                        continue
                    expression = parser.search(text)
                    if not expression:
                        self.fail(f'Parse failed for: {text}, expected: {expected}')
                    else:
                        self.assertDictEqual(yaml.safe_load(expected), expression[0]['matches'][0]['eval'],
                            text)
            if skipped > 0:
                print(f'SKIPPED {skipped} rows for {lang}!')

        test_lang('dutch', 'dutch_dates.csv')
        #test_lang('hebrew', 'hebrew_dates.csv')
