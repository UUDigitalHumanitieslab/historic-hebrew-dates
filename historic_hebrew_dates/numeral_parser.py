#!/usr/bin/env python3
import re

from .pattern_parser import PatternParser
from typing import Iterator, Tuple

class NumeralParser(PatternParser):
    def __init__(self):
        super().__init__('hebrew_numerals.csv', 'מספר')

    def evaluate_expression(self, expression: str) -> int:
        last_index = 0
        evaluated_expression = ''
        for left, right, start, end in self.get_operators('*', expression):
            evaluated_expression += expression[last_index:start] + str(left * right)
            last_index = end
        expression = evaluated_expression + expression[last_index:]

        evaluated_expression = ''
        last_index = 0
        for left, right, start, end in self.get_operators('+', expression):
            evaluated_expression += expression[last_index:start] + str(left + right)
            last_index = end
        expression = evaluated_expression + expression[last_index:]
        if re.match(r'^\d+$', expression):
            return int(expression)
        else:
            return self.evaluate_expression(expression)

    def get_operators(self, operator: str, expression: str) -> Iterator[Tuple[int, int, int, int]]:
        for match in re.finditer(f'(?P<left>\d+)\{operator}(?P<right>\d+)', expression):
            yield (int(match['left']), int(match['right']), match.start(), match.end())
