#!/usr/bin/env python3
import csv
import os
import re

from collections import ChainMap
from typing import cast, Any, Callable, Dict, Iterable, List, Set, Tuple, Union, Pattern, Optional, TypeVar
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

    def parse(self, tokens: Union[List[str], List[FragmentedToken]], omit_captured=True, hide_overlap=True, eval_values=True) -> List[List[TokenSpan]]:
        self.parser.reset()

        if type(tokens) is str:
            tokens = list(self.tokenizer.tokenize(tokens))

        self.parser.input(tokens)

        for child in self.child_patterns:
            self.parser.add_child_matches(child.type, child.parse(tokens))

        self.parser.process_all()
        matches = self.parser.matches
        if omit_captured:
            matches = list(map(
                lambda token_matches: list(filter(
                    lambda match: not match.is_captured, token_matches)),
                matches))
        if hide_overlap:
            matches = self.__hide_overlap(matches)
        if eval_values:
            for token_matches in matches:
                for match in token_matches:
                    if not match.is_child:
                        match.evaluated = self.eval(match.value)
        return cast(List[List[TokenSpan]], matches)

    def __hide_overlap(self, matches: List[List[TokenSpan]]):
        """Hide matches which are fully overlapped by another match

        Arguments:
            matches {List[List[TokenSpan]]} -- matches to filter

        Returns:
            List[List[TokenSpan]] -- Filtered matches
        """

        filtered_matches = list(matches)

        for token_matches in filtered_matches:
            for match in list(token_matches):
                if match in token_matches:
                    # don't run the check if this match has already been removed
                    self.__remove_overlapping(filtered_matches, match)

        return filtered_matches

    def __remove_overlapping(self, matches: List[List[TokenSpan]], match: TokenSpan) -> None:
        for token_index in range(match.start, match.last + 1):
            token_matches = matches[token_index]
            for candidate in list(token_matches):
                if match != candidate and candidate in token_matches \
                        and match.contains(candidate) \
                        and (match.len > candidate.len
                             or match.text == candidate.text):
                    token_matches.remove(candidate)

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
                    for current_match in current['matches']:
                        if current_match['interpretation'] == current['text']:
                            del current_match['interpretation']
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
                        'type': span.type,
                        'eval': span.evaluated,
                        'interpretation': span.text
                    })
                    if span.last + 1 > match_until:
                        match_until = span.last + 1

                current = {
                    'text': token.text,
                    'matches': mapped_matches
                }
        if current:
            yield current
