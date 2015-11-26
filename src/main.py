import argparse

from Node import MainNode
from Node import DivideNode
from Node import ConcatNode
from Node import SuperIndexNode
from Node import SubIndexNode
from Node import SuperSubIndexNode
from Node import CharacterNode
from Node import ParenthesisNode

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



precedence = (
    ('left','SUB','SUPER'),
    ('left','DIVIDE'),
)


# S -> E
def p_statement_expression(p):
    'statement : expression'
    p[0] = MainNode(p[1]).toSvg()

# E -> E / CONCAT
def p_expression_divide(p):
    'expression : expression DIVIDE concat'
    p[0] = DivideNode(p[1], p[3])

# E -> CONCAT
def p_expression_concat(p):
    'expression : concat'
    p[0] = p[1]

# CONCAT -> CONCAT ELEMENTS
def p_concat_concat(p):
    'concat : concat elements'
    p[0] = ConcatNode(p[1], p[2])

# CONCAT -> ELEMENTS
def p_concat_elements(p):
    'concat : elements'
    p[0] = p[1]

# ELEMENTS -> INDEXES
def p_elements_indexes(p):
    'elements : indexes'
    p[0] = p[1]

# ELEMENTS -> NOINDEX
def p_elements_noindex(p):
    'elements : noindex'
    p[0] = p[1]

# SUPER -> NOINDEX^NOINDEX
def p_super(p):
    'super : noindex SUPER noindex'
    p[0] = SuperIndexNode(p[1], p[3])

# SUB -> NOINDEX_NOINDEX
def p_sub(p):
    'sub : noindex SUB noindex'
    p[0] = SubIndexNode(p[1], p[3])

# SUPSUB -> NOINDEX^NOINDEX_NOINDEX
def p_superindex_subindex(p):
    'supsub : noindex SUPER noindex SUB noindex'
    p[0] = SuperSubIndexNode(p[1], p[3], p[5])

# SUBSUP -> NOINDEX_NOINDEX^NOINDEX
def p_subindex_superindex(p):
    'subsup : noindex SUB noindex SUPER noindex'
    p[0] = SuperSubIndexNode(p[1], p[5], p[3])

# INDEXES -> SUPER | SUB | SUPSUB | SUBSUP
def p_indexes(p):
    '''indexes : super
               | sub
               | supsub
               | subsup'''
    p[0] = p[1]

#NOINDEX -> PAR | GROUP | ID
def p_noindex(p):
    '''noindex : parenthesis
               | group
               | id'''
    p[0] = p[1]

# ID -> l
def p_id(p):
    'id : CARACTERES'
    p[0] = CharacterNode(p[1])

# PAR -> (E)
def p_parenthesis(p):
    'parenthesis : LPAREN expression RPAREN'
    p[0] = ParenthesisNode(p[2])

# GROUP -> {E}
def p_group(p):
    'group : LLLAVE expression RLLAVE'
    p[0] = p[2]

def p_error(p):
    if(p):
        if(s): # Si esta seteada la variable global la uso para expresar mejor el error
            if(len(s) > p.lineno+1):
                error = "Error en el caracter '%s'. Contexto: '%s' '%s' '%s'" % (p.value, s[0:p.lineno], s[p.lineno], s[p.lineno+1:])
            else:
                error = "Error en el caracter '%s'. Contexto: '%s'" % (p.value, s[0:p.lineno])
        else:
            error = "Error en el caracter '%s' en la posicion %d." % (p.value, p.lineno)
    else: # en algunos casos p no viene definido y no hay mucha mas informacion para mostrar
        error = "Error de sintaxis."
    raise SyntaxError(error)

import ply.yacc as yacc
yacc.yacc()

def test():
    # Casos que tiene que tiene que reconocer
    assert test_accpet('(a_5-c/b-1)-c')
    assert test_accpet('{a^5-c/b}-c')
    assert test_accpet('{a^{5^6}-c_{{k^9}}/b_i}-c')
    assert test_accpet('(10+5/2)')
    assert test_accpet('1_2^{3_4^{5_6^7}}')
    assert test_accpet('(A^BC^D/E^F_G+H)-I')
    assert test_accpet('A+(B){G^{(F^e_E/(2))}-(Q_{E_{{5}+E_{E_{E_D}}}}-Y)+X^K_J/Y}-{(80)/(2)}-{C^{G^{G^{G}}}/5}/({8+4+7}+5/ee)^{-i}')
    
    assert test_not_accept('1^2^3')
    assert test_not_accept('1_2_3')
    assert test_not_accept('_')
    assert test_not_accept('_1')
    assert test_not_accept('^')
    assert test_not_accept('^1')
    assert test_not_accept('1_')
    assert test_not_accept('1/')
    assert test_not_accept('1/^')
    assert test_not_accept('{1+2')
    assert test_not_accept('1+2}')
    assert test_not_accept('(1+2')
    assert test_not_accept('3(1+2')
    assert test_not_accept('1+2)')
    assert test_not_accept('()')
    assert test_not_accept('())')
    assert test_not_accept('{{1}')
        
		
def test_not_accept(s):
    success = True
    try:
        s = yacc.parse(s)
        success = False # Si no falla paso por aca
    except SyntaxError:
        pass
    return success


# Si no pincha es porque se parseo correctamente
def test_accpet(s):
    yacc.parse(s)
    return True

s = None # Setea la variable global para poder mostrar mas informacion del error de parseo
test()

# Parseo de la entrada
parser = argparse.ArgumentParser(description='Conversor de formulas a SVG.')
parser.add_argument('--formula', type=str, help='Formula en formato pseudo latex')
parser.add_argument('--output', type=str, help='nombre del archivo donde se guardara el resultado')
args = parser.parse_args()

if(args.formula):
    s = args.formula
else:
    try:
        s = raw_input('Formula :> ')
    except EOFError:
        pass

try:
    bald = yacc.parse(s)
except SyntaxError as e:
    print(e) # Si hay un error de parseo lo muestro por pantalla y termino
    raise SystemExit

if(args.output):
    with open(args.output, 'w') as f:
    	f.write(bald)
else:
    print(bald)
