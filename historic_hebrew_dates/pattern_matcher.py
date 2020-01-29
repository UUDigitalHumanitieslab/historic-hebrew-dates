from typing import Dict, Iterator, List, Union, Set, TypeVar, cast


class TokenSpan:
    def __init__(self, start: int, type: Union[str, None], tokens: List[str], length=None, value=None):
        self.start = start
        self.type = type
        self.tokens = tokens
        self.length = cast(int, length or len(tokens))
        self.value = cast(str, value)

    @property
    def end(self):
        return self.start + self.length

    @property
    def text(self):
        return ' '.join(self.tokens)

    def clone(self, override_type: str = None):
        return TokenSpan(
            self.start,
            override_type or self.type,
            self.tokens,
            self.length,
            self.value)


class TokenPart:
    def __init__(self, compare: str):
        self.text = compare

    def test(self, span: TokenSpan) -> bool:
        return cast(bool, self.text == span.text)

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

    def test(self, span: TokenSpan) -> bool:
        return self.type == span.type

    def __str__(self):
        return f"{{{self.name}}}" if self.name == self.type else f"{{{self.name}:{self.type}}}"


class PatternMatcher:
    def __init__(self, type: str, template: str, parts: List[Union[TokenPart, TypePart]]):
        self.type = type
        self.template = template
        self.parts = parts

    def dictionary(self) -> Iterator[str]:
        """Get all the tokens which are used in the pattern.

        Returns:
            Iterator[str] -- An iteration of token strings
        """
        return map(lambda part: part.text,
                   (part for part in self.parts if isinstance(part, TokenPart)))


T = TypeVar('T', bound='PatternMatcherState')


class PatternMatcherState():
    def __init__(self, matcher: PatternMatcher, position: int = 0):
        self.matcher = matcher

        self.index = 0
        self.start_position = position
        self.position = position

        self.spans = cast(List[TokenSpan], [])

        # contains the string values for each id present
        # in this pattern
        self.values = cast(Dict[str, str], {})

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

    def test(self, span: TokenSpan) -> bool:
        """Test whether the current token matches the pattern.

        Arguments:
            span {TokenSpan} -- Span to test against for possible
                continuation

        Returns:
            bool -- Whether this span matches and the pattern can continue.
        """
        part = self.matcher.parts[self.index]
        if part.test(span):
            return True
        return False

    def next(self, span: TokenSpan) -> bool:
        """Move the index forward within the pattern using the given span.
        It is assumed that the span fits the pattern (use {test()} to check).

        Arguments:
            span {TokenSpan} -- Span to assign to this pattern position
                if this is needed.

        Returns:
            bool -- Whether the pattern is complete
        """
        part = self.matcher.parts[self.index]
        if isinstance(part, TypePart):
            # assign the value for this span
            self.values[part.name] = span.value

        self.index += 1
        self.position += span.length
        self.spans.append(span)
        if self.index == len(self.matcher.parts):
            return True
        return False

    def emit(self) -> TokenSpan:
        tokens = cast(List[str], [])
        for span in self.spans:
            tokens += span.tokens
        output = self.matcher.template
        for id, value in self.values.items():
            output = self.__fill_template(output, id, value)
        return TokenSpan(
            self.start_position,
            self.matcher.type,
            tokens,
            self.position - self.start_position,
            output)

    def clone(self: T) -> T:
        clone = PatternMatcherState(self.matcher, self.position)
        clone.index = self.index
        clone.start_position = self.start_position
        clone.values = {** self.values}
        return cast(T, clone)

    def __fill_template(self, template: str, id: str, value: str) -> str:
        return template.replace(f'{{{id}}}', value)

    def __str__(self):
        parts_str = " ".join(str(part) for part in self.matcher.parts)
        return f"({self.type}) \"{parts_str}\""
