import re

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
t_WORD = r'\w+'

t_ignore = " \t\n\r.[]><"

def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)

# Build the lexer
import ply.lex as lex
lexer = lex.lex(reflags=re.UNICODE)

def p_expression(p):
    '''expression : words
                  | annotation
                  | words annotation
                  | words annotation expression
                  | annotation expression'''
    p[0] = p[1:]

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
    print("Syntax error at '%s'" % p.value)

import ply.yacc as yacc
parser = yacc.yacc()

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
