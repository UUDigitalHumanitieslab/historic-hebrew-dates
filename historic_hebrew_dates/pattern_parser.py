#!/usr/bin/env python3
import csv
import os
import re

from collections import ChainMap
from typing import Dict, Iterator, List, Tuple, Pattern, Optional

class PatternParser:
    def __init__(self, filename: str, type: str, child_patterns = []):
        self.type = type
        self.child_patterns: Dict[str, PatternParser] = {
            key:value for (key, value) in map(lambda pattern: (pattern.type, pattern), child_patterns)
        }
        with open(os.path.join(os.path.dirname(__file__), 'patterns', filename), encoding='utf8') as patterns:
            reader = csv.reader(patterns, delimiter=',', quotechar='"')
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

                        var_name, sub_type = self.get_group_name_parts(sub_pattern.groupdict()['name'])

                        if re.match(r'\d+', sub_type):
                            # a number means: include all preceding patterns
                            sub_type_expression = f"({'|'.join(all_patterns)})"
                        elif sub_type in self.child_patterns:
                            sub_type_expression = self.child_patterns[sub_type].search_pattern
                        else:
                            sub_type_expression = pattern_type_expressions[sub_type]
                        named_pattern += f'(?P<{self.get_group_name(var_name, sub_type)}>{sub_type_expression})'

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
                var_parts = ((self.get_var_name(group_name), value) for group_name, value in match.groupdict().items())
                var_values = {
                    parts[0]: (value, parts[1])
                    for parts, value in var_parts
                }
                for group in re.finditer('\{(?P<var>[^\}]+)\}', expression):
                    var_name = group['var']
                    backref = re.match(r'^\d+$', var_name)
                    try:
                        sub_text, sub_type = var_values[f'g{var_name}' if backref else var_name]
                    except:
                        print(var_values)
                        raise IndexError(f"{expression} {var_name}")
                    sub_parse = None
                    if backref:
                        sub_patterns = None
                    elif sub_type in self.child_patterns:
                        sub_parse = self.child_patterns[sub_type].parse(sub_text)
                    else:
                        sub_patterns = self.grouped_patterns[sub_type]
                    if sub_parse is None:
                        sub_parse = self.parse(
                            sub_text, 
                            sub_patterns)
                    if sub_parse is None:
                        return None
                    expression = re.sub(
                        '\{' + group['var'] + '\}',
                        sub_parse,
                        expression)
                return expression
        return None

    def get_group_name_parts(self, group_name: str):
        """
        Get the variable name and sub_type of a named group expression.
        """
        name_parts: List[str] = group_name.split(':')
        if len(name_parts) == 2:
            var_name = name_parts[0]
            sub_type = name_parts[1]
        else:
            var_name = sub_type = name_parts[0]

        if ('_' in var_name) or ('_' in sub_type):
            raise Exception("Underscores aren't allowed in sub-pattern identifiers.")

        return var_name, sub_type

    def get_group_name(self, var_name: str, sub_type: str):
        """
        Gets the group name to use for a named group expression.
        """
        if re.match(r'\d+', sub_type):
            # a number means: include all preceding patterns
            # prefix with g because named groups in regex aren't allowed
            # to start with a digit
            return f'g{var_name}__{sub_type}'
        else:
            return f'{var_name}__{sub_type}'

    def get_var_name(self, group_name: str):
        """
        Gets the variable names from the named groups.
        """
        skip_first = 1 if re.match(r'\d+', group_name) else 0
        return group_name[skip_first:].split('__')
