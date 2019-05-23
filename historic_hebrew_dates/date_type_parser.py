#!/usr/bin/env python3
import re

from .pattern_parser import PatternParser
from typing import Iterator, Tuple

class DateTypeParser(PatternParser):
    def __init__(self, lang='hebrew', rows=None):
        super().__init__('hebrew_date_types.csv', 'טיפוס', rows=rows)

    def eval(self, value):
        return value
