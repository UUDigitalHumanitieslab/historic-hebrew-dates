#!/usr/bin/env python3
import re

from .pattern_parser import PatternParser
from typing import Iterator, Tuple

class MonthParser(PatternParser):
    def __init__(self):
        super().__init__('hebrew_months.csv', 'חודש')
