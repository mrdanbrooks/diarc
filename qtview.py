# from PySide.QtCore import *
# from PySide.QtGui import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import sys



class MyBlock(QGraphicsWidget):
    """ Visual Block, with right hand spacer """
    def __init__(self,parent,block):
        super(MyBlock,self).__init__(parent=parent)
        self.parent = parent
        self.block = block
        self.block.visual = self
        self.setContentsMargins(5,5,5,5)
        self.rightSpacer = MyBlockSpacer(self)

        l = self.parent.layout()
        # Set up top and bottom margin
        self._topMargin = MyBlockHorizontalSpacer(self)
        self._botMargin = MyBlockHorizontalSpacer(self)
        l.addAnchor(self,Qt.AnchorTop, self._topMargin, Qt.AnchorTop)
        l.addAnchor(self,Qt.AnchorLeft, self._topMargin, Qt.AnchorLeft)
        l.addAnchor(self,Qt.AnchorRight, self._topMargin, Qt.AnchorRight)
        l.addAnchor(self,Qt.AnchorBottom, self._botMargin, Qt.AnchorBottom)
        l.addAnchor(self,Qt.AnchorLeft, self._botMargin, Qt.AnchorLeft)
        l.addAnchor(self,Qt.AnchorRight, self._botMargin, Qt.AnchorRight)


        # Set up Emitter and Collector Containers
        self.myEmitter = MyEmitter(self)
        self.myCollector = MyCollector(self)
        l.addAnchor(self._topMargin, Qt.AnchorBottom, self.myEmitter, Qt.AnchorTop)
        l.addAnchor(self._botMargin, Qt.AnchorTop, self.myEmitter, Qt.AnchorBottom)
        l.addAnchor(self._topMargin, Qt.AnchorBottom, self.myCollector, Qt.AnchorTop)
        l.addAnchor(self._botMargin, Qt.AnchorTop, self.myCollector, Qt.AnchorBottom)
        l.addAnchor(self, Qt.AnchorLeft, self.myCollector, Qt.AnchorLeft)
        l.addAnchor(self, Qt.AnchorRight, self.myEmitter, Qt.AnchorRight)
        l.addAnchor(self.myCollector, Qt.AnchorRight, self.myEmitter, Qt.AnchorLeft)

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

class MyBlockHorizontalSpacer(QGraphicsWidget):
    def __init__(self,parent):
        super(MyBlockHorizontalSpacer,self).__init__(parent=parent)
        self.setSizePolicy(QSizePolicy(QSizePolicy.MinimumExpanding,QSizePolicy.MinimumExpanding))
        self.setPreferredHeight(15)
        self.setMinimumHeight(15)

#     def paint(self,painter,option,widget):
#         painter.setPen(Qt.blue)
#         painter.drawRect(self.rect())

class MyBlockSpacer(QGraphicsWidget):
    """ Spacer between blocks, associated with the block to its left """
    def __init__(self,parent):
        super(MyBlockSpacer,self).__init__(parent=parent)
        self.setSizePolicy(QSizePolicy(QSizePolicy.MinimumExpanding,QSizePolicy.Preferred))
        self.setPreferredWidth(15)
        self.setMinimumWidth(15)

    def paint(self,painter,option,widget):
        painter.setPen(Qt.NoPen)
        painter.drawRect(self.rect())


class MyContainer(QGraphicsWidget):
    """ Emitter or Collector """
    def __init__(self,parent):
        super(MyContainer,self).__init__(parent=parent)
        self.parent = parent
        self.setSizePolicy(QSizePolicy(QSizePolicy.MinimumExpanding,QSizePolicy.Preferred))
#         self.setPreferredWidth(15)
        self.setMinimumWidth(15)

    def paint(self,painter,option,widget):
        painter.setPen(Qt.green)
        painter.drawRect(self.rect())

class MyEmitter(MyContainer):
     def paint(self,painter,option,widget):
        painter.setPen(Qt.blue)
        painter.drawRect(self.rect())
   
class MyCollector(MyContainer):
     def paint(self,painter,option,widget):
        painter.setPen(Qt.green)
        painter.drawRect(self.rect())
   




class MySnap(QGraphicsWidget):
    def __init__(self,parent,snap):
        super(MySnap,self).__init__(parent=parent)
        print type(parent)
        self.parent = parent
        # The parent here should be a MyContainer
        self.setSizePolicy(QSizePolicy(QSizePolicy.Preferred,QSizePolicy.Preferred))
        self.setPreferredWidth(20)
        self.setPreferredHeight(40)
        # Link with the snap
        self.snap = snap
        self.snap.visual = self

        self.rightSpacer = MySnap.Spacer(self)

    def link(self):
        l = self.parent.layout()

        # Link with your own right spacer
        l.addAnchor(self, Qt.AnchorRight, self.rightSpacer, Qt.AnchorLeft)
        l.addAnchor(self, Qt.AnchorVerticalCenter, self.rightSpacer, Qt.AnchorVerticalCenter)

        # Link with snap to right (when available)
        if self.snap.rightSnap and self.snap.rightSnap.visual:
            print "Connecting snap",self.snap.order,
            print "to right snap ",self.snap.rightSnap.order,
            print "in block",self.snap.block.index,
            print "emitter" if self.snap.isSource() else "collector"

            l.addAnchor(self.rightSpacer, Qt.AnchorRight, self.snap.rightSnap.visual, Qt.AnchorLeft)
            l.addAnchor(self.rightSpacer, Qt.AnchorVerticalCenter, self.snap.rightSnap.visual, Qt.AnchorVerticalCenter)
            # This will bind to top and bottom
#             l.addAnchor(self.rightSpacer, Qt.AnchorTop, self.snap.rightSnap.visual, Qt.AnchorTop)
#             l.addAnchor(self.rightSpacer, Qt.AnchorBottom, self.snap.rightSnap.visual, Qt.AnchorBottom)

        # If you are the rightmost snap, link with parent container
        else:
            print "Adding rightmost snap order",self.snap.order,"to block",self.snap.block.index,"emitter" if self.snap.isSource() else "collector"
            container = self.snap.block.visual.myEmitter if self.snap.isSource() else self.snap.block.visual.myCollector
#             l.addAnchor(self.rightSpacer, Qt.AnchorTop, container, Qt.AnchorTop)
            l.addAnchor(self.rightSpacer, Qt.AnchorVerticalCenter, container, Qt.AnchorVerticalCenter)
#             l.addAnchor(self.rightSpacer, Qt.AnchorBottom, container, Qt.AnchorBottom)
            l.addAnchor(self.rightSpacer, Qt.AnchorRight, container, Qt.AnchorRight)

        # Link with spacer of Snap to left (when available)
        if self.snap.leftSnap and self.snap.leftSnap.visual:
            print "Connecting snap",self.snap.order,
            print "to left snap",self.snap.leftSnap.order,
            print "in block",self.snap.block.index,
            print "emitter" if self.snap.isSource() else "collector"
            l.addAnchor(self, Qt.AnchorLeft, self.snap.leftSnap.visual.rightSpacer, Qt.AnchorRight)
            l.addAnchor(self, Qt.AnchorVerticalCenter, self.snap.leftSnap.visual.rightSpacer, Qt.AnchorVerticalCenter)
            # This will bind to top and bottom
#             l.addAnchor(self, Qt.AnchorTop, self.snap.leftSnap.visual.rightSpacer, Qt.AnchorTop)
#             l.addAnchor(self, Qt.AnchorBottom, self.snap.leftSnap.visual.rightSpacer, Qt.AnchorBottom)

        # If you are the leftmost snap, link with parent container
        else:
            print "Adding leftmost snap order",self.snap.order,"to block",self.snap.block.index,"emitter" if self.snap.isSource() else "collector"
            container = self.snap.block.visual.myEmitter if self.snap.isSource() else self.snap.block.visual.myCollector
#             l.addAnchor(self, Qt.AnchorTop, container, Qt.AnchorTop)
#             l.addAnchor(self, Qt.AnchorBottom, container, Qt.AnchorBottom)
            l.addAnchor(self, Qt.AnchorLeft, container, Qt.AnchorLeft)
            l.addAnchor(self, Qt.AnchorVerticalCenter, container, Qt.AnchorVerticalCenter)



    def paint(self,painter,option,widget):
        painter.setPen(Qt.red)
        painter.drawRect(self.rect())


    class Spacer(QGraphicsWidget):
        """ Snap Spacer """
        def __init__(self,parent):
            super(MySnap.Spacer,self).__init__(parent=parent)
            self.setSizePolicy(QSizePolicy(QSizePolicy.MinimumExpanding,QSizePolicy.Preferred))
            self.setPreferredWidth(15)
            self.setMinimumWidth(15)

        def paint(self,painter,option,widget):
            painter.setPen(Qt.NoPen)
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
        l = QGraphicsAnchorLayout()
        l.setSpacing(0)
        self.setLayout(l)

    def autoLayout(self,topology):

        lastBlock = None
        visualBlocks = list()
        visualSnaps = list()
        for index,block in topology.blocks.items():
            print "adding block",index
            vertexBlock = MyBlock(self,block)
            visualBlocks.append(vertexBlock)
            for snap in block.emitter.values()+block.collector.values():
                mySnap = MySnap(self,snap)
                visualSnaps.append(mySnap)

        # Anchor the first block against the layout
        self.layout().addAnchor(visualBlocks[0],Qt.AnchorTop,self.layout(),Qt.AnchorTop)
        self.layout().addAnchor(visualBlocks[0],Qt.AnchorLeft,self.layout(),Qt.AnchorLeft)

        

        # Start anchoring the other blocks
        for b in visualBlocks:
            b.link()
        for s in visualSnaps:
            s.link()
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


