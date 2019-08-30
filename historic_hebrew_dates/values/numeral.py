#!/usr/bin/env python3
import math

from typing import cast, Union


def numeral_value(expression: str) -> Union[int, float]:
    try:
        return cast(int, eval(expression, {}, {}))
    except Exception as error:
        return math.nan
