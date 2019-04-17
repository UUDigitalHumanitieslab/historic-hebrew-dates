"""
Unit test for converting Hebrew numbers to Hindu-Arabic numerals.
"""

import csv
import os
import unittest

from historic_hebrew_dates.numeral_parser import NumeralParser

class TestNumerals(unittest.TestCase):
    """
    Unit test class.
    """

    def test_numerals(self):
        parser = NumeralParser()
        with open(os.path.join(os.path.dirname(__file__), 'hebrew_numerals.csv')) as numerals:
            reader = csv.reader(numerals)
            for row in reader:
                [text, expected] = row
                parsed = parser.parse_numeral(text)
                if not parsed:
                    self.fail(f'Parse failed for: {text}, expected: {expected}')
                else:
                    self.assertEqual(parser.evaluate_expression(parsed), int(expected))
