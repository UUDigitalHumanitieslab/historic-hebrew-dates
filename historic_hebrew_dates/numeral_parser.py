#!/usr/bin/env python3
import re

from .pattern_parser import PatternParser
from typing import Iterator, Tuple

class NumeralParser(PatternParser):
    def __init__(self, lang='hebrew'):
        if lang == 'hebrew':
            super().__init__('hebrew_numerals.csv', 'מספר')
        elif lang == 'dutch':
            super().__init__('dutch_numerals.csv', 'nummer')
        else:
            raise f'Unknown language {lang}'

    def eval(self, expression: str) -> int:
        return eval(expression, {}, {})

    def get_operators(self, operator: str, expression: str) -> Iterator[Tuple[int, int, int, int]]:
        for match in re.finditer(f'(?P<left>\d+)\\{operator}(?P<right>\d+)', expression):
            yield (int(match['left']), int(match['right']), match.start(), match.end())
