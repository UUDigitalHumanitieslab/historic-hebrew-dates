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
                 value=None,
                 is_captured=False,
                 is_child=False):
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
        self.evaluated = value
        """Whether this span has been captured
        by another completed pattern and should therefor be omitted
        from the results as match.
        """
        self.is_captured = is_captured
        """Whether this span is a match from a child pattern
        """
        self.is_child = is_child

    @property
    def text(self):
        return ' '.join(self.tokens)

    @property
    def len(self):
        return len(self.tokens)

    def clone(self, override_type: str = None, is_child = False):
        cloned = TokenSpan(
            self.start,
            self.interpretation_index,
            self.interpretation_length,
            self.subtoken_index,
            self.last,
            self.last_interpretation_index,
            self.last_interpretation_length,
            self.last_subtoken_index,
            override_type or self.type,
            self.tokens,
            self.value,
            self.is_captured,
            is_child)
        cloned.evaluated = self.evaluated
        return cloned

    def precedes(self, following: T) -> bool:
        """Whether this span, which could be a sub token, directly
        precedes the passed span.

        Arguments:
            following {TokenSpan} -- Span to check

        Returns:
            bool -- Whether this directly textually precedes the passed
                token span.
        """

        if self.last_subtoken_index < self.last_interpretation_length - 1:
            # continue within the subtokens of an interpretation
            return self.last == following.start and \
                self.last_interpretation_index == following.interpretation_index and \
                self.last_subtoken_index == following.subtoken_index - 1
        elif self.last == following.start - 1:
            # this is followed by the start of the next token
            return following.subtoken_index == 0
        else:
            return False

    def before(self, after: T) -> bool:
        """Whether this span is anywhere before the passed span without any overlap.

        Arguments:
            after {TokenSpan} -- Span to check

        Returns:
            bool -- Whether this textually precedes the passed token span.
        """

        if self.last == after.start:
            # before the subtokens of an interpretation
            if self.last_interpretation_index == after.interpretation_index:
                return self.last_subtoken_index < after.subtoken_index
            else:
                # not within the same interpretation
                return False
        else:
            return self.last < after.start

    def contains(self, contained: T) -> bool:
        """Whether this span fully contains the passed span.

        Arguments:
            contained {TokenSpan} -- Span to check

        Returns:
            bool -- Whether this textually contains the passed token span.
        """
        if self.start > contained.start or self.last < contained.last:
            return False

        if self.start == contained.start:
            if self.interpretation_index != contained.interpretation_index or \
                    self.subtoken_index > contained.subtoken_index:
                return False

        if self.last == contained.last:
            if self.last_interpretation_index != contained.last_interpretation_index or \
                    self.last_subtoken_index < contained.last_subtoken_index:
                return False

        return True


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
        return span.type != None

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


U = TypeVar('U', bound='PatternMatcherState')


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
        # if isinstance(part, BackrefPart):
        #     return True, True
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
        if isinstance(part, TypePart) or isinstance(part, BackrefPart):
            # assign the value for this span
            self.values[part.name] = span.evaluated

        self.parts_index += 1
        self.spans.append(span)
        if self.parts_index == len(self.matcher.parts):
            # notify all the spans that they have been captured,
            # and should be omitted from the (usual) results
            for s in self.spans:
                s.is_captured = True

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

    def clone(self: U) -> U:
        clone = PatternMatcherState(self.matcher)
        clone.parts_index = self.parts_index
        clone.spans.extend(self.spans)
        clone.values = {** self.values}
        return cast(U, clone)

    def __fill_template(self, template: str, id: str, value) -> str:
        return template.replace(f'{{{id}}}', str(value))

    def __str__(self):
        parts_str = " ".join(str(part) for part in self.matcher.parts)
        return f"({self.matcher.type}) \"{parts_str}\""
