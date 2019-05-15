"""
Unit test for converting Hebrew numbers to Hindu-Arabic numerals.
"""

import csv
import os
import unittest

from historic_hebrew_dates.date_type_parser import DateTypeParser

class TestNumerals(unittest.TestCase):
    """
    Unit test class.
    """

    def test_date_types(self):
        parser = DateTypeParser()
        with open(os.path.join(os.path.dirname(__file__), 'hebrew_date_types.csv')) as date_types:
            reader = csv.reader(date_types)
            for row in reader:
                [text, expected] = row
                parsed = parser.parse(text)
                if not parsed:
                    self.fail(f'Parse failed for: {text}, expected: {expected}')
                else:
                    self.assertEqual(parsed, expected)

    def test_dates(self):
        parser = DateTypeParser()
        with open(os.path.join(os.path.dirname(__file__), 'hebrew_dates.csv')) as dates:
            reader = csv.reader(dates)
            next(reader)  # skip header
            for row in reader:
                [text, expected_year, expected_type] = row
                parsed = parser.parse(text)
                if not parsed:
                    # assert.fail
                    print(f'Parse failed for: {text}, expected: {expected_year} {expected_type}')
                else:
                    print(parsed)
