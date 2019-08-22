#!/usr/bin/env python3
import csv
import os
import re

from collections import ChainMap
from typing import cast, Dict, Iterator, List, Tuple, Pattern, Optional
from functools import reduce

from .grammars.pattern_grammar import get_parts


class PatternParser:
    def __init__(self, filename: str, type: str, child_patterns=[], rows=None):
        self.type = type
        self.child_patterns: Dict[str, PatternParser] = {
            key: value for (key, value) in map(lambda pattern: (pattern.type, pattern), child_patterns)
        }
        if rows:
            self.__parse_rows(rows)
        else:
            with open(os.path.join(os.path.dirname(__file__), 'patterns', filename), encoding='utf-8-sig') as patterns:
                rows = csv.reader(patterns, delimiter=',', quotechar='"')
                next(rows)  # skip header
                self.__parse_rows(rows)

    def __parse_rows(self, rows):
        grouped_patterns_str: Dict[str, List[Tuple[str, str]]] = {}
        # Start with terminal expression, make sure patterns only
        # rely on preceding types: that way a pattern for the entire
        # dependent type can be constructed first and used in the following
        # types.
        pattern_type_order: List[str] = []
        for row in rows:
            pattern_type: str = row[0]
            pattern: str = row[1]
            expression: str = row[2]
            if not pattern_type in pattern_type_order:
                pattern_type_order.append(pattern_type)
            if not pattern_type in grouped_patterns_str:
                grouped_patterns_str[pattern_type] = []
            grouped_patterns_str[pattern_type].append((pattern, expression))

        search_patterns: List[Pattern] = []

        # Patterns by type. For each item in the tuple:
        # 0: the extraction pattern
        # 1: the search pattern
        # 2: the expression to evaluate
        grouped_patterns: Dict[str, List[Tuple[Pattern, Pattern, str]]] = {}

        for pattern_type in pattern_type_order:
            grouped_patterns[pattern_type] = []
            for i, (pattern, expression) in enumerate(grouped_patterns_str[pattern_type]):
                parts = get_parts(pattern)
                extraction_pattern = self.__compile_pattern(
                    parts,
                    grouped_patterns,
                    search_patterns,
                    True)
                search_pattern = self.__compile_pattern(
                    parts,
                    grouped_patterns,
                    search_patterns,
                    False)

                grouped_patterns[pattern_type].append(
                    (extraction_pattern, search_pattern, expression))
                search_patterns.append(search_pattern)

        self.grouped_patterns = grouped_patterns
        self.search_pattern = self.__merge_patterns(search_patterns)

    def parse(self, text: str, patterns: List[Tuple[Pattern, Pattern, str]]=None) -> Optional[str]:
        if patterns is None:
            patterns = cast(
                List[Tuple[Pattern, Pattern, str]],
                reduce((lambda x, y: x + list(y)),
                       self.grouped_patterns.values(), []))
        for (extraction_pattern, search_pattern, expression) in patterns:
            match = extraction_pattern.fullmatch(text)
            if match:
                var_parts = ((self.__var_name(group_name), value)
                             for group_name, value in match.groupdict().items())
                # dictionary with the variable names, the values and the types
                var_values = {
                    parts[0]: (value, parts[1])
                    for parts, value in var_parts
                }
                for group in re.finditer('\{(?P<var>[^\}]*)\}', expression):
                    var_name = group['var']
                    if not var_name:
                        # refers to the entire text
                        var_name = ''
                        sub_parse = match.group(0)
                    else:
                        try:
                            (sub_text, sub_type) = var_values[var_name]
                        except:
                            print(var_values)
                            raise IndexError(f"{expression} {var_name}")
                        backref = sub_type == 'backref'
                        sub_parse = None
                        sub_patterns = None

                        if backref:
                            # use the other (preceding patterns) to
                            # evaluate this part of the match
                            pass
                        elif sub_type in self.child_patterns:
                            sub_parse = self.child_patterns[sub_type].parse(
                                sub_text)
                        else:
                            sub_patterns = self.grouped_patterns[sub_type]
                        if sub_parse is None:
                            sub_parse = self.parse(
                                sub_text,
                                sub_patterns)
                        if sub_parse is None:
                            return None
                    expression = re.sub(
                        '\{' + var_name + '\}',
                        sub_parse,
                        expression)
                return expression
        return None

    def __group_name(self, var_name: str, sub_type: str):
        """
        Gets the group name to use for a named group expression.
        """

        return f'{self.type}__{var_name}__{sub_type}'

    def __var_name(self, group_name: str) -> Tuple[str, str]:
        """
        Gets the variable names from the named groups.
        """
        type, var_name, sub_type = group_name.split('__')
        return (var_name, sub_type)

    def __merge_patterns(self, patterns: List[Pattern]) -> str:
        return f"({'|'.join(map(lambda p: cast(str, p.pattern), patterns))})"

    def __compile_pattern(self,
                          parts: List[Dict[str, str]],
                          type_patterns: Dict[str, List[Tuple[Pattern, Pattern, str]]],
                          preceding_patterns: List[Pattern],
                          extraction: bool) -> Pattern:
        """Compile the pattern from csv-file to an executable regular expression.

        Arguments:
            parts {List[Dict[str, str]]} -- The evaluation result from the pattern grammar.
            type_patterns {Dict[str, List[Tuple[Pattern, Pattern, str]]]} -- The dictionary of all the compiled patterns by type.
            preceding_patterns {List[Pattern]} -- The patterns which have already been compiled.
            extraction {bool} -- Whether the compilation should generate a named regular expression to allow for evaluation the associated expression.

        Returns:
            Pattern -- The compiled regular expression
        """
        pattern = ''
        for part in parts:
            if 'words' in part:
                pattern += re.sub(r'[ \t\n]+', r'\\s*',
                                  ' '.join(part['words']))
            else:
                if part['type'] == 'backref':
                    sub_type_expression = self.__merge_patterns(
                        preceding_patterns)
                elif part['type'] in self.child_patterns:
                    sub_type_expression = self.child_patterns[
                        part['type']].search_pattern
                else:
                    sub_type_expression = self.__merge_patterns(
                        list(map(lambda row: row[1], type_patterns[part['type']])))

                if extraction:
                    pattern += f'(?P<{self.__group_name(part["name"], part["type"])}>{sub_type_expression})'
                else:
                    pattern += sub_type_expression
        return re.compile(pattern)

    def search(self, text):
        pos = 0
        for match in re.finditer(self.search_pattern, text):
            (start, end) = match.span()
            if start > pos:
                yield {
                    'text': text[pos:start]
                }
            pos = end
            match_text = match.group(0)
            parsed_text = self.parse(match_text)
            yield {
                'text': match_text,
                'parsed': parsed_text,
                'eval': self.eval(parsed_text)
            }
        if pos < len(text):
            yield {
                'text': text[pos:]
            }
