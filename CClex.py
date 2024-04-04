
import ply.lex as lex
import ply.yacc as yacc


reserved_word = {
    'if': 'IF', 'then': 'THEN', 'else': 'ELSE',
    'for': 'FOR', 'do': 'DO', 'while': 'WHILE',
    'end': 'END', 'print': 'PRINT', 'function': 'FUNCTION',
    'contract': 'CONTRACT', 'public': 'PUBLIC', 'private': 'PRIVATE',
    'internal': 'INTERNAL', 'external': 'EXTERNAL', 'return': 'RETURN',
    'returns': 'RETURNS', 'emit': 'EMIT', 'event': 'EVENT',
    'int': 'INT','string': 'STRING', 'bool': 'BOOL',
    'address': 'ADDRESS', 'var': 'VAR'
}

type_specifiers = {'int', 'string', 'bool', 'address'}

tokens = [
             'EQUAL', 'ADD', 'SUBTRACT', 'MULTIPLY', 'DIVIDE',
             'LESSTHAN', 'GREATERTHAN', 'LESSTHANOREQUAL', 'GREATERTHANOREQUAL',
             'NOTEQUAL', 'EQUIVALENT', 'SEMICOLON', 'COMMA', 'OPENPAREN', 'CLOSEPAREN',
             'CURLYOPENINGPAREN', 'CURLYCLOSINGPAREN',
             'IDENTIFIER', 'VISIBILITY', 'ADDRESS_LITERAL', 'NUMBER',
             'STRING_LITERAL', 'TYPE_SPECIFIER'] + list(reserved_word.values())

t_ignore = '\t '
t_ignore_COMMENT = r'//.*|\#[^\n]*'
t_EQUAL = r'='
t_ADD = r'\+'
t_SUBTRACT = r'-'
t_MULTIPLY = r'\*'
t_DIVIDE = r'/'
t_LESSTHAN = r'<'
t_GREATERTHAN = r'>'
t_LESSTHANOREQUAL = r'<='
t_GREATERTHANOREQUAL = r'>='
t_NOTEQUAL = r'!='
t_EQUIVALENT = r'=='
t_SEMICOLON = r';'
t_COMMA = r','
t_OPENPAREN = r'\('
t_CLOSEPAREN = r'\)'
t_CURLYOPENINGPAREN = r'\{'
t_CURLYCLOSINGPAREN = r'\}'
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

def t_number(t):
    r'\d+'
    t.value = int(t.value)
    t.type = 'NUMBER'
    return t

def t_address(t):
    r'address'
    t.type = 'ADDRESS'
    return t

def t_address_literal(t):
    r'"0x[a-fA-F0-9]{40}"|"[a-fA-F0-9]{64}"'
    t.value = t.value[1:-1]  # Extract the actual address value
    t.type = 'ADDRESS_LITERAL'
    return t

def t_string_literal(t):
    r'"([^"\\]|\\.)*"'
    t.value = t.value[1:-1]
    t.type = 'STRING_LITERAL'
    return t

def t_bool(t):
    r'true|false'
    t.type = 'BOOL'
    return t

def t_visibility(t):
    r'private|public'
    t.type = 'VISIBILITY'
    return t


def t_error(t):
    print(f"********************************")
    print(f"ERROR: Invalid Character {t.value[0]} at line {t.lineno}")
    print(f"********************************")
    t.lexer.skip(1)

def t_id(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    if t.value in type_specifiers:
        t.type = 'TYPE_SPECIFIER'
    elif t.value in reserved_word:
        t.type = reserved_word[t.value]
    else:
        t.type = 'IDENTIFIER'
    return t


lexer = lex.lex()