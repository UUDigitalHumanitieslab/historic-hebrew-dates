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
                test = re.compile('^' + item.replace('?', '.').replace('.', '.*') + '$')
                interpretations = []
                for candidate in self.dictionary:
                    if test.search(candidate):
                        interpretations.append([candidate])
                if interpretations:
                    yield FragmentedToken(item, interpretations)
            else:
                yield FragmentedToken(item, [[item]])
