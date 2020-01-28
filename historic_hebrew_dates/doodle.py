from historic_hebrew_dates.chart_parser import ChartParser
from historic_hebrew_dates.pattern_matcher import TokenPart, TypePart, PatternMatcher
from historic_hebrew_dates.tokenizer import Tokenizer

getallen = [PatternMatcher(
    "getal",
    f"{n}",
    [token_part]) for n, token_part in enumerate([
        TokenPart("een"),
        TokenPart("twee"),
        TokenPart("drie"),
        TokenPart("vier"),
        TokenPart("vijf"),
        TokenPart("zes"),
        TokenPart("zeven"),
        TokenPart("acht"),
        TokenPart("negen")], start=1)]

maanden = [PatternMatcher(
    "maand",
    f"{n}",
    [token_part]) for n, token_part in enumerate([
        TokenPart("januari"),
        TokenPart("februari"),
        TokenPart("maart"),
        TokenPart("april"),
        TokenPart("mei"),
        TokenPart("juni"),
        TokenPart("juli"),
        TokenPart("augustus"),
        TokenPart("september"),
        TokenPart("november"),
        TokenPart("december")], start=1)]

getal_en_maand = PatternMatcher("getal_en_maand", "[dag: {dag}, maand: {maand}]", [
    TypePart("getal", "dag"),
    TypePart("maand", "maand")])

parser = ChartParser(getallen + maanden + [getal_en_maand])
tokenizer = Tokenizer(parser.dictionary())
tokens = list(tokenizer.tokenize("dit is vier februari"))

parser.input(tokens)
# parser.next(token)
# print(parser.position)
# print(parser.matches)

while parser.iterate():
    pass
print(parser)

print("NEXT")
parser.reset()

tokens = tokenizer.tokenize("een februari en nog een tekst ?ee? januari")
parser.input(tokens)

while parser.iterate():
    pass
print(parser)
