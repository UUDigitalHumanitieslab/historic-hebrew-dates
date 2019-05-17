﻿"""
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
        def test_lang(lang, expected_filename):
            parser = NumeralParser(lang=lang)
            with open(os.path.join(os.path.dirname(__file__), expected_filename), encoding='utf8') as numerals:
                reader = csv.reader(numerals)
                for row in reader:
                    [text, expected] = row
                    parsed = parser.parse(text)
                    if not parsed:
                        self.fail(f'Parse failed for: {text} ({lang}), expected: {expected}')
                    else:                        
                        evaluated = parser.eval(parsed)
                        self.assertEqual(
                            evaluated,
                            int(expected),
                            f'Text: {text} Parse: {parsed} Evaluated: {evaluated} Expected: {expected} ({lang})')

        test_lang('hebrew', 'hebrew_numerals.csv')
        test_lang('dutch', 'dutch_numerals.csv')
