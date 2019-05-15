#!/usr/bin/env python3
import re

from .pattern_parser import PatternParser
from typing import Iterator, Tuple

class DateTypeParser(PatternParser):
    def __init__(self):
        super().__init__('hebrew_date_types.csv', 'טיפוס')
