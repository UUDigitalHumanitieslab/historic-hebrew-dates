#!/usr/bin/env python3
import csv
import os
import re

from collections import ChainMap
from typing import cast, Any, Callable, Dict, Iterable, List, Set, Tuple, Pattern, Optional, TypeVar
from functools import reduce

from .grammars.pattern_grammar import get_parts
from .chart_parser import ChartParser
from .pattern_matcher import PatternMatcher, TokenSpan
from .tokenizer import FragmentedToken, Tokenizer
from historic_hebrew_dates.pattern_matcher import BackrefPart, ChildPart, TokenPart, TypePart

T = TypeVar('T', bound='PatternParser')

class PatternParser:
    def __init__(self,
                 filename: str,
                 type: str,
                 eval_func: Callable[[str], Any],
                 child_patterns: List[T] = [],
                 rows=None):
        self.type = type
        self.child_patterns = child_patterns
        self.child_dictionaries = cast(Set[str], set())
        for child in child_patterns:
            self.child_dictionaries |= child.dictionary()

        self.eval = eval_func
        if rows:
            self.__parse_rows(rows)
        else:
            with open(os.path.join(os.path.dirname(__file__), 'patterns', filename), encoding='utf-8-sig') as patterns:
                rows = csv.reader(patterns, delimiter=',', quotechar='"')
                next(rows)  # skip header
                self.__parse_rows(rows)

    def __parse_rows(self, rows: List[List[str]]):
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

        matchers = cast(List[PatternMatcher], [])
        for pattern_type in pattern_type_order:
            for pattern, expression in grouped_patterns_str[pattern_type]:
                parts = get_parts(pattern)
                matcher = self.__compile_matcher(
                    pattern_type,
                    expression,
                    parts)

                matchers.append(matcher)

        self.parser = ChartParser(matchers)
        self.tokenizer = Tokenizer(self.dictionary())

    def dictionary(self) -> Set[str]:
        return self.parser.dictionary() | self.child_dictionaries

    def search(self, text: str):
        tokens = list(self.tokenizer.tokenize(text))
        matches = self.parse(tokens)

        return list(self.__format_matches(tokens, matches))

    def parse(self, tokens: List[FragmentedToken]) -> List[List[TokenSpan]]:
        self.parser.reset()
        self.parser.input(tokens)

        for child in self.child_patterns:
            self.parser.add_child_matches(child.type, child.parse(tokens))

        self.parser.process_all()
        return cast(List[List[TokenSpan]], self.parser.matches)
        # if patterns is None:
        #     patterns = cast(
        #         List[Tuple[Pattern, Pattern, str]],
        #         reduce((lambda x, y: x + list(y)),
        #                self.grouped_patterns.values(), []))
        # for (extraction_pattern, search_pattern, expression) in patterns:
        #     match = extraction_pattern.fullmatch(text)
        #     if match:
        #         var_parts = ((self.__var_name(group_name), value)
        #                      for group_name, value in match.groupdict().items())
        #         # dictionary with the variable names, the values and the types
        #         var_values = {
        #             parts[0]: (value, parts[1])
        #             for parts, value in var_parts
        #         }
        #         for group in re.finditer('\{(?P<var>[^\}]*)\}', expression):
        #             var_name = group['var']
        #             if not var_name:
        #                 # refers to the entire text
        #                 var_name = ''
        #                 sub_parse = match.group(0)
        #             else:
        #                 try:
        #                     (sub_text, sub_type) = var_values[var_name]
        #                 except:
        #                     print(var_values)
        #                     raise IndexError(f"{expression} {var_name}")
        #                 backref = sub_type == 'backref'
        #                 sub_parse = None
        #                 sub_patterns = None

        #                 if backref:
        #                     # use the other (preceding patterns) to
        #                     # evaluate this part of the match
        #                     pass
        #                 elif sub_type in self.child_patterns:
        #                     sub_parse = self.child_patterns[sub_type].parse(
        #                         sub_text,
        #                         evaluate)
        #                 else:
        #                     sub_patterns = self.grouped_patterns[sub_type]
        #                 if sub_parse is None:
        #                     sub_parse = self.parse(
        #                         sub_text,
        #                         evaluate,
        #                         sub_patterns)
        #                 if sub_parse is None:
        #                     return None
        #             expression = re.sub(
        #                 '\{' + var_name + '\}',
        #                 str(sub_parse),
        #                 expression)
        #         return self.eval(expression) if evaluate else expression
        # return None

    # def __group_name(self, var_name: str, sub_type: str):
    #     """
    #     Gets the group name to use for a named group expression.
    #     """

    #     return f'{self.type}__{var_name}__{sub_type}'

    # def __var_name(self, group_name: str) -> Tuple[str, str]:
    #     """
    #     Gets the variable names from the named groups.
    #     """
    #     type, var_name, sub_type = group_name.split('__')
    #     return (var_name, sub_type)

    # def __merge_patterns(self, patterns: List[Pattern]) -> str:
    #     # have the longest patterns first: try to match long patterns
    #     # otherwise it is more likely to have multiple smaller matches
    #     # e.g. two hundred would match 2 and 100 instead of 2*100 -> 200.
    #     sorted = list(map(lambda p: cast(str, p.pattern), patterns))
    #     sorted.sort(key=len, reverse=True)
    #     return f"({'|'.join(sorted)})"

    def __convert_part(self, part):
        if 'words' in part:
            words = ' '.join(part['words']).lower()
            regularized_whitespace = re.sub(r'[ \t\n]+', ' ', words)
            tokens = re.split('[ -]', regularized_whitespace)
            return [TokenPart(token) for token in tokens if token]
        else:
            if part['type'] == 'backref':
                return [BackrefPart(part['name'])]
            elif part['type'] in self.child_patterns:
                return [ChildPart(part['type'], part['name'])]
            else:
                return [TypePart(part['type'], part['name'])]

    def __compile_matcher(self, pattern_type: str, expression: str, parts: List[Dict[str, str]]) -> PatternMatcher:
        """Compile the pattern from csv-file to a matcher which can be used by the chart parter.

        Arguments:
            pattern_type {str} -- The type name of this pattern.
            expression {str} -- The expression template.
            parts {List[Dict[str, str]]} -- The evaluation result from the pattern grammar.

        Returns:
            PatternMatcher -- The pattern matcher to apply
        """
        return PatternMatcher(
            pattern_type,
            expression,
            reduce(list.__add__, (self.__convert_part(part) for part in parts)))

    def __format_matches(self, tokens: List[FragmentedToken], matches: List[List[TokenSpan]]):
        current = cast(Dict[str, Any], {})
        match_until = 0

        for i in range(0, len(tokens)):
            token = tokens[i]
            match = matches[i]
            if not match:
                if current == {}:
                    current = {
                        'text': token.text
                    }
                elif 'matches' in current and match_until < i + 1:
                    yield current
                    current = {
                        'text': token.text
                    }
                else:
                    current['text'] += ' ' + token.text
            else:
                if current:
                    yield current
                mapped_matches = []
                for span in match:
                    mapped_matches.append({
                        'parsed': span.value,
                        'eval': self.eval(span.value)
                    })
                    if span.end > match_until:
                        match_until = span.end

                current = {
                    'text': token.text,
                    'matches': mapped_matches
                }
        if current:
            yield current
