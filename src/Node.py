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
        self.setPosition(nodeA.getPosition())   #Mueve el nodo
        self.addNode(nodeA)                     #Agrega el 1er nodo
        self.addNode(nodeB)                     #Agrega el 2do nodo

        nodeB.setPosition(nodeA.getPosition())  #Mueve el nodo y B a la pos. de A
        nodeB.movePosition(nodeA.getWidth(), 0) #Desplaza B.x por A.width()

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
        snx, _ = self.subNodes[0].getPosition() #Me fijo la posicion del subnodo

        #subNodeWidth = self.getWidth() - PARENTHESIS_SPACING / scale
        #Y le resto la posicion del parentesis para saber el spacing a la izquierda
        #Sacandole al width total este spacing, queda la distancia al parentesis derecho
        subNodeWidth = self.getWidth() - (snx - x)

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
        self.addNode(indexNode)                             #Agrega el nodo Index
        self.setPosition(rootNode.getPosition())            #Setea el nodo en la posicion de Root
        self.addNode(rootNode)                              #Agrega el nodo Root

class SuperIndexNode(Node):
    def __init__(self, rootNode, indexNode):
        indexNode.scaleBy(0.7)

        wid = rootNode.getWidth() + indexNode.getWidth()
        hlow, hupp = rootNode.getHeights()

        hupp += indexNode.getHeight() + SUPER_SPACING
        super(SuperIndexNode, self).__init__(wid, hlow, hupp)
        
        #Mueve el nodo Index a la derecha y un poco mas arriba que Root
        indexNode.movePosition(rootNode.getWidth(), -indexNode.getLowerHeight() - rootNode.getUpperHeight() - SUPER_SPACING)
        self.addNode(indexNode)                             #Agrega el nodo Index
        self.setPosition(rootNode.getPosition())            #Setea el nodo en la posicion de Root
        self.addNode(rootNode)                              #Agrega el nodo Root

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

        self.addNode(subNode)                               #Agrega el nodo Sub
        self.addNode(superNode)                             #Agrega el nodo Super
        self.setPosition(rootNode.getPosition())            #Setea el nodo en la posicion de Root
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
        self.setPosition(upperNode.getPosition())               #Mueve el Nodo a la posicion de Upper
        self.addNode(upperNode)
        self.addNode(lineNode)
        self.addNode(lowerNode)

        lineNode.setPosition(upperNode.getPosition())               #Mueve la linea al Baseline
        lineNode.movePosition(0, -.28*CHAR_HEIGHT)                  #Mueve la linea un poco arriba para que quede alineada con los '-''
        lowerNode.setPosition(upperNode.getPosition())              #Mueve Lower al Baseline
        lowerNode.movePosition(0, lowerNode.getUpperHeight())       #Mueve Lower por debajo de la linea
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

