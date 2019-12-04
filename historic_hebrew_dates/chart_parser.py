from typing import cast, List, Dict, Tuple, Set
from .pattern_matcher import PatternMatcher


class ChartParser:
    def __init__(self, agenda: List[PatternMatcher]):
        self.agenda = agenda

        # each matcher is shifted individually accross the data set
        # this records what their current starting positions are
        self.start_positions = cast(Dict[int, int], {})

        # these retain the current positions of the matcher itself
        # for example the pattern "this is a test"
        # could be looking for "a" after having already found "this is"
        # in the two preceding tokens
        self.current_positions = cast(Dict[int, int], {})
        self.reset()

    def reset(self):
        self.position = 0
        self.tokens = cast(List[str], [])

        # everything starts at zero
        for i in range(0, len(self.agenda)):
            self.agenda[i].reset()
            self.start_positions[i] = 0
            self.current_positions[i] = 0

        # no matches, matches at their position
        # containing their associated PatternMatcher, inclusive
        # end position and filled templates
        self.matches = cast(List[List[Tuple[PatternMatcher, int, List[str]]]], [])

    def input(self, tokens: List[str]):
        self.tokens += tokens

    def iterate(self) -> bool:
        """Attempt to move all the matchers one token forward.

        Returns:
            bool -- Whether more parsing could be done on the data set
        """
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

    def __block_cleared(self, type: str, rule_index: int, position: int):
        # determine matches which need to finish before
        # this is allowed to continue; only allow waiting
        # for preceding rules
        for i in range(0, rule_index):
            if self.agenda[i].type == type:
                if self.start_positions[i] < position:
                    # this is blocking
                    return False
                elif self.start_positions[i] == position and \
                        self.agenda[i].blocked_by_type:
                    # this block is also blocked, that has to be
                    # resolved first
                    return False
        return True

    def __str__(self):
        def format_token_matches(matches: List[Tuple[PatternMatcher, int, List[str]]]):
            return ", ".join(f":{end_position} {pattern_matcher} -> {';'.join(values)}" for (pattern_matcher, end_position, values) in matches)

        formatted_tokens = (
            f"{i}:{format_token_matches(self.matches[i])}" for i in range(0, len(self.matches)))
        return "\n".join(formatted_tokens)
