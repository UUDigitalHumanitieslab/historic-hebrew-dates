#!/usr/bin/env python3
import pandas as pd
import re
from bidi.algorithm import get_display

pd.set_option('display.max_colwidth', -1)


class AnnotatedCorpus:
    def __init__(self, filepath):
        self.raw_df = pd.read_excel(filepath, header=0)
        self.cleaned_df = self.raw_df.copy(deep=True)
        self.cleaned_df['Transcription'] = self.cleaned_df['Transcription'] \
            .str.replace('\n', '') \
            .str.replace('[', '') \
            .str.replace(']', '')

    def as_infixed(self):
        pattern = r"(})(\(.+?\))"
        infixed_df = self.cleaned_df.copy(deep=True)
        infixed_df['Transcription'].replace(
            to_replace=pattern, value=r"\2\1", regex=True, inplace=True)
        return infixed_df
