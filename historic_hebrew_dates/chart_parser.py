from typing import cast, List, Dict, Tuple, Set
from .pattern_matcher import PatternMatcher


class ChartParser:
    def __init__(self, agenda: List[PatternMatcher]):
        self.agenda = agenda
        self.start_positions = cast(Dict[int, int], {})
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
        # containing their associated PatternMatcher and inclusive
        # end position
        self.matches = cast(List[List[Tuple[PatternMatcher, int]]], [])

    def input(self, tokens: List[str]):
        self.tokens += tokens

    def iterate(self) -> bool:
        has_more = False
        for i in range(0, len(self.agenda)):
            matcher = self.agenda[i]
            current_position = self.current_positions[i]
            if current_position == len(self.matches):
                self.matches.append([])

            types = set()
            for match, _ in self.matches[current_position]:
                types.add(match.type)

            def continue_rule():
                nonlocal matcher, check_for_more, current_position
                self.current_positions[i] += 1
                if matcher.next():
                    # completed match!
                    self.matches[self.start_positions[i]].append(
                        (matcher, current_position))
                    matcher.reset()
                    # types.add(matcher.type)
                    self.start_positions[i] = self.current_positions[i]
                check_for_more()

            def restart_rule():
                nonlocal matcher, check_for_more, current_position
                # maybe it starts at the next position?
                current_position += 1
                self.start_positions[i] = current_position
                self.current_positions[i] = current_position
                matcher.reset()
                check_for_more()

            def check_for_more():
                nonlocal has_more
                if not has_more:
                    has_more = self.current_positions[i] < len(self.tokens)

            if matcher.test(self.tokens[current_position], types):
                continue_rule()
            elif matcher.blocked_by_type:
                if self.__block_cleared(matcher.blocked_by_type, i, current_position):
                    # can the rule continue?
                    if matcher.test(self.tokens[current_position], types):
                        continue_rule()
                    else:
                        restart_rule()
                else:
                    has_more = True
            else:
                restart_rule()

        return has_more

    def __block_cleared(self, type: str, rule_index: int, position: int):
        # determine matches which need to finish before
        # this is allowed to continue; only allow waiting
        # for preceding rules
        for i in range(0, rule_index):
            if self.agenda[i].type == type:
                if self.current_positions[i] < position:
                    # this is blocking
                    return False
                elif self.current_positions[i] == position and \
                        self.agenda[i].blocked_by_type:
                    # this block is also blocked, that has to be
                    # resolved first
                    return False
        return True

    def __str__(self):
        def format_token_matches(matches: List[Tuple[PatternMatcher, int]]):
            return ", ".join(f":{end_position} {pattern_matcher}" for (pattern_matcher, end_position) in matches)

        formatted_tokens = (f"{i}:{format_token_matches(self.matches[i])}" for i in range(0, len(self.matches)))
        return "\n".join(formatted_tokens)
