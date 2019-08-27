#!/usr/bin/env python3
from os import path
import yaml
from typing import Dict, List
from .pattern_parser import PatternParser
from .values import values

def create_parsers(lang: str, override_rows: Dict[str, List[str]] = {}) -> Dict[str, PatternParser]:
    with open(path.join(path.dirname(__file__), 'patterns', '%s.json' % lang)) as file:
        specification = yaml.safe_load(file)

    parsers = {}

    for pattern in specification['patterns']:
        type = pattern['type']
        dependencies = list(map(lambda subtype: parsers[subtype], (pattern.get('dependencies') or [])))
        parsers[type] = PatternParser(
            '%s_%s.csv' % (lang, type),
            pattern['key'],
            values[pattern['eval']],
            dependencies,
            override_rows.get(type))

    return parsers
