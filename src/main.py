CHAR_WIDTH = 0.6
CHAR_UPPER_HEIGHT = 1
CHAR_LOWER_HEIGHT = 0.2
PARENTHESIS_WIDTH = 0.1
PARENTHESIS_SPACING = 0.5
LINE_SPACING = 0.05

class Node(object):
	def __init__(self, wid, hlw, hup):
		self.x = 0
		self.y = 0
		self.wid = wid
		self.hup = hup
		self.hlw = hlw
		self.scale = 1
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
<g transform="translate(0, 50) scale(50)" font-family=
"Courier">''' + \
			super(MainNode, self).toSvg() + \
			'''</g></svg>'''

class CharacterNode(Node):
	def __init__(self, char):
		super(CharacterNode, self).__init__(CHAR_WIDTH, CHAR_UPPER_HEIGHT, CHAR_LOWER_HEIGHT)
		self.char = char

	def toSvg(self):
		x, y = self.getPosition()
		return "<text x='%.2f' y='%.2f' font-size='%.2f'>%s</text>\n" % (x, y, self.scale, self.char)

class ConcatNode(Node):
	def __init__(self, nodeA, nodeB):
		wid = nodeA.getWidth() + nodeB.getWidth()
		hlowA, huppA = nodeA.getHeights()
		hlowB, huppB = nodeB.getHeights()
		ax, ay = nodeA.getPosition()

		super(ConcatNode, self).__init__(wid, max(hlowA, hlowB), max(huppA, huppB))
		nodeB.movePosition(ax + nodeA.getWidth(), ay)
		self.addNode(nodeA)
		self.addNode(nodeB)

class ParenthesisNode(Node):
	def __init__(self, subNode):
		wid = subNode.getWidth() + PARENTHESIS_SPACING * 2
		hlow, hupp = subNode.getHeights()

		super(ParenthesisNode, self).__init__(wid, hlow, hupp)
		subNode.movePosition(PARENTHESIS_SPACING, 0)
		self.addNode(subNode)

	def toSvg(self):
		x, y = self.getPosition()
		scale = self.getScale()
		height = self.getHeight()
		subNodeWidth = self.getWidth() - PARENTHESIS_SPACING

		parStr = "<text x='%.2f' y='%.2f' font-size='%.2f' transform='translate(0, 0) scale(1, %.2f)'>%s</text>\n"
		lPar = parStr % (x, y, scale, height, '(')
		rPar = parStr % (x + subNodeWidth, y, scale, height, ')')
		return lPar + super(ParenthesisNode, self).toSvg() + rPar

class SubIndexNode(Node):
	def __init__(self, rootNode, indexNode):
		indexNode.scaleBy(0.7)

		rx, ry = rootNode.getPosition()
		wid = rootNode.getWidth() + indexNode.getWidth()
		hlow, hupp = rootNode.getHeights()
		hlow += indexNode.getHeight()

		super(SubIndexNode, self).__init__(wid, hlow, hupp)
		indexNode.movePosition(rx + rootNode.getWidth(), ry + indexNode.getUpperHeight())
		self.addNode(rootNode)
		self.addNode(indexNode)

class SuperIndexNode(Node):
	def __init__(self, rootNode, indexNode):
		indexNode.scaleBy(0.7)

		rx, ry = rootNode.getPosition()
		wid = rootNode.getWidth() + indexNode.getWidth()
		hlow, hupp = rootNode.getHeights()
		hupp += indexNode.getHeight()

		super(SuperIndexNode, self).__init__(wid, hlow, hupp)
		indexNode.movePosition(rx + rootNode.getWidth(), ry - indexNode.getLowerHeight())
		self.addNode(rootNode)
		self.addNode(indexNode)

class SuperSubIndexNode(Node):
	def __init__(self, rootNode, superNode, subNode):
		superNode.scaleBy(0.7)
		subNode.scaleBy(0.7)

		rx, ry = rootNode.getPosition()
		wid = rootNode.getWidth() + max(superNode.getWidth(), subNode.getWidth())
		hlow, hupp = rootNode.getHeights()
		hupp += superNode.getLowerHeight()
		hlow += subNode.getUpperHeight()

		super(SuperSubIndexNode, self).__init__(wid, hlow, hupp)
		superNode.movePosition(rx + rootNode.getWidth(), ry - superNode.getLowerHeight())
		subNode.movePosition(rx + rootNode.getWidth(), ry + subNode.getUpperHeight())
		self.addNode(rootNode)
		self.addNode(superNode)
		self.addNode(subNode)

class DivideNode(Node):
	def __init__(self, upperNode, lowerNode):
		uwid = upperNode.getWidth()
		lwid = lowerNode.getWidth()
		if uwid > lwid:
			lowerNode.movePosition((uwid - lwid) / 2, 0)
			wid = uwid
		else:
			upperNode.movePosition((lwid - uwid) / 2, 0)
			wid = lwid
		hlow = lowerNode.getHeight()
		hupp = upperNode.getHeight()

		lowerNode.movePosition(0, LINE_SPACING*2 + lowerNode.getLowerHeight())

		super(DivideNode, self).__init__(wid, hlow, hupp)
		self.addNode(upperNode)
		self.addNode(lowerNode)

		self.movePosition(0, upperNode.getUpperHeight())

	def toSvg(self):
		x, y = self.getPosition()
		wid = self.getWidth()
		lineStr = "<line x1='%.2f' y1='%.2f' x2='%.2f' y2='%.2f' stroke-width='0.03' stroke='black' />\n"
		return (lineStr % (x, y + LINE_SPACING, x + wid, y + LINE_SPACING)) + super(DivideNode, self).toSvg()




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
        s = raw_input('calc > ')   # use input() on Python 3
    except EOFError:
        break
    bald = yacc.parse(s)

    with open('out.svg', 'w') as f:
    	f.write(bald)

    print("====")
    print(bald)

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
