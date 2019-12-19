from typing import cast, List, Dict, Tuple, Set, TypeVar
from functools import reduce
from .pattern_matcher import PatternMatcher
from historic_hebrew_dates.pattern_matcher import PatternMatcherState, TokenSpan

T = TypeVar('T', bound='ChartParser')


class ChartParser:
    def __init__(self: T, agenda: List[PatternMatcher], child_parses: Dict[str, T] = None):
        self.agenda = agenda
        self.child_parses = child_parses or {}
        self.reset()

    def reset(self):
        # everything starts at zero
        self.agenda_index = 0
        self.token_indexes = cast(Dict[int, int], {})
        for i in range(0, len(agenda)):
            self.token_indexes[i] = 0

        self.states = cast(List[PatternMatcherState], [])
        self.tokens = cast(List[str], [])

        # no matches, matches at their position
        # containing their associated TokenSpans
        self.matches = cast(
            List[List[TokenSpan]], [])

    def input(self, tokens: List[str]):
        # start at the lowest agenda again
        self.agenda_index = 0
        for token in tokens:
            self.tokens.append(token)

    def iterate(self) -> bool:
        """Moves the current matcher one step forward, or shift to the
        next matcher

        Returns:
            bool -- Whether more parsing could be done on the data set
        """

        has_more = False
        self.token_indexes[self.agenda_index] += 1
        if self.token_indexes[self.agenda_index] < len(self.tokens):
            has_more = True
        else:
            self.agenda_index += 1
            if self.agenda_index < len(self.agenda_index):
                has_more = True

        if not has_more:
            return False

        matcher = self.agenda[self.agenda_index]
        token_index = self.token_indexes[self.agenda_index]

        while token_index < len(self.matches):
            self.matches.append([])

        # insert a new state starting from this position
        self.states.append(PatternMatcherState(matcher, token_index))

        updated_states = []
        # tests all states for this agenda
        for state in self.states:
            if state.matcher != matcher or state.position > token_index:
                updated_states.append(state)
                continue
            first = True
            for span in [TokenSpan(
                    token_index,
                    None,
                    [self.tokens[token_index]])] + \
                    self.matches[token_index]:
                if state.test(span):
                    # no need to clone the first match
                    next_state = state if first else state.clone()
                    first = False
                    if next_state.next(state):
                        # complete!
                        self.matches[state.start_position].append(state.emit())
                    else:
                        updated_states.append(next_state)
        self.states = updated_states

        # # if necessary: clone for all matches on this position
        # # matches? forward
        # # no match? remove

        # # for all state
        # for state in self.states:
        #     blocked_by = state.blocked_by()
        #     if blocked_by != None and not self.__block_cleared(blocked_by, state.position):
        #         has_more = True
        #     else:
        #         # TODO: loop through all possible tokens and all possible
        #         # matches
        #         if state.position >= len(self.tokens):
        #             for span in [TokenSpan(state.position, None, [self.tokens[state.position]])] \
        #                     + self.matches[state.position]:
        #                 state.test()

        # has_more = False
        # for index in range(0, len(self.agenda)):
        #     matcher = self.agenda[index]
        #     current_position = self.current_positions[index]
        #     if current_position == len(self.matches):
        #         self.matches.append([])

        #     # matched types on this position
        #     matches = cast(Dict[str, List[str]], {})
        #     for match, _, values in self.matches[current_position]:
        #         try:
        #             matches[match.type] += values
        #         except KeyError:
        #             matches[match.type] = list(values)

        #     for type, parser in self.child_parses.items():
        #         child_values = reduce(
        #             list.__add__, parser.matches[current_position].values())
        #         try:
        #             matches[type] += child_values
        #         except KeyError:
        #             matches[match.type] = child_values

        #     if matcher.test(self.tokens[current_position], matches):
        #         has_more = self.__continue_rule(
        #             index,
        #             matcher,
        #             current_position,
        #             has_more)
        #     elif matcher.blocked_by_type:
        #         if self.__block_cleared(
        #                 matcher.blocked_by_type,
        #                 index,
        #                 current_position):
        #             # can the rule continue?
        #             if matcher.test(self.tokens[current_position], matches):
        #                 has_more = self.__continue_rule(
        #                     index,
        #                     matcher, current_position,
        #                     has_more)
        #             else:
        #                 # shift the match window to start on this position
        #                 current_position, has_more = self.__restart_rule(
        #                     index,
        #                     matcher,
        #                     current_position,
        #                     has_more)
        #         else:
        #             has_more = True
        #     else:
        #         current_position, has_more = self.__restart_rule(
        #             index,
        #             matcher,
        #             current_position,
        #             has_more)

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
