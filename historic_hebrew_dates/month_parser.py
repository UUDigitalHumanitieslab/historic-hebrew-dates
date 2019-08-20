#!/usr/bin/env python3
import re

from .pattern_parser import PatternParser
from .numeral_parser import NumeralParser
from typing import Iterator, Tuple


class MonthParser(PatternParser):
    def __init__(self, lang='hebrew', rows=None):
        self.numeral_parser = NumeralParser(lang)
        if lang == 'hebrew':
            super().__init__('hebrew_months.csv',
                             'חודש', [self.numeral_parser], rows)
        elif lang == 'dutch':
            super().__init__('dutch_months.csv',
                             'maand', [self.numeral_parser], rows)
            self.number_keys = ['nummer']
        else:
            raise f'Unknown language {lang}'

    def eval(self, value):
        return self.numeral_parser.eval(value)
