#!/usr/bin/env python3
from .dict import dict_value
from .numeral import numeral_value
from .text import text_value


values = {
    'dict': dict_value,
    'numeral': numeral_value,
    'text': text_value
}
