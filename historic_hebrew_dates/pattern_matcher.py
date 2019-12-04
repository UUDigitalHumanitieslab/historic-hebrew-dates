from typing import Dict, List, Union, Set, cast


class TokenPart:
    def __init__(self, compare: str):
        self.compare = compare

    def test(self, token: str, types: Set[str]) -> bool:
        return self.compare == token

    def __str__(self):
        return f"\"{self.compare}\""


class TypePart:
    def __init__(self, compare: str, id: str):
        self.compare = compare
        self.id = id

    def test(self, token: str, types: Set[str]) -> bool:
        return self.compare in types

    def __str__(self):
        return f"{{{self.id}}}" if self.id == self.compare else f"{{{self.id}:{self.compare}}}"


class PatternMatcher:
    def __init__(self, type: str, template: str, parts: List[Union[TokenPart, TypePart]]):
        self.type = type
        self.template = template
        self.parts = parts

        self.blocking = cast(List[TokenPart], [])
        self.reset()

    def test(self, token: str, matches: Union[Set[str], Dict[str, List[str]]]) -> bool:
        """Test whether the current token matches the pattern.

        Arguments:
            token {str} -- The string value of the current token
            matches {Union[Set[str], Dict[str, str]]} -- Other patterns which
                matched starting from this token; either only contains a set
                of type names, or type names and their interpolated
                string values.

        Returns:
            bool -- Whether this token matches and the pattern can continue,
                if it doesn't match it could be because it didn't match
                an other pattern type expected here. {blocked_by_type}
                will be set to the type name in such a case.
        """
        part = self.parts[self.index]
        if part.test(token, matches):
            if isinstance(part, TypePart) and isinstance(matches, dict):
                # assign the value for this token
                self.values[part.id] = matches[part.compare]
            return True
        if isinstance(part, TypePart):
            self.blocked_by_type = cast(Union[str, None], part.compare)
        else:
            self.blocked_by_type = None
        return False

    def next(self) -> bool:
        """Move the index forward within the pattern

        Returns:
            bool -- Whether the pattern is complete
        """
        self.index += 1
        if self.index == len(self.parts):
            self.complete = True
        return self.complete

    def emit(self) -> List[str]:
        outputs = cast(List[str], [self.template])
        for id, values in self.values.items():
            transformed = cast(List[str], [])
            for output in outputs:
                transformed += self.__fill_template(output, id, values)
            outputs = transformed
        return outputs

    def reset(self):
        self.blocked_by_type = None
        self.index = 0
        self.complete = False

        # contains the possible string values for each id present
        # in this pattern
        self.values = cast(Dict[str, List[str]], {})

    def __fill_template(self, template: str, id: str, values: List[str]) -> List[str]:
        return [template.replace(f'{{{id}}}', value) for value in values]

    def __str__(self):
        parts_str = " ".join(str(part) for part in self.parts)
        return f"({self.type}) \"{parts_str}\""
