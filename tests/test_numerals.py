﻿"""
Unit test for converting Hebrew numbers to Hindu-Arabic numerals.
"""

import csv
import os
import unittest

from historic_hebrew_dates import create_parsers

class TestNumerals(unittest.TestCase):
    """
    Unit test class.
    """

    def test_numerals(self):
        def test_lang(lang, expected_filename):
            parser = create_parsers(lang)['numerals']
            with open(os.path.join(os.path.dirname(__file__), expected_filename), encoding='utf8') as numerals:
                reader = csv.reader(numerals)
                for row in reader:
                    [text, expected] = row
                    parsed = parser.search(text)
                    if not parsed:
                        self.fail(f'Parse failed for: {text} ({lang}), expected: {expected}')
                    else:
                        evaluated = [match['eval'] for match in parsed[0]['matches']]
                        self.assertIn(
                            int(expected),
                            evaluated,
                            f'Text: {text} Parse: {parsed} Evaluated: {evaluated} Expected: {expected} ({lang})')
                        if len(evaluated) > 1:
                            print(f"WARNING: Ambiguous parse! For: {text} -> {evaluated} (expected {expected})")

        test_lang('hebrew', 'hebrew_numerals.csv')
        test_lang('dutch', 'dutch_numerals.csv')
