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
    def __init__(self, matcher: PatternMatcher):
        self.matcher = matcher

        self.blocking = cast(List[TokenPart], [])
        self.reset()

    def test(self, span: TextSpan) -> bool:
        """Test whether the current token matches the pattern.

        Arguments:
            span {TextSpan} -- Span to test against for possible
                continuation

        Returns:
            bool -- Whether this span matches and the pattern can continue,
                if it doesn't match it could be because it didn't match
                an other pattern type expected here. {blocked_by_type}
                will be set to the type name in such a case.
        """
        part = self.matcher.parts[self.index]
        if part.test(span):
            if isinstance(part, TypePart):
                # assign the value for this token
                self.values[part.name] = span.text
            return True
        if isinstance(part, TypePart):
            self.blocked_by_type = cast(Union[str, None], part.type)
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
        outputs = cast(List[str], [self.matcher.template])
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
        parts_str = " ".join(str(part) for part in self.matcher.parts)
        return f"({self.type}) \"{parts_str}\""


class TextSpan:
    def __init__(self, start: int, type: Union[str, None], tokens: List[str]):
        self.start = start
        self.type = type
        self.tokens = tokens

    @property
    def end(self):
        return self.start + len(self.tokens)

    @property
    def text(self):
        return ' '.join(self.tokens)
