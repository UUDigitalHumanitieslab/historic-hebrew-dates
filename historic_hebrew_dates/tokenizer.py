from typing import Iterable, List, Set
import re


class FragmentedToken:
    def __init__(self, text: str, interpretations: List[List[str]]):
        self.text = text
        self.interpretations = interpretations


class Tokenizer:
    def __init__(self, dictionary: Set[str]):
        # search for keys, case insensitively
        self.dictionary = {
            item.casefold(): item for item in dictionary
        }

    # TODO: this should preserve whitespace
    def tokenize(self, text: str) -> Iterable[FragmentedToken]:
        splitted = text.split()
        for item in splitted:
            if '?' in item or '.' in item:
                # basic implementation, only supports wildcards and single tokens
                test = re.compile(
                    '^' + item.replace('?', '.').replace('.', '.*') + '$', re.IGNORECASE)
                interpretations = []
                for candidate in self.dictionary:
                    if test.search(candidate):
                        interpretations.append([candidate])
                if interpretations:
                    yield FragmentedToken(item, interpretations)
            elif item.casefold() in self.dictionary:
                # known text
                yield FragmentedToken(item, [[self.dictionary[item.casefold()]]])
            else:
                # see if this token could be splitted into multiple
                # tokens
                interpretations = list(self.subdivide(item))
                if interpretations:
                    yield FragmentedToken(item, interpretations)
                else:
                    # yield the text as-is
                    yield FragmentedToken(item, [[item]])

    def subdivide(self, item: str) -> Iterable[List[str]]:
        """Divide an unknown token into multiple known tokens, if possible

        Arguments:
            item {str} -- The text to divide

        Yields:
            Iterable[List[str]] -- A list of tokens completely spanning the text
        """
        for (casefold_candidate, candidate) in self.dictionary.items():
            casefold_item = item.casefold()
            if casefold_item == casefold_candidate:
                yield [candidate]
            elif casefold_item.startswith(casefold_candidate):
                for additional in self.subdivide(casefold_item[len(casefold_candidate):]):
                    yield [candidate] + additional
