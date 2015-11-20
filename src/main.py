
tokens = (
    'SUB',
    'SUPER',
    'DIVIDE',
    'LPAREN',
    'RPAREN',
    'LLLAVE',
    'RLLAVE',
    'CARACTERES'
)
# Tokens

t_SUB   = r'_'
t_SUPER   = r'\^'
t_DIVIDE  = r'/'
t_LPAREN  = r'\('
t_RPAREN  = r'\)'
t_LLLAVE  = r'\{'
t_RLLAVE  = r'\}'
t_CARACTERES = r'[^_\^/\(\)\{\}]'



# Ignored characters
t_ignore = " \t"

def t_newline(t):
    r'\n+'
    t.lexer.lineno += t.value.count("\n")

def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)

# Build the lexer
import ply.lex as lex
lex.lex()




# TODO: VALIDAR LAS PRESEDENCIAS:
# Concat no tiene token como para definirlo
precedence = (
    ('left','SUB','SUPER'),
    ('left','DIVIDE'),
    )

# Precedence rules for the arithmetic operators
# precedence = (
#     ('left','PLUS','MINUS'),
#     ('left','TIMES','DIVIDE'),
#     ('right','UMINUS'),
#     )

# dictionary of names (for storing variables)
names = { }

# S -> E
def p_statement_expression(p):
    'statement : expression'
    print("p_statement_expression CALLED")
    print(p[1])

# E -> E / CONCAT
def p_expression_divide(p):
    'expression : expression DIVIDE concat'
    print("p_expression_divide CALLED")
    #p[0] = p[1] / p[3]

# E -> CONCAT
def p_expression_concat(p):
    'expression : concat'
    print("p_expression_concat CALLED")
    p[0] = p[1]

# CONCAT -> CONCAT ELEMENTS
def p_concat_concat(p):
    'concat : concat elements'
    print("p_concat_concat CALLED")

# CONCAT -> ELEMENTS
def p_concat_elements(p):
    'concat : elements'
    print("p_concat_elements CALLED")
    p[0] = p[1]

# ELEMENTS -> INDEXES
def p_elements_indexes(p):
    'elements : indexes'
    print("p_elements_indexes CALLED")
    p[0] = p[1]

# ELEMENTS -> NOINDEX
def p_elements_noindex(p):
    'elements : noindex'
    print("p_elements_noindex CALLED")
    p[0] = p[1]

# SUPER -> NOINDEX^NOINDEX
def p_super(p):
    'super : noindex SUPER noindex'
    print("p_super CALLED")

# SUB -> NOINDEX_NOINDEX
def p_sub(p):
    'sub : noindex SUB noindex'
    print("p_sub CALLED")

# SUPSUB -> NOINDEX^NOINDEX_NOINDEX
def p_superindex_subindex(p):
    'supsub : noindex SUPER noindex SUB noindex'
    print("p_superindex_subindex CALLED")

# SUBSUP -> NOINDEX_NOINDEX^NOINDEX
def p_subindex_superindex(p):
    'subsup : noindex SUB noindex SUPER noindex'
    print("p_subindex_superindex CALLED")

# INDEXES -> SUPER | SUB | SUPSUB | SUBSUP
def p_indexes(p):
    '''indexes : super
               | sub
               | supsub
               | subsup'''
    print("p_indexes CALLED")
    p[0] = p[1]

#NOINDEX -> PAR | GROUP | ID
def p_noindex(p):
    '''noindex : parenthesis
               | group
               | id'''
    print("noindex CALLED")
    p[0] = p[1]

# ID -> l
def p_id(p):
    'id : CARACTERES'
    print("CARACTER %s ENCONTRADO" % (p[1]))
    p[0] = p[1]

# PAR -> (E)
def p_parenthesis(p):
    'parenthesis : LPAREN expression RPAREN'
    print("parenthesis CALLED")

# GROUP -> {E}
def p_group(p):
    'group : LLLAVE expression RLLAVE'
    print("group CALLED")
    p[0] = p[2]

def p_error(p):
    print("Syntax error at '%s'" % p.value)
import ply.yacc as yacc
yacc.yacc()

while True:
    try:
        s = raw_input('calc > ')   # use input() on Python 3
    except EOFError:
        break
    yacc.parse(s)

"""
lexer = lex.lex()
while True:
    try:
        s = raw_input('calc > ')   # use input() on Python 3
    except EOFError:
        break
    lexer.input(s)
    for tok in lexer:
        print(tok)
"""
