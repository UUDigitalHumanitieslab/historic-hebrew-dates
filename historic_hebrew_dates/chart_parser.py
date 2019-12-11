from typing import cast, List, Dict, Tuple, Set
from functools import reduce
from .pattern_matcher import PatternMatcher
from historic_hebrew_dates.pattern_matcher import PatternMatcherState, TextSpan


class ChartParser:
    def __init__(self, agenda: List[PatternMatcher], child_parses: Dict[str, ChartParser] = None):
        self.agenda = agenda

        # each matcher is shifted individually accross the data set
        # this records what their current starting positions are
        self.start_positions = cast(Dict[int, int], {})

        # these retain the current positions of the matcher itself
        # for example the pattern "this is a test"
        # could be looking for "a" after having already found "this is"
        # in the two preceding tokens
        self.current_positions = cast(Dict[int, int], {})
        self.child_parses = child_parses or {}
        self.reset()

    def reset(self):
        # self.position = 0
        self.states = cast(List[PatternMatcherState], [])
        for matcher in self.agenda:
            # start with a state for each matcher
            self.states.append(PatternMatcherState(matcher))
        self.tokens = cast(List[str], [])

        # everything starts at zero
        for i in range(0, len(self.agenda)):
            self.agenda[i].reset()
            # self.start_positions[i] = 0
            # self.current_positions[i] = 0

        # no matches, matches at their position
        # containing their associated TextSpans
        self.matches = cast(
            List[List[TextSpan]], [])

    def input(self, tokens: List[str]):
        position = len(self.tokens)
        for token in tokens:
            self.tokens.append(token)
            position += 1

    def iterate(self) -> bool:
        """Attempt to move all the states one token forward.

        Returns:
            bool -- Whether more parsing could be done on the data set
        """

        has_more = False
        for state in self.states:
            blocked_by = state.blocked_by()
            if blocked_by != None and not self.__block_cleared(blocked_by, state.position):
                has_more = True
            else:
                # TODO: loop through all possible tokens and all possible
                # matches
                if state.position >= len(self.tokens):
                    for span in [TextSpan(state.position, None, [self.tokens[state.position]])] \
                        + self.matches[state.position]:
                        state.test()

        has_more = False
        for index in range(0, len(self.agenda)):
            matcher = self.agenda[index]
            current_position = self.current_positions[index]
            if current_position == len(self.matches):
                self.matches.append([])

            # matched types on this position
            matches = cast(Dict[str, List[str]], {})
            for match, _, values in self.matches[current_position]:
                try:
                    matches[match.type] += values
                except KeyError:
                    matches[match.type] = list(values)

            for type, parser in self.child_parses.items():
                child_values = reduce(
                    list.__add__, parser.matches[current_position].values())
                try:
                    matches[type] += child_values
                except KeyError:
                    matches[match.type] = child_values

            if matcher.test(self.tokens[current_position], matches):
                has_more = self.__continue_rule(
                    index,
                    matcher,
                    current_position,
                    has_more)
            elif matcher.blocked_by_type:
                if self.__block_cleared(
                        matcher.blocked_by_type,
                        index,
                        current_position):
                    # can the rule continue?
                    if matcher.test(self.tokens[current_position], matches):
                        has_more = self.__continue_rule(
                            index,
                            matcher, current_position,
                            has_more)
                    else:
                        # shift the match window to start on this position
                        current_position, has_more = self.__restart_rule(
                            index,
                            matcher,
                            current_position,
                            has_more)
                else:
                    has_more = True
            else:
                current_position, has_more = self.__restart_rule(
                    index,
                    matcher,
                    current_position,
                    has_more)

        return has_more

    def process_all(self):
        while self.iterate():
            pass

    def __continue_rule(self,
                        index: int,
                        matcher: PatternMatcher,
                        current_position: int,
                        has_more: bool):
        self.current_positions[index] += 1
        if matcher.next():
            # completed match!
            self.matches[self.start_positions[index]].append(
                (matcher, current_position, matcher.emit()))
            matcher.reset()
            self.start_positions[index] = self.current_positions[index]
        return self.__check_for_more(index, has_more)

    def __restart_rule(self, index: int, matcher: PatternMatcher, current_position: int, has_more: bool):
        # maybe it starts at the next position?
        current_position += 1
        self.start_positions[index] = current_position
        self.current_positions[index] = current_position
        matcher.reset()
        has_more = self.__check_for_more(index, has_more)
        return current_position, has_more

    def __check_for_more(self, index: int, has_more: bool):
        if not has_more:
            return self.current_positions[index] < len(self.tokens)
        else:
            return True

    def __block_cleared(self, type: str, position: int):
        for state in self.states:
            if state.type == type and state.start_position < position:
                return False
        return True
        # # determine matches which need to finish before
        # # this is allowed to continue; only allow waiting
        # # for preceding rules
        # for i in range(0, rule_index):
        #     if self.agenda[i].type == type:
        #         if self.start_positions[i] < position:
        #             # this is blocking
        #             return False
        #         elif self.start_positions[i] == position and \
        #                 self.agenda[i].blocked_by_type:
        #             # this block is also blocked, that has to be
        #             # resolved first
        #             return False
        # return True

    def __str__(self):
        def format_token_matches(matches: List[Tuple[PatternMatcher, int, List[str]]]):
            return ", ".join(f":{end_position} {pattern_matcher} -> {';'.join(values)}" for (pattern_matcher, end_position, values) in matches)

        formatted_tokens = (
            f"{i}:{format_token_matches(self.matches[i])}" for i in range(0, len(self.matches)))
        return "\n".join(formatted_tokens)
