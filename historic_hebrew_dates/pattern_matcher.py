from typing import Dict, Iterator, List, Union, Set, Tuple, TypeVar, cast

T = TypeVar('T', bound='TokenSpan')


class TokenSpan:
    def __init__(self,
                 start: int,
                 interpretation_index: int,
                 interpretation_length: int,
                 subtoken_index: int,
                 last: int,
                 last_interpretation_index: int,
                 last_interpretation_length: int,
                 last_subtoken_index: int,
                 type: Union[str, None],
                 tokens: List[str],
                 value=None):
        self.start = start
        self.interpretation_index = interpretation_index
        self.interpretation_length = interpretation_length
        self.subtoken_index = subtoken_index
        self.last = last
        self.last_interpretation_index = last_interpretation_index
        self.last_interpretation_length = last_interpretation_length
        self.last_subtoken_index = last_subtoken_index
        self.type = type
        self.tokens = tokens
        self.value = cast(str, value)

    @property
    def text(self):
        return ' '.join(self.tokens)

    def clone(self, override_type: str = None):
        return TokenSpan(
            self.start,
            self.interpretation_index,
            self.interpretation_length,
            self.subtoken_index,
            self.end,
            self.last_interpretation_index,
            self.last_interpretation_length,
            self.last_subtoken_index,
            override_type or self.type,
            self.tokens,
            self.value)

    def precedes(self, following: T) -> bool:
        """Whether this span, which could be a sub token, directly
        precedes the passed span.

        Arguments:
            following {TokenSpan} -- Span to check

        Returns:
            bool -- Whether this directly textually precedes the passed
                token
        """

        if self.last_subtoken_index < self.last_interpretation_length - 1:
            # within an interpretation
            return self.interpretation_index == following.last_interpretation_index and \
                self.subtoken_index == following.last_subtoken_index - 1
        elif self.last == following.start - 1:
            # this is followed by the start of the next token
            return following.subtoken_index == 0
        else:
            return False


class TokenPart:
    def __init__(self, compare: str):
        self.text = compare

    def test(self, span: TokenSpan) -> bool:
        return cast(bool, self.text == span.text)

    def __str__(self):
        return f"\"{self.text}\""


class BackrefPart:
    def __init__(self, id: str):
        self.name = id

    def test(self, span: TokenSpan) -> bool:
        raise Exception("Back-reference should be checked by the parser")

    def __str__(self):
        return f"@{self.name}"


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
    def __init__(self, matcher: PatternMatcher):  # , position: int = 0):
        self.matcher = matcher

        # a matcher is a list of parts to match, this sets the index
        self.parts_index = 0

        self.spans = cast(List[TokenSpan], [])

        # contains the string values for each id present
        # in this pattern
        self.values = cast(Dict[str, str], {})

    @property
    def position(self) -> int:
        """Current token position

        Returns:
            int -- Last inclusive(!) index of this pattern in the
                tokenized input
        """
        try:
            return self.spans[-1].last
        except IndexError:
            return 0

    def blocked_by(self) -> Union[str, None]:
        """Whether this state depends on another type being parsed first.

        Returns:
            Union[str, None] -- The name of the type to wait for or None.
        """
        part = self.matcher.parts[self.parts_index]
        if isinstance(part, TypePart):
            return cast(Union[str, None], part.type)
        else:
            return None

    def test(self, span: TokenSpan) -> Tuple[bool, bool]:
        """Test whether the current token matches the pattern.

        Arguments:
            span {TokenSpan} -- Span to test against for possible
                continuation
            matches {List[PatternMatcherState]} -- Other matches on this position

        Returns:
            Tuple[bool, bool] -- 0: Whether this span matches and the pattern can continue,
                1: Whether this entails a backreference
        """
        if len(self.spans) > 0 and not self.spans[-1].precedes(span):
            return False, False

        part = self.matcher.parts[self.parts_index]
        if isinstance(part, BackrefPart):
            return True, True
        if part.test(span):
            return True, False
        return False, False

    def next(self, span: TokenSpan) -> bool:
        """Move the index forward within the pattern using the given span.
        It is assumed that the span fits the pattern (use {test()} to check).

        Arguments:
            span {TokenSpan} -- Span to assign to this pattern position
                if this is needed.

        Returns:
            bool -- Whether the pattern is complete
        """
        part = self.matcher.parts[self.parts_index]
        if isinstance(part, TypePart):
            # assign the value for this span
            self.values[part.name] = span.value

        self.parts_index += 1
        # self.token_position += span.length
        self.spans.append(span)
        if self.parts_index == len(self.matcher.parts):
            return True
        return False

    def emit(self) -> TokenSpan:
        tokens = cast(List[str], [])
        for span in self.spans:
            tokens += span.tokens
        output = self.matcher.template
        for id, value in self.values.items():
            output = self.__fill_template(output, id, value)
        start = self.spans[0]
        end = self.spans[-1]
        return TokenSpan(
            start.start,
            start.interpretation_index,
            start.interpretation_length,
            start.subtoken_index,
            end.last,
            end.last_interpretation_index,
            end.last_interpretation_length,
            end.last_subtoken_index,
            self.matcher.type,
            tokens,
            output)

    def clone(self: T) -> T:
        clone = PatternMatcherState(self.matcher)  # , self.token_position)
        clone.parts_index = self.parts_index
        clone.spans.extend(self.spans)
        clone.values = {** self.values}
        return cast(T, clone)

    def __fill_template(self, template: str, id: str, value: str) -> str:
        return template.replace(f'{{{id}}}', value)

    def __str__(self):
        parts_str = " ".join(str(part) for part in self.matcher.parts)
        return f"({self.matcher.type}) \"{parts_str}\""
