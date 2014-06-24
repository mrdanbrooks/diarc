# from PySide.QtCore import *
# from PySide.QtGui import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import sys



class MyBlock(QGraphicsWidget):
    def __init__(self,parent,block):
        super(MyBlock,self).__init__(parent=parent)
        self.parent = parent
        self.block = block
        self.block.visual = self
        self.setContentsMargins(5,5,5,5)
        self.rightSpacer = MyBlockSpacer(self)

    def link(self):
        l = self.parent.layout()

        # Link with your own right spacer
        l.addAnchor(self,Qt.AnchorRight,self.rightSpacer,Qt.AnchorLeft)
        l.addAnchor(self,Qt.AnchorVerticalCenter,self.rightSpacer,Qt.AnchorVerticalCenter)

        # Link with Block to right (when available)
        if self.block.rightBlock and self.block.rightBlock.visual:
            print "block",self.block.index,"linking right to",self.block.rightBlock.index
            l.addAnchor(self.rightSpacer,Qt.AnchorRight,self.block.rightBlock.visual,Qt.AnchorLeft)
            l.addAnchor(self.rightSpacer,Qt.AnchorVerticalCenter,self.block.rightBlock.visual,Qt.AnchorVerticalCenter)

        # Link with spacer of Block to left (when available)
        if self.block.leftBlock and self.block.leftBlock.visual:
            print "block",self.block.index,"linking left to",self.block.leftBlock.index
            l.addAnchor(self,Qt.AnchorLeft,self.block.leftBlock.visual.rightSpacer,Qt.AnchorRight)
            l.addAnchor(self,Qt.AnchorVerticalCenter,self.block.leftBlock.visual.rightSpacer,Qt.AnchorVerticalCenter)


    def paint(self,painter,option,widget):
        painter.setPen(Qt.red)
        painter.drawRect(self.rect())

class MyBlockSpacer(QGraphicsWidget):
    def __init__(self,parent):
        super(MyBlockSpacer,self).__init__(parent=parent)
        self.setSizePolicy(QSizePolicy(QSizePolicy.MinimumExpanding,QSizePolicy.Preferred))
        self.setPreferredWidth(15)
        self.setMinimumWidth(15)



class MySnap(QGraphicsWidget):
    def __init__(self,parent):
        super(MySnap,self).__init__(parent=parent)
        self.setSizePolicy(QSizePolicy(QSizePolicy.Preferred,QSizePolicy.Preferred))
        self.setPreferredWidth(20)
        self.setPreferredHeight(40)
        
    def paint(self,painter,option,widget):
        painter.setPen(Qt.green)
        painter.drawRect(self.rect())


class MyArc(QGraphicsWidget):
    def __init__(self,parent):
        super(MyArc,self).__init__(parent=parent)
 
    def paint(self,painter,option,widget):
        painter.setPen(Qt.red)
        painter.drawRect(self.rect())






class DrawingBoard(QGraphicsWidget):
    def __init__(self):
        super(DrawingBoard,self).__init__(parent=None)
        self.setAcceptedMouseButtons(Qt.LeftButton)
        self.resize(0,0)

#         a = MyBlock(self)
#         b = MyBlockSpacer(self)
#         c = MyBlock(self)
# 
#         d = MyArc(self)
#         c.setLayout(QGraphicsLinearLayout(Qt.Horizontal))
# 
# 
#         e1 = MySnap(self)
#         e2 = MySnap(self)
#         e3 = MySnap(self)
#         e4 = MySnap(self)
#         e5 = MySnap(self)
#         e6 = MySnap(self)
# 
# 
        l = QGraphicsAnchorLayout()
        l.setSpacing(0)

        self.setLayout(l)
#         # Vertical
#         l.addAnchor(a, Qt.AnchorTop, l, Qt.AnchorTop)
#         l.addAnchor(a, Qt.AnchorLeft,l,Qt.AnchorLeft)
#         l.addAnchor(a, Qt.AnchorTop,b,Qt.AnchorTop)
#         l.addAnchor(a, Qt.AnchorRight, b, Qt.AnchorLeft)
#         l.addAnchor(b, Qt.AnchorTop,c,Qt.AnchorTop)
#         l.addAnchor(b, Qt.AnchorRight,c,Qt.AnchorLeft)
# 
#         l.addAnchor(a, Qt.AnchorLeft, e1, Qt.AnchorLeft)
#         l.addAnchor(a, Qt.AnchorVerticalCenter, e1, Qt.AnchorVerticalCenter)
#         l.addAnchor(e1, Qt.AnchorRight, e2, Qt.AnchorLeft)
#         l.addAnchor(e2, Qt.AnchorRight, e3, Qt.AnchorLeft)
#         l.addAnchor(e3, Qt.AnchorRight, e4, Qt.AnchorLeft)
#         l.addAnchor(e4, Qt.AnchorRight, e5, Qt.AnchorLeft)
#         l.addAnchor(e5, Qt.AnchorRight, e6, Qt.AnchorLeft)
#         l.addAnchor(e6, Qt.AnchorRight, a, Qt.AnchorRight)
# 
# 
#         f1 = MySnap(c)
#         f2 = MySnap(c)
#         f3 = MySnap(c)
#         f4 = MySnap(c)
#         f5 = MySnap(c)
#  
#         l.addAnchor(e6,Qt.AnchorRight,d,Qt.AnchorLeft)
#         l.addAnchor(d,Qt.AnchorRight,f1,Qt.AnchorLeft)
# 
# 
#         c.layout().addItem(f1)
#         c.layout().addItem(f2)
#         c.layout().addItem(f3)
#         c.layout().addItem(f4)
#         c.layout().addItem(f5)

    def autoLayout(self,topology):

        lastBlock = None
        visualBlocks = list()
        for index,block in topology.blocks.items():
            print "adding block",index
            vertexBlock = MyBlock(self,block)
            visualBlocks.append(vertexBlock)
        self.layout().addAnchor(visualBlocks[0],Qt.AnchorTop,self.layout(),Qt.AnchorTop)
        self.layout().addAnchor(visualBlocks[0],Qt.AnchorLeft,self.layout(),Qt.AnchorLeft)
        for b in visualBlocks:
            b.link()
        self.layout().invalidate()
        
        

    def paint(self,painter,option,widget):
        painter.setPen(Qt.blue)
        painter.drawRect(self.rect())


class GraphView(QGraphicsView):
    def __init__(self):
        super(GraphView,self).__init__(parent=None)
        self.setScene(QGraphicsScene(self))
        # We might want to do this later to speed things up
        self.drawingBoard = DrawingBoard()

        self.scene().addItem(self.drawingBoard)
        # Basically, I'm not sure how to tell a widget where to go inside a scene.
        # But widgets placed inside widgets seem to be pretty reliable.

        # Set the size of the window
        self.resize(1024,768)

        # Show the window
        self.show()

    def autoLayout(self,topology):
        self.drawingBoard.autoLayout(topology)

    def mousePressEvent(self,event):
        pos = event.pos()
        print pos.x(),pos.y()
        super(GraphView,self).mousePressEvent(event)


