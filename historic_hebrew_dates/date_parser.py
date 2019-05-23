#!/usr/bin/env python3
import re
import yaml

from .date_type_parser import DateTypeParser
from .month_parser import MonthParser
from .pattern_parser import PatternParser
from .numeral_parser import NumeralParser
from typing import Dict, Iterator, Tuple

class DateParser(PatternParser):
    def __init__(self, lang='hebrew'):
        self.numeral_parser = NumeralParser(lang=lang)
        if lang == 'hebrew':
            super().__init__('hebrew_dates.csv', 'תאריך', [DateTypeParser(), MonthParser(), self.numeral_parser])
            self.number_keys = ['שנה']
        elif lang == 'dutch':
            super().__init__('dutch_dates.csv', 'datum', [self.numeral_parser])
            self.number_keys = ['dag', 'jaar']
        else:
            raise f'Unknown language {lang}'

    def eval(self, expression: str) -> Dict:
        values: Dict[str, str] = yaml.safe_load('{' + expression[1:-1] + '}')

        for key, value in values.items():
            if key in self.number_keys:
                values[key] = self.numeral_parser.eval(value)
        
        return values
