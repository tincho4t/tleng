FONT_SIZE = 48
CHAR_WIDTH = .6 * FONT_SIZE
CHAR_HEIGHT = 1.0 * FONT_SIZE
CHAR_UPPER_HEIGHT = .8 * FONT_SIZE
CHAR_LOWER_HEIGHT = .2 * FONT_SIZE
PARENTHESIS_SPACING = .5 * FONT_SIZE
LINE_SPACING = .1 * FONT_SIZE
SUPER_SPACING = -0.5 * CHAR_UPPER_HEIGHT
SUB_SPACING = -0.5 * CHAR_UPPER_HEIGHT

class Node(object):
	def __init__(self, wid, hlw, hup):
		self.x = 0
		self.y = 0
		self.wid = wid
		self.hlw = hlw
		self.hup = hup
		self.scale = FONT_SIZE
		self.subNodes = []

	def getPosition(self):
		return (self.x, self.y)

	def getHeights(self):
		return (self.hlw, self.hup)

	def getLowerHeight(self):
		return self.hlw

	def getUpperHeight(self):
		return self.hup

	def getHeight(self):
		return self.hup + self.hlw

	def getWidth(self):
		return self.wid

	def getScale(self):
		return self.scale

	def setPosition(self, position):
		nx, ny = position
		dx = nx - self.x
		dy = ny - self.y
		self.movePosition(dx, dy)

	def scaleBy(self, scale):
		self.scale *= scale
		self.x *= scale
		self.y *= scale
		self.wid *= scale
		self.hup *= scale
		self.hlw *= scale
		for node in self.subNodes:
			node.scaleBy(scale)

	def movePosition(self, x, y):
		self.x += x
		self.y += y
		for node in self.subNodes:
			node.movePosition(x, y)

	def addNode(self, node):
		self.subNodes.append(node)

	def toSvg(self):
		return "".join([node.toSvg() for node in self.subNodes])

class MainNode(Node):
	def __init__(self, node):
		wid = node.getWidth()
		hlow, hupp = node.getHeights()
		super(MainNode, self).__init__(wid, hlow, hupp)
		self.addNode(node)

	def toSvg(self):
		return '''<?xml version="1.0" standalone="no"?>
<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN"
"http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">
<svg xmlns="http://www.w3.org/2000/svg" version="1.1">
<g transform="translate(10, %.2f) " font-family="Courier">\n''' % (10+ self.hup - self.y) + \
			super(MainNode, self).toSvg() + \
			'''</g></svg>'''

class CharacterNode(Node):
	def __init__(self, char):
		super(CharacterNode, self).__init__(CHAR_WIDTH, CHAR_LOWER_HEIGHT, CHAR_UPPER_HEIGHT)
		self.char = char

	def toSvg(self):
		x, y = self.getPosition()
		return "<text x='%.2f' y='%.2f' font-size='%.2f'>%s</text>\n" % (x, y, self.scale, self.char)

class ConcatNode(Node):
	def __init__(self, nodeA, nodeB):
		wid = nodeA.getWidth() + nodeB.getWidth()
		hlowA, huppA = nodeA.getHeights()
		hlowB, huppB = nodeB.getHeights()

		super(ConcatNode, self).__init__(wid, max(hlowA, hlowB), max(huppA, huppB))
		self.setPosition(nodeA.getPosition())	#Mueve el nodo
		self.addNode(nodeA)						#Agrega el 1er nodo
		self.addNode(nodeB)						#Agrega el 2do nodo

		nodeB.setPosition(nodeA.getPosition())	#Mueve el nodo y B a la pos. de A
		nodeB.movePosition(nodeA.getWidth(), 0)	#Desplaza B.x por A.width()

class ParenthesisNode(Node):
	def __init__(self, subNode):
		wid = subNode.getWidth() + PARENTHESIS_SPACING * 2
		hlow, hupp = subNode.getHeights()

		super(ParenthesisNode, self).__init__(wid, hlow, hupp)
		self.setPosition(subNode.getPosition())
		subNode.movePosition(PARENTHESIS_SPACING, 0)
		self.addNode(subNode)

	def toSvg(self):
		x, y = self.getPosition()
		scale = self.getScale()
		height = self.getHeight() / .74
		subNodeWidth = self.getWidth() - PARENTHESIS_SPACING

		y += self.getLowerHeight()
		y -= (0.12 * FONT_SIZE) * height / scale

		parStr = "<text x='0' y='0' font-size='%.2f' transform='translate(%.2f, %.2f) scale(1, %.2f)'>%s</text>\n"
		lPar = parStr % (scale, x, y, height / scale, '(')
		rPar = parStr % (scale, x + subNodeWidth, y, height / scale, ')')

		return lPar + super(ParenthesisNode, self).toSvg() + rPar

class SubIndexNode(Node):
	def __init__(self, rootNode, indexNode):
		indexNode.scaleBy(0.7)

		wid = rootNode.getWidth() + indexNode.getWidth()
		hlow, hupp = rootNode.getHeights()

		hlow += indexNode.getHeight() + SUB_SPACING
		super(SubIndexNode, self).__init__(wid, hlow, hupp)


		#Mueve el nodo Index a la derecha y un poco mas abajo que Root
		indexNode.movePosition(rootNode.getWidth(), indexNode.getUpperHeight() + rootNode.getLowerHeight() + SUB_SPACING)
		self.addNode(indexNode)								#Agrega el nodo Index
		self.setPosition(rootNode.getPosition())			#Setea el nodo en la posicion de Root
		self.addNode(rootNode)								#Agrega el nodo Root

class SuperIndexNode(Node):
	def __init__(self, rootNode, indexNode):
		indexNode.scaleBy(0.7)

		wid = rootNode.getWidth() + indexNode.getWidth()
		hlow, hupp = rootNode.getHeights()

		hupp += indexNode.getHeight() + SUPER_SPACING
		super(SuperIndexNode, self).__init__(wid, hlow, hupp)
		
		#Mueve el nodo Index a la derecha y un poco mas arriba que Root
		indexNode.movePosition(rootNode.getWidth(), -indexNode.getLowerHeight() - rootNode.getUpperHeight() - SUPER_SPACING)
		self.addNode(indexNode)								#Agrega el nodo Index
		self.setPosition(rootNode.getPosition())			#Setea el nodo en la posicion de Root
		self.addNode(rootNode)								#Agrega el nodo Root

class SuperSubIndexNode(Node):
	def __init__(self, rootNode, superNode, subNode):
		superNode.scaleBy(0.7)
		subNode.scaleBy(0.7)

		wid = rootNode.getWidth() + max(superNode.getWidth(), subNode.getWidth())
		hlow, hupp = rootNode.getHeights()
		hlow += subNode.getHeight() + SUB_SPACING
		hupp += superNode.getHeight() + SUPER_SPACING
		super(SuperSubIndexNode, self).__init__(wid, hlow, hupp)

		#Mueve el Sub a la derecha y abajo del Root
		subNode.movePosition(rootNode.getWidth(), subNode.getUpperHeight() + rootNode.getLowerHeight() + SUB_SPACING)
		
		#Mueve el Super a la derecha y arriba del Root
		superNode.movePosition(rootNode.getWidth(), -superNode.getLowerHeight() - rootNode.getUpperHeight() - SUPER_SPACING)

		self.addNode(subNode)								#Agrega el nodo Sub
		self.addNode(superNode)								#Agrega el nodo Super
		self.setPosition(rootNode.getPosition())			#Setea el nodo en la posicion de Root
		self.addNode(rootNode)	

class DivideNode(Node):
	def __init__(self, upperNode, lowerNode):
		uwid = upperNode.getWidth()
		lwid = lowerNode.getWidth()
		if uwid > lwid:
			wid = uwid
		else:
			wid = lwid
		hlow = lowerNode.getHeight() + CHAR_HEIGHT * 0.28
		hupp = upperNode.getHeight() + CHAR_HEIGHT * 0.4

		lineNode = LineNode(wid)


		super(DivideNode, self).__init__(wid, hlow, hupp)
		self.setPosition(upperNode.getPosition())				#Mueve el Nodo a la posicion de Upper
		self.addNode(upperNode)
		self.addNode(lineNode)
		self.addNode(lowerNode)

		lineNode.setPosition(upperNode.getPosition())				#Mueve la linea al Baseline
		lineNode.movePosition(0, -.28*CHAR_HEIGHT)					#Mueve la linea un poco arriba para que quede alineada con los '-''
		lowerNode.setPosition(upperNode.getPosition())				#Mueve Lower al Baseline
		lowerNode.movePosition(0, lowerNode.getUpperHeight())		#Mueve Lower por debajo de la linea
		upperNode.movePosition(0, -upperNode.getLowerHeight() -.4*CHAR_HEIGHT) #Mueve Upper por encima de la linea

		if uwid > lwid:
			lowerNode.movePosition((uwid - lwid) / 2, 0)
		else:
			upperNode.movePosition((lwid - uwid) / 2, 0)


class LineNode(Node):
	def __init__(self, wid):
		super(LineNode, self).__init__(wid, LINE_SPACING, LINE_SPACING)

	def toSvg(self):
		x, y = self.getPosition()
		wid = self.getWidth()
		lineStr = "<line x1='%.2f' y1='%.2f' x2='%.2f' y2='%.2f' stroke-width='%.3f' stroke='black' />\n"
		stroke = 0.03 * self.scale
		return (lineStr % (x, y, x + wid, y, stroke)) + super(LineNode, self).toSvg()




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
    p[0] = MainNode(p[1]).toSvg()

# E -> E / CONCAT
def p_expression_divide(p):
    'expression : expression DIVIDE concat'
    print("p_expression_divide CALLED")
    #p[0] = p[1] / p[3]
    p[0] = DivideNode(p[1], p[3])

# E -> CONCAT
def p_expression_concat(p):
    'expression : concat'
    print("p_expression_concat CALLED")
    p[0] = p[1]

# CONCAT -> CONCAT ELEMENTS
def p_concat_concat(p):
    'concat : concat elements'
    print("p_concat_concat CALLED")
    p[0] = ConcatNode(p[1], p[2])

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
    p[0] = SuperIndexNode(p[1], p[3])

# SUB -> NOINDEX_NOINDEX
def p_sub(p):
    'sub : noindex SUB noindex'
    print("p_sub CALLED")
    p[0] = SubIndexNode(p[1], p[3])

# SUPSUB -> NOINDEX^NOINDEX_NOINDEX
def p_superindex_subindex(p):
    'supsub : noindex SUPER noindex SUB noindex'
    print("p_superindex_subindex CALLED")
    p[0] = SuperSubIndexNode(p[1], p[3], p[5])

# SUBSUP -> NOINDEX_NOINDEX^NOINDEX
def p_subindex_superindex(p):
    'subsup : noindex SUB noindex SUPER noindex'
    print("p_subindex_superindex CALLED")
    p[0] = SuperSubIndexNode(p[1], p[5], p[3])

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
    p[0] = CharacterNode(p[1])

# PAR -> (E)
def p_parenthesis(p):
    'parenthesis : LPAREN expression RPAREN'
    print("parenthesis CALLED")
    p[0] = ParenthesisNode(p[2])

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
    	s = '{a^5-c/b}-c'
    	s = '{a^{5^6}-c_{{k^9}}/b_i}-c'
    	s = '(10+5/2)'
    	s = '1_2^{3_4^{5_6^7}}'
    	s = '(A^BC^D/E^F_G+H)-I'
    	s = 'A+(B){G^{(F^e_E/(2))}-(Q_{E_{{5}+E_{E_{E_D}}}}-Y)+X^K_J/Y}-{(80)/(2)}-{C^{G^{G^{G}}}/5}/({8+4+7}+5/ee)^{-i}'
        #s = raw_input('calc > ')   # use input() on Python 3
    except EOFError:
        break
    bald = yacc.parse(s)

    with open('out.svg', 'w') as f:
    	f.write(bald)

    print("====")
    print(bald)
    break

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
