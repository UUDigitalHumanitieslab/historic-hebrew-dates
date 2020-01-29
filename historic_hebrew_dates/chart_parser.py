from typing import cast, List, Dict, Tuple, Set, TypeVar
from functools import reduce
from .pattern_matcher import PatternMatcher
from .tokenizer import FragmentedToken
from historic_hebrew_dates.pattern_matcher import PatternMatcherState, TokenSpan

T = TypeVar('T', bound='ChartParser')


class ChartParser:
    def __init__(self: T, agenda: List[PatternMatcher]):
        self.agenda = agenda
        self.reset()

    def dictionary(self) -> Set[str]:
        """Retrieves all the tokens which can be matched by the parser.

        Returns:
            Set[str] -- Set of unique tokens
        """
        dictionary = cast(Set[str], set())

        for matcher in self.agenda:
            for token in matcher.dictionary():
                dictionary.add(token)

        return dictionary

    def reset(self):
        # everything starts at zero
        self.agenda_index = 0
        self.token_indexes = cast(Dict[int, int], {})
        for i in range(0, len(self.agenda)):
            self.token_indexes[i] = 0

        self.states = cast(List[PatternMatcherState], [])
        self.tokens = cast(List[FragmentedToken], [])

        # matches at the token start positions containing
        # their associated TokenSpans
        self.matches = cast(List[List[TokenSpan]], [])

    def input(self, tokens: List[FragmentedToken]):
        # start at the lowest agenda again
        self.agenda_index = 0
        for token in tokens:
            self.tokens.append(token)

    def add_child_matches(self, type: str, matches: List[List[TokenSpan]]):
        while len(self.matches) <= len(matches):
            self.matches.append([])

        for index in range(0, len(matches)):
            for match in matches[index]:
                self.matches[index].append(match.clone(type))


    def iterate(self) -> bool:
        """Moves the current matcher one step forward, or shift to the
        next matcher

        Returns:
            bool -- Whether more parsing could be done on the data set
        """

        has_more = False

        # move the current agenda forward
        self.token_indexes[self.agenda_index] += 1
        if self.token_indexes[self.agenda_index] < len(self.tokens):
            has_more = True
        else:
            # try the next matcher on the agenda
            self.agenda_index += 1
            if self.agenda_index < len(self.agenda):
                has_more = True

        if not has_more:
            return False

        matcher = self.agenda[self.agenda_index]
        token_index = self.token_indexes[self.agenda_index]

        while len(self.matches) <= token_index:
            self.matches.append([])

        # insert a new state starting from this position
        self.states.append(PatternMatcherState(matcher, token_index))

        updated_states = cast(List[PatternMatcherState], [])
        new_matches = cast(List[PatternMatcherState], [])
        # tests all states for this agenda
        for state in self.states:
            # retain states for other agendas
            # and for those which are beyond this token
            if state.matcher != matcher or state.position > token_index:
                updated_states.append(state)
                continue
            for interpretation in self.tokens[token_index].interpretations:
                # an ambiguous token could be resolved to multiple realizations
                for token in interpretation:
                    self.__state_next(state, TokenSpan(
                        token_index,
                        None,
                        [token]), updated_states, new_matches)
            for span in self.matches[token_index]:
                self.__state_next(state, span, updated_states, new_matches)
        self.states = updated_states

        for match in new_matches:
            self.matches[match.start_position].append(match.emit())

        return has_more

    def process_all(self):
        while self.iterate():
            pass

    def __state_next(self,
                     state: PatternMatcherState,
                     span: TokenSpan,
                     updated_states: List[PatternMatcherState],
                     matches: List[PatternMatcherState]) -> None:
        if state.test(span):
            next_state=state.clone()
            if next_state.next(span):
                # complete!
                matches.append(next_state)
            else:
                updated_states.append(next_state)
    # def __continue_rule(self,
    #                     index: int,
    #                     matcher: PatternMatcher,
    #                     current_position: int,
    #                     has_more: bool):
    #     self.current_positions[index] += 1
    #     if matcher.next():
    #         # completed match!
    #         self.matches[self.start_positions[index]].append(
    #             (matcher, current_position, matcher.emit()))
    #         matcher.reset()
    #         self.start_positions[index] = self.current_positions[index]
    #     return self.__check_for_more(index, has_more)

    # def __restart_rule(self, index: int, matcher: PatternMatcher, current_position: int, has_more: bool):
    #     # maybe it starts at the next position?
    #     current_position += 1
    #     self.start_positions[index] = current_position
    #     self.current_positions[index] = current_position
    #     matcher.reset()
    #     has_more = self.__check_for_more(index, has_more)
    #     return current_position, has_more

    # def __check_for_more(self, index: int, has_more: bool):
    #     if not has_more:
    #         return self.current_positions[index] < len(self.tokens)
    #     else:
    #         return True

    # def __block_cleared(self, type: str, position: int):
    #     for state in self.states:
    #         if state.type == type and state.start_position < position:
    #             return False
    #     return True
    #     # # determine matches which need to finish before
    #     # # this is allowed to continue; only allow waiting
    #     # # for preceding rules
    #     # for i in range(0, rule_index):
    #     #     if self.agenda[i].type == type:
    #     #         if self.start_positions[i] < position:
    #     #             # this is blocking
    #     #             return False
    #     #         elif self.start_positions[i] == position and \
    #     #                 self.agenda[i].blocked_by_type:
    #     #             # this block is also blocked, that has to be
    #     #             # resolved first
    #     #             return False
    #     # return True

    def __str__(self):
        def format_token_matches(matches: List[TokenSpan]):
            return ", ".join(f":{match.end} {match.type} -> {match.value}" for match in matches)

        formatted_tokens=(
            f"{i}:{format_token_matches(self.matches[i])}" for i in range(0, len(self.matches)))
        return "\n".join(formatted_tokens)
