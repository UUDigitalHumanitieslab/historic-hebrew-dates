from typing import Dict, List, Union, Set, cast


class TokenPart:
    def __init__(self, compare: str):
        self.text = compare

    def test(self, span: TextSpan) -> bool:
        return self.text == span.text

    def __str__(self):
        return f"\"{self.type}\""


class BackrefPart:
    def __init__(self, id: str):
        self.name = id

    def __str__(self):
        return f"\"{self.name}\""


class ChildPart:
    def __init__(self, type: str, name: str):
        self.type = type
        self.name = name

    def test(self, span: TokenSpan) -> bool:
        return self.type == span.type

    def __str__(self):
        return f"{{{self.name}}}" if self.name == self.type else f"{{{self.name}:{self.type}}}"


class TypePart:
    def __init__(self, type: str, name: str):
        self.type = type
        self.name = name

    def test(self, token: str, types: Set[str]) -> bool:
        return self.type in types

    def __str__(self):
        return f"{{{self.name}}}" if self.name == self.type else f"{{{self.name}:{self.type}}}"


class PatternMatcher:
    def __init__(self, type: str, template: str, parts: List[Union[TokenPart, TypePart]]):
        self.type = type
        self.template = template
        self.parts = parts


class PatternMatcherState():
    def __init__(self, matcher: PatternMatcher, position: int = 0):
        self.matcher = matcher

        self.index = 0
        self.start_position = position
        self.position = position

        # contains the possible string values for each id present
        # in this pattern
        self.values = cast(Dict[str, List[str]], {})

    def blocked_by(self) -> Union[str, None]:
        """Whether this state depends on another type being parsed first.

        Returns:
            Union[str, None] -- The name of the type to wait for or None.
        """
        part = self.matcher.parts[self.index]
        if isinstance(part, TypePart):
            return cast(Union[str, None], part.type)
        else:
            return None

    def test(self, span: TextSpan) -> bool:
        """Test whether the current token matches the pattern.

        Arguments:
            span {TextSpan} -- Span to test against for possible
                continuation

        Returns:
            bool -- Whether this span matches and the pattern can continue.
        """
        part = self.matcher.parts[self.index]
        if part.test(span):
            return True
        return False

    def next(self, span: TextSpan) -> bool:
        """Move the index forward within the pattern using the given span.
        It is assumed that span fits the pattern (use {test()} to check).

        Arguments:
            span {TextSpan} -- Span to assign to this pattern position
                if this is needed.

        Returns:
            bool -- Whether the pattern is complete
        """
        part = self.matcher.parts[self.index]
        if isinstance(part, TypePart):
            # assign the value for this span
            self.values[part.name] = span.text

        self.index += 1
        self.position += part.len
        if self.index == len(self.parts):
            return True
        return False

    def emit(self) -> List[str]:
        outputs = cast(List[str], [self.matcher.template])
        for id, values in self.values.items():
            transformed = cast(List[str], [])
            for output in outputs:
                transformed += self.__fill_template(output, id, values)
            outputs = transformed
        return outputs

    def clone(self) -> PatternMatcherState:
        clone = PatternMatcherState(self.matcher, self.position)
        clone.index = self.index
        clone.start_position = self.start_position
        clone.values = {** self.values}

    def __fill_template(self, template: str, id: str, values: List[str]) -> List[str]:
        return [template.replace(f'{{{id}}}', value) for value in values]

    def __str__(self):
        parts_str = " ".join(str(part) for part in self.matcher.parts)
        return f"({self.type}) \"{parts_str}\""


class TextSpan:
    def __init__(self, start: int, type: Union[str, None], tokens: List[str], len=None):
        self.start = start
        self.type = type
        self.tokens = tokens
        self.len = cast(int, len or len(self.tokens))

    @property
    def end(self):
        return self.start + self.len

    @property
    def text(self):
        return ' '.join(self.tokens)
