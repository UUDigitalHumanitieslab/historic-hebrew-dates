from typing import cast, List, Dict, Tuple, Set, TypeVar
from functools import reduce
from itertools import chain
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
        # their associated TokenSpans (including
        # position information for potential sub tokens)
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

        updated_states = cast(List[PatternMatcherState], [])
        new_matches = cast(List[PatternMatcherState], [])

        # insert a new state to check whether a pattern starts from this
        # (sub) token index
        check_states = list(chain(
            filter(lambda state: state.matcher == matcher and state.position == token_index,
                   self.states),
            [PatternMatcherState(matcher)]))

        self.__place_matches(token_index, check_states, updated_states, new_matches)

        # tests all states for this agenda
        interpretations = self.tokens[token_index].interpretations
        for interpretation_index, interpretation in enumerate(interpretations):
            # an ambiguous token could be resolved to multiple realizations
            for subtoken_index, subtoken in enumerate(interpretation):
                self.__place_matches(token_index, check_states + updated_states, updated_states, new_matches)

                self.__states_next(check_states + updated_states, TokenSpan(
                    token_index,
                    interpretation_index,
                    len(interpretations),
                    subtoken_index,
                    token_index,
                    interpretation_index,
                    len(interpretations),
                    subtoken_index,
                    None,
                    [subtoken]), updated_states, new_matches)

        self.__place_matches(token_index, check_states + updated_states, updated_states, new_matches)

        for state in self.states:
            # retain states for other agendas
            # and for those which are beyond this token
            if state.matcher != matcher or state.position > token_index:
                updated_states.append(state)
                continue

        self.states = updated_states

        for match in new_matches:
            span = match.emit()
            self.matches[span.start].append(span)

        return has_more

    def process_all(self):
        while self.iterate():
            pass

    def __place_matches(self,
        token_index: int,
        states: List[PatternMatcherState],
        updated_states: List[PatternMatcherState],
        matches: List[PatternMatcherState]):
        """
        Attempt to continue the states using the existing
        matches on this position.
        """

        any_match = True
        check_states = states
        while any_match:
            any_match = False
            for span in self.matches[token_index]:
                # could the pattern continue using an existing match on this (sub)token?
                any_match |= self.__states_next(
                    check_states,
                    span,
                    updated_states,
                    matches)
                check_states = updated_states


    def __states_next(self,
                      states: List[PatternMatcherState],
                      span: TokenSpan,
                      updated_states: List[PatternMatcherState],
                      matches: List[PatternMatcherState]) -> bool:
        any_match = False
        for state in states:
            is_match, is_backref = state.test(span)
            if is_match:
                any_match = True
                if is_backref:
                    # backref continues on all existing matches on this position
                    for match in list(matches):
                        self.__state_next_span(
                            state, match.emit(), updated_states, matches)
                else:
                    self.__state_next_span(
                        state, span, updated_states, matches)
        return any_match

    def __state_next_span(self,
                          state: PatternMatcherState,
                          span: TokenSpan,
                          updated_states: List[PatternMatcherState],
                          matches: List[PatternMatcherState]):
        next_state = state.clone()
        if next_state.next(span):
            # complete!
            matches.append(next_state)
        else:
            updated_states.append(next_state)

    def __str__(self):
        def format_token_matches(matches: List[TokenSpan]):
            return ", ".join(f":{match.last} {match.type} -> {match.value}" for match in matches)

        formatted_tokens = (
            f"{i}:{format_token_matches(self.matches[i])}" for i in range(0, len(self.matches)))
        return "\n".join(formatted_tokens)
