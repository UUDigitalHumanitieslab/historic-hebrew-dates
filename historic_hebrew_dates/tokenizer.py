from typing import List, Set
import re


class FragmentedToken:
    def __init__(self, text: str, interpretations: List[List[str]]):
        self.text = text
        self.interpretations = interpretations


class Tokenizer:
    def __init__(self, dictionary: Set[str]):
        self.dictionary = dictionary

    def tokenize(self, text: str):
        splitted = text.split()
        for item in splitted:
            if '?' in item or '.' in item:
                # basic implementation, only supports wildcards and single tokens
                test = re.compile(
                    '^' + item.replace('?', '.').replace('.', '.*') + '$')
                interpretations = []
                for candidate in self.dictionary:
                    if test.search(candidate):
                        interpretations.append([candidate])
                if interpretations:
                    yield FragmentedToken(item, interpretations)
            elif item in self.dictionary:
                # known text
                yield FragmentedToken(item, [[item]])
            else:
                # see if this token could be splitted into multiple
                # tokens
                interpretations = list(self.subdivide(item))
                if interpretations:
                    yield FragmentedToken(item, interpretations)
                else:
                    # yield the text as-is
                    yield FragmentedToken(item, [[item]])

    def subdivide(self, item: str) -> List[str]:
        """Divide an unknown token into multiple known tokens, if possible

        Arguments:
            item {str} -- The text to divide

        Yields:
            List[str] -- A list of tokens completely spanning the text
        """
        for candidate in self.dictionary:
            if item == candidate:
                yield [candidate]
            elif item.startswith(candidate):
                for additional in self.subdivide(item[len(candidate):]):
                    yield [candidate] + additional
