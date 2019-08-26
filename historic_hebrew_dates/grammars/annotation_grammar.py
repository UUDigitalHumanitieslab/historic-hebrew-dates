import re
from typing import Dict, List, Union

tokens = (
    'WORD',
    'LBRACE',
    'RBRACE',
    'LPAREN',
    'RPAREN'
)

t_LBRACE = r'\{'
t_RBRACE = r'\}'
t_LPAREN  = r'\('
t_RPAREN  = r'\)'
t_WORD = r'[\w \t\n\.\*]+'

t_ignore = "\r[]><,?/:'"

def t_error(t):
    raise Exception("Illegal character '%s'" % t.value[0])

# Build the lexer
import ply.lex as lex
lexer = lex.lex(reflags=re.UNICODE)

def p_expression(p):
    '''expression : words
                  | annotation
                  | words annotation'''
    p[0] = p[1:]

def p_expression_multiple(p):
    '''expression : words annotation expression
                  | annotation expression'''
    terms = len(p)
    p[0] = p[1:terms-1] + p[terms-1]

def p_annotation(p):
    'annotation : LBRACE expression RBRACE LPAREN WORD RPAREN'
    p[0] = {
        'tag': p[5],
        'expression': p[2]
    }

def p_words(p):
    '''words : WORD
             | WORD words'''
    if len(p) == 2:
        p[0] = { 'words': [p[1]] }
    else:
        p[0] = { 'words': [p[1]] + p[2]['words'] }

def p_error(p):
    raise Exception("Syntax error at '%s'" % p.value)

import ply.yacc as yacc
parser = yacc.yacc(tabmodule='annotation_parsetab', debugfile='annotation.out')

def word_to_pattern(word: str):
    word = re.sub(r'[ \t\n]+', ' ', word)
    return re.sub(r'[\*\.]+', '\\\\w*', word)

def expression_to_pattern(expression, tag_types: Dict[str, str]):
    for part in expression:
        if 'tag' in part:
            tag = part['tag']
            if tag in tag_types:
                yield f'{{{tag}:{tag_types[tag]}}}'
            else:
                yield f'{{{tag}}}'
        elif 'words' in part:
            yield from map(word_to_pattern, part['words'])

def get_patterns_from_parse(parse, tag_types: Dict[str, str]) -> List[Union[str, str, str, str]]:
    patterns = []

    for expression in parse:
        if 'tag' in expression:
            annotation_expression = expression['expression']
            tag = expression['tag']
            if tag in tag_types:
                tag_type = tag_types[tag]
            else:
                tag_type = tag
            patterns += [(
                tag,
                tag,
                tag_type,
                ''.join(expression_to_pattern(annotation_expression, tag_types)).strip())]

            # store the context to disambiguate year of age, and of dates
            context = tag
            patterns += list(map(
                lambda item: (context, item[1], item[2], item[3]),
                get_patterns_from_parse(annotation_expression, tag_types)))

    return patterns


def get_patterns(text: str, tag_types: Dict[str, str] = {}):
    """
    Gets all the pattern from annotated text.

    tag_types: Tag types which should be mapped to another type (e.g. year -> number)
    """

    parse = parser.parse(text, lexer=lexer)
    return get_patterns_from_parse(parse, tag_types)

if __name__ == "__main__":
    # interactive mode for testing from console
    while True:
        try:
            s = input('input > ')
            if not s:
                quit()
        except EOFError:
            break
        parse = parser.parse(s)
        print(parse)
        patterns = get_patterns(s)
        print(patterns)
