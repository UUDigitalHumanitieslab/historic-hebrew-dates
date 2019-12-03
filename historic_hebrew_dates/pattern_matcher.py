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
        return f"{{{self.compare}}}"


class PatternMatcher:
    def __init__(self, type: str, parts: List[Union[TokenPart, TypePart]]):
        self.type = type
        self.parts = parts
        self.blocking = cast(List[TokenPart], [])
        self.reset()

    def test(self, token: str, types: Union[Set[str], Dict[str, str]]) -> bool:
        part = self.parts[self.index]
        if part.test(token, types):
            if isinstance(part, TypePart) and isinstance(types, dict):
                # assign the value for this token
                self.values[part.id] = types[part.compare]
            return True
        if isinstance(part, TypePart):
            self.blocked_by_type = cast(Union[str, None], part.compare)
        else:
            self.blocked_by_type = None
        return False


    def next(self) -> bool:
        """Move the index within the pattern

        Returns:
            bool -- Whether the pattern is complete
        """
        self.index += 1
        if self.index == len(self.parts):
            self.complete = True
        return self.complete

    def reset(self):
        self.blocked_by_type = None
        self.index = 0
        self.complete = False

        # contains the possible string value for each id present
        # in this pattern
        self.values = cast(Dict[str, str], {})

    def __str__(self):
        parts_str = " ".join(str(part) for part in self.parts)
        return f"{self.type} [{parts_str}]"
