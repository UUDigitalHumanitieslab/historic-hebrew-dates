#!/usr/bin/env python3
import csv
import os
import re

from typing import Dict, Iterator, List, Tuple, Pattern, Optional

class PatternParser:
    def __init__(self, filename: str, type: str, child_patterns = []):
        self.type = type
        self.child_patterns: List[PatternParser] = child_patterns
        with open(os.path.join(os.path.dirname(__file__), 'patterns', filename)) as patterns:
            reader = csv.reader(patterns)
            next(reader)  # skip header

            grouped_patterns_str: Dict[str, List[Tuple[str, str]]] = {}
            # Start with terminal expression, make sure patterns only
            # rely on preceding types: that way a pattern for the entire
            # dependent type can be constructed first and used in the following
            # types.
            pattern_type_order: List[str] = []
            for row in reader:
                pattern_type: str = row[0]
                pattern: str = row[1].replace(' ', ' *')
                expression: str = row[2]
                if not pattern_type in pattern_type_order:
                    pattern_type_order.append(pattern_type)
                if not pattern_type in grouped_patterns_str:
                    grouped_patterns_str[pattern_type] = []
                grouped_patterns_str[pattern_type].append((pattern, expression))

            all_patterns: List[str] = []
            parse_patterns: List[Tuple[Pattern, str]] = []

            # Expressions matching an entire pattern type
            pattern_type_expressions: Dict[str, str] = {}

            grouped_patterns: Dict[str, List[Tuple[Pattern, str]]] = {}

            for pattern_type in pattern_type_order:
                type_patterns: List[str] = []
                grouped_patterns[pattern_type] = []
                for i, (pattern, expression) in enumerate(grouped_patterns_str[pattern_type]):
                    named_pattern = r'^'
                    matching_pattern = ''
                    last_pos = 0
                    for sub_pattern in re.finditer(r'\{(?P<name>[^\}]+)\}', pattern):
                        (start, end) = sub_pattern.span()
                        named_pattern += pattern[last_pos:start]

                        sub_type: str = sub_pattern.groupdict()['name']
                        if re.match(r'\d+', sub_type):
                            # a number means: include all preceding patterns
                            sub_type_expression = f"({'|'.join(all_patterns)})"
                            named_pattern += f'(?P<g{sub_type}>{sub_type_expression})'
                        else:
                            # TODO: use child_patterns if available
                            sub_type_expression = pattern_type_expressions[sub_type]
                            named_pattern += f'(?P<{sub_type}>{sub_type_expression})'

                        matching_pattern += pattern[last_pos:start]
                        matching_pattern += sub_type_expression
                        last_pos = end
                    named_pattern += pattern[last_pos:] + r'$'
                    matching_pattern += pattern[last_pos:]

                    grouped_patterns[pattern_type].append((
                        re.compile(named_pattern), expression))
                    parse_patterns.append((re.compile(named_pattern), expression))

                    type_patterns.append(matching_pattern)
                    all_patterns.append(matching_pattern)
                pattern_type_expressions[pattern_type] = f"({'|'.join(type_patterns)})"

        self.parse_patterns = parse_patterns
        self.grouped_patterns = grouped_patterns
        self.search_pattern = f"({'|'.join(all_patterns)})"

    def parse(self, text: str, patterns: Optional[List[Tuple[Pattern, str]]]=None) -> Optional[str]:
        if patterns is None:
            patterns = self.parse_patterns
        for (pattern, expression) in patterns:
            match = pattern.match(text)
            if match:
                for group in re.finditer('\{(?P<group>[^\}]+)\}', expression):
                    group_name = group['group']
                    if re.match(r'\d+', group_name):
                        sub_patterns = None
                        sub_text = match['g' + group_name]
                    else:                    
                        sub_patterns = self.grouped_patterns[group_name]
                        sub_text = match[group_name]
                    numeral = self.parse(
                            sub_text, 
                            sub_patterns)
                    if numeral is None:
                        return None
                    expression = re.sub(
                        '\{' + group_name + '\}',
                        numeral,
                        expression)
                return expression
        return None
