#!/usr/bin/env python3
import csv
import os
import re

class NumeralParser:
    def __init__(self):
        with open(os.path.join(os.path.dirname(__file__), 'numeral_patterns.csv')) as patterns:
            reader = csv.reader(patterns)
            next(reader)  # skip header

            grouped_patterns = {}
            # Start with terminal expression, make sure patterns only
            # rely on preceding types: that way a pattern for the entire
            # dependent type can be constructed first and used in the following
            # types.
            pattern_type_order = []
            for row in reader:
                pattern_type = row[0]
                pattern = row[1].replace(' ', ' *')
                expression = row[2]
                if not pattern_type in pattern_type_order:
                    pattern_type_order.append(pattern_type)
                if not pattern_type in grouped_patterns:
                    grouped_patterns[pattern_type] = []
                grouped_patterns[pattern_type].append((pattern, expression))

            all_patterns = []
            parse_patterns = []

            # Expressions matching an entire pattern type
            pattern_type_expressions = {}

            for pattern_type in pattern_type_order:
                patterns = []
                for i, (pattern, expression) in enumerate(grouped_patterns[pattern_type]):
                    named_pattern = r'^'
                    matching_pattern = ''
                    last_pos = 0
                    for sub_pattern in re.finditer(r'\{(?P<name>[^\}]+)\}', pattern):
                        (start, end) = sub_pattern.span()
                        named_pattern += pattern[last_pos:start]

                        sub_type = sub_pattern.groupdict()['name']
                        if re.match(r'\d+', sub_type):
                            sub_type_expression = f"({'|'.join(all_patterns)})"
                            named_pattern += f'(?P<g{sub_type}>{sub_type_expression})'
                        else:
                            sub_type_expression = pattern_type_expressions[sub_type]
                            named_pattern += f'(?P<{sub_type}>{sub_type_expression})'

                        matching_pattern += pattern[last_pos:start]
                        matching_pattern += sub_type_expression
                        last_pos = end
                    named_pattern += pattern[last_pos:] + r'$'
                    matching_pattern += pattern[last_pos:]

                    grouped_patterns[pattern_type][i] = (
                        named_pattern, expression)
                    parse_patterns.append((named_pattern, expression))
                    patterns.append(matching_pattern)
                    all_patterns.append(matching_pattern)
                pattern_type_expressions[pattern_type] = f"({'|'.join(patterns)})"

        self.parse_patterns = parse_patterns
        self.grouped_patterns = grouped_patterns
        # TODO: this could include the pattern type (group for every type)
        # that way parsing a match should be easier and quicker
        self.search_pattern = f"({'|'.join(all_patterns)})"

    def parse_numeral(self, text, patterns=None):
        if patterns is None:
            patterns = self.parse_patterns
        for (pattern, expression) in patterns:
            # TODO: pre-compile patterns?
            match = re.match(pattern, text)
            if match:
                for group in re.finditer('\{(?P<group>[^\}]+)\}', expression):
                    group_name = group['group']
                    if re.match(r'\d+', group_name):
                        sub_patterns = None
                        sub_text = match['g' + group_name]
                    else:                    
                        sub_patterns = self.grouped_patterns[group_name]
                        sub_text = match[group_name]
                    expression = re.sub(
                        '\{' + group_name + '\}',
                        self.parse_numeral(
                            sub_text, 
                            sub_patterns),
                        expression)
                return expression

    def evaluate_expression(self, expression):
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

    def get_operators(self, operator, expression):
        for match in re.finditer(f'(?P<left>\d+)\{operator}(?P<right>\d+)', expression):
            yield (int(match['left']), int(match['right']), match.start(), match.end())

    def replace_string_part(self, text, start, end, replacement):
        return text[:start] + replacement + text[end:]
