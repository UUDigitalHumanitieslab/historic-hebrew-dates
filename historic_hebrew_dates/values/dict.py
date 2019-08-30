#!/usr/bin/env python3
import yaml
from typing import Dict


def dict_value(expression: str) -> Dict:
    values: Dict[str, str] = yaml.safe_load('{' + expression[1:-1] + '}')

    return values
