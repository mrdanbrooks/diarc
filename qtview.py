# from PySide.QtCore import *
# from PySide.QtGui import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from util import *
from topology import *
from SpacerContainer import *
import types
import json
import sys


class BandStack(SpacerContainer):
    def __init__(self,parent):
        super(BandStack,self).__init__(parent)
        self.setSizePolicy(QSizePolicy(QSizePolicy.MinimumExpanding,QSizePolicy.Preferred))
        self.setMinimumWidth(15)
        self.spacerType = BandSpacer

class BandSpacer(SpacerContainer.Spacer):
    def __init__(self,parent):
        super(BandSpacer,self).__init__(parent)
        self.setSizePolicy(QSizePolicy(QSizePolicy.Preferred,QSizePolicy.MinimumExpanding))
        self.setPreferredHeight(15)
        self.setMinimumHeight(15)
        self.setAcceptDrops(True)

    @property
    def topBand(self):
        return self.itemA

    @property
    def bottomBand(self):
        return self.itemB

    def link(self):
        l = self.layout()
        print "Working on Spacer between bands",self.topBand.band.altitude if self.topBand else None, "and",self.bottomBand.band.altitude if self.bottomBand else None
        sys.stdout.flush()
        # Link To your Top! If you have a band above, connect
        if self.topBand:
            print "Linking to bottom of ",self.topBand.band.altitude
            sys.stdout.flush()
            l.addAnchor(self, Qt.AnchorTop, self.topBand, Qt.AnchorBottom)
        # Otherwise, if it is a positive band, connect to the top of the BandStack
        elif self.bottomBand.band.isPositive:
            print "linking band",self.bottomBand.band.altitude,"to top of band stack"
            sys.stdout.flush()
            l.addAnchor(self, Qt.AnchorTop, self.parent, Qt.AnchorTop)
        # Otherwise, if it is a negative band, connect to Block Ribbon
        elif not self.bottomBand.band.isPositive: 
            print "linking band",self.bottomBand.band.altitude,"to bottom of ribbon"
            sys.stdout.flush()
            l.addAnchor(self, Qt.AnchorTop, self.parent.parent.blockRibbon, Qt.AnchorBottom)

        # Link to your bottom! If you have a band below, connect
        if self.bottomBand:
            print "Linking to top of ",self.bottomBand.band.altitude
            sys.stdout.flush()
            l.addAnchor(self, Qt.AnchorBottom, self.bottomBand, Qt.AnchorTop)
        # Otherwise, if it is a positive band, connect to the block ribbon
        elif self.topBand.band.isPositive:
            print "linking band",self.topBand.band.altitude,"to top of ribbon"
            sys.stdout.flush()
            l.addAnchor(self, Qt.AnchorBottom, self.parent.parent.blockRibbon, Qt.AnchorTop)
        elif not self.topBand.band.isPositive:
            print "linking band",self.topBand.band.altitude,"to bottom of band stack"
            sys.stdout.flush()
            l.addAnchor(self, Qt.AnchorBottom, self.parent, Qt.AnchorBottom)
        
        # Connect sides
        l.addAnchor(self, Qt.AnchorLeft, self.parent, Qt.AnchorLeft)
        l.addAnchor(self, Qt.AnchorRight, self.parent, Qt.AnchorRight)

    def mousePressEvent(self,event):
        print "Band Spacer: Above=",self.topBand.band.altitude if self.topBand else None,
        print "Below=",self.bottomBand.band.altitude if self.bottomBand else None 

    def paint(self,painter,option,widget):
#             painter.setPen(Qt.NoPen)
        pen = QPen()
        pen.setBrush(Qt.lightGray)
        pen.setStyle(Qt.DotLine)
        painter.setPen(pen)
        painter.drawRect(self.rect())

class BandItem(SpacerContainer.Item):
    def __init__(self,parent,band):
        typecheck(parent,DrawingBoard,"parent")
        super(BandItem,self).__init__(parent,parent.bandStack)
        self.band = band
        self.band.visual = self
        self.setContentsMargins(5,5,5,5)
        self.setSizePolicy(QSizePolicy(QSizePolicy.Preferred,QSizePolicy.MinimumExpanding))
        self.setPreferredHeight(15)
        self.setMinimumHeight(15)

    def itemA(self):
        """ Set itemA to be the topBand """
        return self.band.topBand.visual if self.band.topBand else None

    def itemB(self):
        """ Set itemB to be the bottomBand """
        return self.band.bottomBand.visual if self.band.bottomBand else None

    def isUsed(self):
        return self.band.isUsed()

    def link(self):
        print "*** linking band",self.band.altitude,"***"
        sys.stdout.flush()
        super(BandItem,self).link()

        l = self.parent.layout()
        l.addAnchor(self, Qt.AnchorHorizontalCenter, self.parent.blockRibbon, Qt.AnchorHorizontalCenter)

    def mousePressEvent(self,event):
        pos = event.pos()
        print "Band:",self.band.altitude
        sys.stdout.flush()
        self.setCursor(Qt.ClosedHandCursor)

    def paint(self,painter,option,widget):
        if self.band.isUsed():
            painter.setPen(Qt.red)
        else:
            painter.setPen(Qt.blue)
        painter.drawRect(self.rect())
        rect = self.geometry()
        painter.drawText(0,rect.height(),str(self.band.altitude))



class BlockRibbon(SpacerContainer):
    def __init__(self,parent):
        super(BlockRibbon,self).__init__(parent)
        self.spacerType = BlockSpacer
        self.parent = typecheck(parent,DrawingBoard,"parent")
        self.setSizePolicy(QSizePolicy(QSizePolicy.MinimumExpanding,QSizePolicy.Preferred))
        self.setMinimumWidth(15)

    def paint(self,painter,option,widget):
        painter.setPen(Qt.green)
        painter.drawRect(self.rect())

class BlockSpacer(SpacerContainer.Spacer):
    def __init__(self,parent):
        super(BlockSpacer,self).__init__(parent)
        self.setSizePolicy(QSizePolicy(QSizePolicy.MinimumExpanding,QSizePolicy.Preferred))
        self.setPreferredWidth(15)
        self.setMinimumWidth(15)
        self.setAcceptDrops(True)

    @property
    def leftBlock(self):
        return self.itemA

    @property
    def rightBlock(self):
        return self.itemB

    def link(self):
        l = self.parent.parent.layout()
        # If you have a block to your left, connect
        if self.leftBlock:
            l.addAnchor(self, Qt.AnchorLeft, self.leftBlock, Qt.AnchorRight)
            l.addAnchor(self, Qt.AnchorTop, self.leftBlock, Qt.AnchorTop)
            l.addAnchor(self, Qt.AnchorBottom, self.leftBlock, Qt.AnchorBottom)
        # Otherwise connect to left container edge
        else:
            l.addAnchor(self, Qt.AnchorLeft, self.parent, Qt.AnchorLeft)
            l.addAnchor(self, Qt.AnchorTop, self.parent, Qt.AnchorTop)
            l.addAnchor(self, Qt.AnchorBottom, self.parent, Qt.AnchorBottom)

        # If you have a block to your right, connect
        if self.rightBlock:
            l.addAnchor(self, Qt.AnchorRight, self.rightBlock, Qt.AnchorLeft)
            l.addAnchor(self, Qt.AnchorTop, self.rightBlock, Qt.AnchorTop)
            l.addAnchor(self, Qt.AnchorBottom, self.rightBlock, Qt.AnchorBottom)
        # Otherwise connect to the right container edge
        else:
            l.addAnchor(self, Qt.AnchorRight, self.parent, Qt.AnchorRight)
            l.addAnchor(self, Qt.AnchorTop, self.parent, Qt.AnchorTop)
            l.addAnchor(self, Qt.AnchorBottom, self.parent, Qt.AnchorBottom)

    def dragEnterEvent(self,event):
        if not event.mimeData().hasText():
            event.setAccepted(False)
            return
        data = json.loads(str(event.mimeData().text()))
        if 'block' in data:
            event.setAccepted(True)
            self.dragOver = True
            print "Drag ENTER"
        else:
            event.setAccepted(False)

    def dragLeaveEvent(self,event):
        self.dragOver = False

    def dropEvent(self,event):
        self.dragOver = False
        # Dragged Index
        data = json.loads(str(event.mimeData().text()))
        if not 'block' in data:
            raise Exception("Wrong drag data type!")
        srcIdx = data['block']
        # Left Index
        lowerIdx = self.leftBlock.block.index if self.leftBlock else None
        upperIdx = self.rightBlock.block.index if self.rightBlock else None
        blocks = self.parent.parent.topology.blocks

        lastIdx = None
        currIdx = srcIdx
        # If we are moving to the right, lowerIdx is the target index.
        # Clear the dragged block's index, then shift all effected block
        # indices left.
        # NOTE: See issue #12
        if lowerIdx > srcIdx:
            while isinstance(currIdx,int) and currIdx < (upperIdx or lowerIdx+1): # In case upperIdx is None, use lower+1
                nextIdx = blocks[currIdx].rightBlock.index if blocks[currIdx].rightBlock else None
                blocks[currIdx].index = lastIdx
                print "%s -> %s"%(str(currIdx),str(lastIdx))
                lastIdx = currIdx
                currIdx = nextIdx
            assert lastIdx == lowerIdx, "%r %r"%(lastIdx,upperIdx)

        # If we are moving to the left, upperIdx is the target index.
        # Clear the dragged blocks index, then shift all effected blocks right
        elif upperIdx < srcIdx:
            while isinstance(currIdx,int) and currIdx > lowerIdx:
                nextIdx = blocks[currIdx].leftBlock.index if blocks[currIdx].leftBlock else None
                blocks[currIdx].index = lastIdx
                print "%s -> %s"%(str(currIdx),str(lastIdx))
                lastIdx = currIdx
                currIdx = nextIdx
            assert lastIdx == upperIdx, "%r %r"%(lastIdx,upperIdx)

        # Otherwise we are just dragging to the side a bit and nothing is 
        # really moving anywhere. Return immediately to avoid trying to give
        # the block a new index and unnecessary extra linking actions.
        else:
            print "No op!"
            return
        # Finally give the moved object its desired destination. Then make 
        # the DrawingBoard relink all the objects again.
        blocks[srcIdx].index = lastIdx
        self.parent.parent.link()

    def paint(self,painter,option,widget):
        painter.setPen(Qt.NoPen)
        painter.drawRect(self.rect())


class BlockItem(SpacerContainer.Item):
    """ This is a QGraphicsWidget for a Diarc Block. """
    def __init__(self,parent,block):
        typecheck(parent,DrawingBoard,"parent")
        super(BlockItem,self).__init__(parent,parent.blockRibbon)
        self.block = block
        self.block.visual = self
        self.setContentsMargins(5,5,5,5)

        # We want to have a little space above and below the Emitter/Collector,
        # Set up top and bottom margin to give that space. 
        self._topMargin = BlockItem.HorizontalSpacer(self)
        self._botMargin = BlockItem.HorizontalSpacer(self)
        # TODO: Set up left and right margins as well

        # Set up Emitter and Collector Containers. They will sit "inside" the 
        # block margins
        self.myEmitter = MyEmitter(self)
        self.myCollector = MyCollector(self)

    def itemA(self):
        """ We use itemA for the BlockItem to the left. """
        return self.block.leftBlock.visual if self.block.leftBlock else None

    def itemB(self):
        """ We use itemB for the BlockItem to the right. """
        return self.block.rightBlock.visual if self.block.rightBlock else None

    def isUsed(self):
        """ Right now, BlockItem cannot 'disappear' """
        return True

    def link(self):
        """ Link to other objects around you. In addition to linking to other 
        blocks, we need to link to our top and bottom margins, and the emitter
        and collector containers 
        """
        # Link with other BlockItems
        super(BlockItem,self).link()
        
        l = self.parent.layout()
        # Link with top and bottom margins
        l.addAnchor(self,Qt.AnchorTop, self._topMargin, Qt.AnchorTop)
        l.addAnchor(self,Qt.AnchorLeft, self._topMargin, Qt.AnchorLeft)
        l.addAnchor(self,Qt.AnchorRight, self._topMargin, Qt.AnchorRight)
        l.addAnchor(self,Qt.AnchorBottom, self._botMargin, Qt.AnchorBottom)
        l.addAnchor(self,Qt.AnchorLeft, self._botMargin, Qt.AnchorLeft)
        l.addAnchor(self,Qt.AnchorRight, self._botMargin, Qt.AnchorRight)

        # Link with emitter and collector containers
        l.addAnchor(self._topMargin, Qt.AnchorBottom, self.myEmitter, Qt.AnchorTop)
        l.addAnchor(self._botMargin, Qt.AnchorTop, self.myEmitter, Qt.AnchorBottom)
        l.addAnchor(self._topMargin, Qt.AnchorBottom, self.myCollector, Qt.AnchorTop)
        l.addAnchor(self._botMargin, Qt.AnchorTop, self.myCollector, Qt.AnchorBottom)
        l.addAnchor(self, Qt.AnchorLeft, self.myCollector, Qt.AnchorLeft)
        l.addAnchor(self, Qt.AnchorRight, self.myEmitter, Qt.AnchorRight)
        l.addAnchor(self.myCollector, Qt.AnchorRight, self.myEmitter, Qt.AnchorLeft)

    def mousePressEvent(self,event):
        pos = event.pos()
        print "Block:",self.block.index
        self.setCursor(Qt.ClosedHandCursor)

    def mouseMoveEvent(self, event):
        drag = QDrag(event.widget())
        mimeData = QMimeData()
        mimeData.setText(json.dumps({'block':self.block.index}))
        drag.setMimeData(mimeData)
        drag.start()

    def mouseReleaseEvent(self,event):
        print "hi",
        self.setCursor(Qt.ArrowCursor)

    def paint(self,painter,option,widget):
        painter.setPen(Qt.red)
        painter.drawRect(self.rect())


    class HorizontalSpacer(QGraphicsWidget):
        def __init__(self,parent):
            super(BlockItem.HorizontalSpacer,self).__init__(parent=parent)
            self.setSizePolicy(QSizePolicy(QSizePolicy.MinimumExpanding,QSizePolicy.MinimumExpanding))
            self.setPreferredHeight(5)
            self.setMinimumHeight(5)


class SnapContainer(SpacerContainer):
    def __init__(self,parent):
        super(SnapContainer,self).__init__(parent.parent)
        self.parentBlock = typecheck(parent,BlockItem,"parent")

        self.spacerType = SnapSpacer
        self.setSizePolicy(QSizePolicy(QSizePolicy.MinimumExpanding,QSizePolicy.Preferred))
        self.setMinimumWidth(15)

    def strType(self):
        """ prints the container type as a string """
        return "emitter" if isinstance(self,MyEmitter) else "collector" if isinstance(self,MyCollector) else "unknown"

    def paint(self,painter,option,widget):
        painter.setPen(Qt.green)
        painter.drawRect(self.rect())

    def mousePressEvent(self,event):
        pos = event.pos()
        print "Emitter" if isinstance(self,MyEmitter) else "Collector" if isinstance(self,MyCollector) else "Container"
        super(SnapContainer,self).mousePressEvent(event)

    def mouseReleaseEvent(self,event):
        print "hi"
        self.setCursor(Qt.ArrowCursor)
        super(SnapContainer,self).mouseReleaseEvent(event)


class SnapSpacer(SpacerContainer.Spacer):
    def __init__(self,parent):
        super(SnapSpacer,self).__init__(parent)
        self.setSizePolicy(QSizePolicy(QSizePolicy.MinimumExpanding,QSizePolicy.Preferred))
        self.setPreferredWidth(15)
        self.setMinimumWidth(15)
        self.setAcceptDrops(True)

    @property
    def leftSnap(self):
        return self.itemA

    @property
    def rightSnap(self):
        return self.itemB

    def link(self):
        l = self.parent.parent.layout()

        # If you have a snap to your left, connect
        target = None
        if self.leftSnap:
            l.addAnchor(self, Qt.AnchorLeft, self.leftSnap, Qt.AnchorRight)
            l.addAnchor(self, Qt.AnchorVerticalCenter, self.leftSnap, Qt.AnchorVerticalCenter)
#                 l.addAnchor(self, Qt.AnchorTop, self.leftSnap, Qt.AnchorTop)
#                 l.addAnchor(self, Qt.AnchorBottom, self.leftSnap, Qt.AnchorBottom)

        # Otherwise connect to left container edge
        else:
            l.addAnchor(self, Qt.AnchorLeft, self.parent, Qt.AnchorLeft)
            l.addAnchor(self, Qt.AnchorVerticalCenter, self.parent, Qt.AnchorVerticalCenter)
#                 l.addAnchor(self, Qt.AnchorTop, self.parent, Qt.AnchorTop)
#                 l.addAnchor(self, Qt.AnchorBottom, self.parent, Qt.AnchorBottom)

        # if you have a snap to your right, connect
        if self.rightSnap:
            l.addAnchor(self, Qt.AnchorRight, self.rightSnap, Qt.AnchorLeft)
            l.addAnchor(self, Qt.AnchorVerticalCenter, self.rightSnap, Qt.AnchorVerticalCenter)
#                 l.addAnchor(self, Qt.AnchorTop, self.rightSnap, Qt.AnchorTop)
#                 l.addAnchor(self, Qt.AnchorBottom, self.rightSnap, Qt.AnchorBottom)

        # Otherwise connect to the right container edge
        else:
            l.addAnchor(self, Qt.AnchorRight, self.parent, Qt.AnchorRight)
            l.addAnchor(self, Qt.AnchorVerticalCenter, self.parent, Qt.AnchorVerticalCenter)
#                 l.addAnchor(self, Qt.AnchorTop, self.parent, Qt.AnchorTop)
#                 l.addAnchor(self, Qt.AnchorBottom, self.parent, Qt.AnchorBottom)

    def dragEnterEvent(self,event):
        """ Decides whether or not the information being dragged can be placed here"""
        if not event.mimeData().hasText():
            event.setAccepted(False)
            return
        data = json.loads(str(event.mimeData().text()))
        if not set(['block','container','snap']).issubset(set(data.keys())):
            event.setAccepted(False)
            return
        if not data['block'] == self.parent.parentBlock.block.index:
            event.setAccepted(False)
            return
        if not self.parent.strType() == data['container']:
            event.setAccepted(False)
            return
        event.setAccepted(True)


    def dropEvent(self,event):
        """ Relocates a MySnap to this position """
        data = json.loads(str(event.mimeData().text()))
        assert(data['block'] == self.parent.parentBlock.block.index)
        assert(data['container'] == self.parent.strType())

        srcIdx = data['snap']
        lowerIdx = self.leftSnap.snap.order if self.leftSnap else None
        upperIdx = self.rightSnap.snap.order if self.rightSnap else None
        snaps = self.parent.parentBlock.block.emitter if isinstance(self.parent,MyEmitter) else self.parent.parentBlock.block.collector
        print snaps.keys()
        print "move snap",srcIdx,"between",lowerIdx,"and",upperIdx

        lastIdx = None
        currIdx = srcIdx
        # If we are moving to the right, lowerIdx is the target index.
        # Clear the dragged snaps's order, then shift all effected snap
        # indices left.
        # NOTE: see #12
        if lowerIdx > srcIdx:
            while isinstance(currIdx,int) and currIdx < (upperIdx or lowerIdx+1):
                nextIdx = snaps[currIdx].rightSnap.order if snaps[currIdx].rightSnap else None
                snaps[currIdx].order = lastIdx
                print "%s -> %s"%(str(currIdx),str(lastIdx))
                lastIdx = currIdx
                currIdx = nextIdx
            # Assertion check. TODO: Remove
            assert lastIdx == lowerIdx, "%r %r"%(lastIdx,lowerIdx)

        # If we are moving to the left, upperIdx is the target index.
        # Clear the dragged snaps order, then shift all effected snaps
        # indices right
        elif upperIdx < srcIdx:
            while isinstance(currIdx,int) and currIdx > lowerIdx:
                nextIdx = snaps[currIdx].leftSnap.order if snaps[currIdx].leftSnap else None
                snaps[currIdx].order = lastIdx
                print "%s -> %s"%(str(currIdx),str(lastIdx))
                lastIdx = currIdx
                currIdx = nextIdx
            # Assertion check. TODO remove
            assert lastIdx == upperIdx, "%r %r"%(lastIdx,upperIdx)

        # Otherwise we are just dragging to the side a bit and nothing is
        # really moving anywhere. Return immediately to avoid trying to
        # give the snap a new order and unnecessary extra linking actions.
        else:
            print "No op!"
            return

        # Finally give the moved object its desired destination. Then
        # make the DrawingBoard relink all the objects again.
        snaps[srcIdx].order = lastIdx
        self.parent.parentBlock.parent.link()


    def paint(self,painter,option,widget):
        painter.setPen(Qt.NoPen)
        painter.drawRect(self.rect())

class MyEmitter(SnapContainer):
    def paint(self,painter,option,widget):
        painter.setPen(Qt.blue)
        painter.drawRect(self.rect())
   
class MyCollector(SnapContainer):
    def paint(self,painter,option,widget):
        painter.setPen(Qt.green)
        painter.drawRect(self.rect())
 
class SnapItem(SpacerContainer.Item):
    def __init__(self,parent,snap):
        typecheck(parent,DrawingBoard,"parent")
        self.snap = snap
        self.snap.visual = self
        # Determine which container you are in
        container = snap.block.visual.myEmitter if snap.isSource() else snap.block.visual.myCollector
        super(SnapItem,self).__init__(parent,container)
        self.setSizePolicy(QSizePolicy(QSizePolicy.Preferred,QSizePolicy.Preferred))
        self.setPreferredWidth(20)
        self.setPreferredHeight(40)
 
    def itemA(self):
        """ We use itemA for the SnapItem to the left """
        return self.snap.leftSnap.visual if self.snap.leftSnap else None

    def itemB(self):
        """ We use itemB for the SnapItem to the right """
        return self.snap.rightSnap.visual if self.snap.rightSnap else None

    def isUsed(self):
        return True


    def mousePressEvent(self,event):
        pos = event.pos()
        print "Snap:",self.snap.order

    def mouseMoveEvent(self, event):
        drag = QDrag(event.widget())
        mimeData = QMimeData()
        mimeData.setText(json.dumps({'block': self.snap.block.index,'container': "emitter" if self.snap.isSource() else "collector",'snap':self.snap.order}))
        drag.setMimeData(mimeData)
        drag.start()


    def mouseReleaseEvent(self,event):
        print "hi"
        self.setCursor(Qt.ArrowCursor)

    def paint(self,painter,option,widget):
        painter.setPen(Qt.red)
        painter.drawRect(self.rect())
        rect = self.geometry()
        if self.snap.posBandLink:
            painter.drawText(6,12,str(self.snap.posBandLink.altitude))
        if self.snap.negBandLink:
            painter.drawText(3,rect.height()-3,str(self.snap.negBandLink.altitude))






class MyContainer(QGraphicsWidget):
    """ Emitter or Collector """
    def __init__(self,parent):
        super(MyContainer,self).__init__(parent=parent)
#         self.parent = typecheck(parent,MyBlock,"parent")
        self.parent = typecheck(parent,BlockItem,"parent")
        self.setSizePolicy(QSizePolicy(QSizePolicy.MinimumExpanding,QSizePolicy.Preferred))
#         self.setPreferredWidth(15)
        self.setMinimumWidth(15)

        # This is a list of spacers in this container
        self._spacers = list() 

    def strType(self):
        """ prints the container type as a string """
        return "emitter" if isinstance(self,MyEmitter) else "collector" if isinstance(self,MyCollector) else "unknown"


    def getLeftSpacer(self,snap):
        #TODO: This seems to work correctly, but the code is a mess :(

        # Find all spacers that have this snap to the right
        ret = filter(lambda x: x.rightSnap == snap, self._spacers)

        # Delete outdated spacers
        for spacer in ret:
            if not spacer.leftSnap == snap.leftSnap:
                # Delete this object, it doesn't match any more
#                 print "Removing old spacer",spacer.leftSnap.order if spacer.leftSnap else None,spacer.rightSnap.order if spacer.rightSnap else None
                self._spacers.remove(spacer)

        ret = filter(lambda x: x.rightSnap == snap, self._spacers)
        # Return existing spacer if only one exists. There should not be extras
        if len(ret) == 1 and ret[0].leftSnap == snap.leftSnap:
#             print "#spacers=",len(self._spacers)
            return ret[0]
        elif len(ret) >= 1:
            raise Exception("To many spacers found! %d"%len(ret))

        # No existing spacers fit. Create a new spacer
#         print "making new left spacer",snap.leftSnap.order if isinstance(snap.leftSnap,Snap) else None, snap.order if isinstance(snap,Snap) else None
        spacer = MyContainer.Spacer(self)
        spacer.rightSnap = snap
        spacer.leftSnap = snap.leftSnap 
        self._spacers.append(spacer)
#         print "#spacers=",len(self._spacers)
        return spacer

    def getRightSpacer(self,snap):
        #TODO: This seems to work correctly, but the code is a mess :(
        
        # Find all spacers that have this snap to the left
        ret = filter(lambda x: x.leftSnap == snap,self._spacers)

        # Delete outdated spacers
        for spacer in ret:
            # Delete this object, it doesn't match any more
            if not spacer.rightSnap == snap.rightSnap:
#                 print "Removing old spacer",spacer.leftSnap.order if spacer.leftSnap else None,spacer.rightSnap.order if spacer.rightSnap else None
                self._spacers.remove(spacer)

        ret = filter(lambda x: x.leftSnap == snap,self._spacers)
        # Return existing spacer if only one exists. There should not be extras
        if len(ret) == 1 and ret[0].rightSnap == snap.rightSnap:
#             print "#spacers=",len(self._spacers)
            return ret[0]
        elif len(ret) >= 1:
            raise Exception("To many spacers found! %d"%len(ret))

        # No existing spacers fit. Create a new spacer
#         print "making new right spacer",snap.order if isinstance(snap,Snap) else None,snap.rightSnap.order if isinstance(snap.rightSnap,Snap) else None
        spacer = MyContainer.Spacer(self)
        spacer.leftSnap = snap
        spacer.rightSnap = snap.rightSnap
        self._spacers.append(spacer)
#         print "#spacers=",len(self._spacers)
        return spacer


    def paint(self,painter,option,widget):
        painter.setPen(Qt.green)
        painter.drawRect(self.rect())

    def mousePressEvent(self,event):
        pos = event.pos()
        print "Emitter" if isinstance(self,MyEmitter) else "Collector" if isinstance(self,MyCollector) else "Container"
        super(MyContainer,self).mousePressEvent(event)

    def mouseReleaseEvent(self,event):
        print "hi"
        self.setCursor(Qt.ArrowCursor)
        super(MyContainer,self).mouseReleaseEvent(event)


    class Spacer(QGraphicsWidget):
        """ Snap Spacer """
        def __init__(self,parent):
            self.parent = typecheck(parent,MyContainer,"parent")
            super(MyContainer.Spacer,self).__init__(parent=parent)
            self.setSizePolicy(QSizePolicy(QSizePolicy.MinimumExpanding,QSizePolicy.Preferred))
            self.setPreferredWidth(15)
            self.setMinimumWidth(15)
            self.setAcceptDrops(True)
            self.leftSnap = None
            self.rightSnap = None


        def link(self):
            l = self.parent.parent.parent.layout()

            # If you have a snap to your left, connect
            target = None
            if self.leftSnap and self.leftSnap.visual:
                l.addAnchor(self, Qt.AnchorLeft, self.leftSnap.visual, Qt.AnchorRight)
                l.addAnchor(self, Qt.AnchorVerticalCenter, self.leftSnap.visual, Qt.AnchorVerticalCenter)
#                 l.addAnchor(self, Qt.AnchorTop, self.leftSnap.visual, Qt.AnchorTop)
#                 l.addAnchor(self, Qt.AnchorBottom, self.leftSnap.visual, Qt.AnchorBottom)

            # Otherwise connect to left container edge
            else:
                l.addAnchor(self, Qt.AnchorLeft, self.parent, Qt.AnchorLeft)
                l.addAnchor(self, Qt.AnchorVerticalCenter, self.parent, Qt.AnchorVerticalCenter)
#                 l.addAnchor(self, Qt.AnchorTop, self.parent, Qt.AnchorTop)
#                 l.addAnchor(self, Qt.AnchorBottom, self.parent, Qt.AnchorBottom)

            # if you have a snap to your right, connect
            if self.rightSnap and self.rightSnap.visual:
                l.addAnchor(self, Qt.AnchorRight, self.rightSnap.visual, Qt.AnchorLeft)
                l.addAnchor(self, Qt.AnchorVerticalCenter, self.rightSnap.visual, Qt.AnchorVerticalCenter)
#                 l.addAnchor(self, Qt.AnchorTop, self.rightSnap.visual, Qt.AnchorTop)
#                 l.addAnchor(self, Qt.AnchorBottom, self.rightSnap.visual, Qt.AnchorBottom)

            # Otherwise connect to the right container edge
            else:
                l.addAnchor(self, Qt.AnchorRight, self.parent, Qt.AnchorRight)
                l.addAnchor(self, Qt.AnchorVerticalCenter, self.parent, Qt.AnchorVerticalCenter)
#                 l.addAnchor(self, Qt.AnchorTop, self.parent, Qt.AnchorTop)
#                 l.addAnchor(self, Qt.AnchorBottom, self.parent, Qt.AnchorBottom)


        def dragEnterEvent(self,event):
            """ Decides whether or not the information being dragged can be placed here"""
            if not event.mimeData().hasText():
                event.setAccepted(False)
                return
            data = json.loads(str(event.mimeData().text()))
            if not set(['block','container','snap']).issubset(set(data.keys())):
                event.setAccepted(False)
                return
            if not data['block'] == self.parent.parent.block.index:
                event.setAccepted(False)
                return
            if not self.parent.strType() == data['container']:
                event.setAccepted(False)
                return
            event.setAccepted(True)


        def dropEvent(self,event):
            """ Relocates a MySnap to this position """
            data = json.loads(str(event.mimeData().text()))
            assert(data['block'] == self.parent.parent.block.index)
            assert(data['container'] == self.parent.strType())

            srcIdx = data['snap']
            lowerIdx = self.leftSnap.order if self.leftSnap else None
            upperIdx = self.rightSnap.order if self.rightSnap else None
            snaps = self.parent.parent.block.emitter if isinstance(self.parent,MyEmitter) else self.parent.parent.block.collector
            print snaps.keys()
            print "move snap",srcIdx,"between",lowerIdx,"and",upperIdx

            lastIdx = None
            currIdx = srcIdx
            # If we are moving to the right, lowerIdx is the target index.
            # Clear the dragged snaps's order, then shift all effected snap
            # indices left.
            # NOTE: see #12
            if lowerIdx > srcIdx:
                while isinstance(currIdx,int) and currIdx < (upperIdx or lowerIdx+1):
                    nextIdx = snaps[currIdx].rightSnap.order if snaps[currIdx].rightSnap else None
                    snaps[currIdx].order = lastIdx
                    print "%s -> %s"%(str(currIdx),str(lastIdx))
                    lastIdx = currIdx
                    currIdx = nextIdx
                # Assertion check. TODO: Remove
                assert lastIdx == lowerIdx, "%r %r"%(lastIdx,lowerIdx)

            # If we are moving to the left, upperIdx is the target index.
            # Clear the dragged snaps order, then shift all effected snaps
            # indices right
            elif upperIdx < srcIdx:
                while isinstance(currIdx,int) and currIdx > lowerIdx:
                    nextIdx = snaps[currIdx].leftSnap.order if snaps[currIdx].leftSnap else None
                    snaps[currIdx].order = lastIdx
                    print "%s -> %s"%(str(currIdx),str(lastIdx))
                    lastIdx = currIdx
                    currIdx = nextIdx
                # Assertion check. TODO remove
                assert lastIdx == upperIdx, "%r %r"%(lastIdx,upperIdx)

            # Otherwise we are just dragging to the side a bit and nothing is
            # really moving anywhere. Return immediately to avoid trying to
            # give the snap a new order and unnecessary extra linking actions.
            else:
                print "No op!"
                return

            # Finally give the moved object its desired destination. Then
            # make the DrawingBoard relink all the objects again.
            snaps[srcIdx].order = lastIdx
            self.parent.parent.parent.link()


        def paint(self,painter,option,widget):
            painter.setPen(Qt.NoPen)
            painter.drawRect(self.rect())


# class MyEmitter(MyContainer):
#     def paint(self,painter,option,widget):
#         painter.setPen(Qt.blue)
#         painter.drawRect(self.rect())
#    
# class MyCollector(MyContainer):
#     def paint(self,painter,option,widget):
#         painter.setPen(Qt.green)
#         painter.drawRect(self.rect())
#    




class MySnap(QGraphicsWidget):
    def __init__(self,parent,snap):
        super(MySnap,self).__init__(parent=parent)
        self.parent = parent
        # The parent here should be a MyContainer
        self.setSizePolicy(QSizePolicy(QSizePolicy.Preferred,QSizePolicy.Preferred))
        self.setPreferredWidth(20)
        self.setPreferredHeight(40)
        # Link with the snap
        self.snap = snap
        self.snap.visual = self

    def link(self):
        """ Link this snap with objects surrounding it. """
        l = self.parent.layout()
#         print "\nLinking Snap",self.snap.order,"in block",self.snap.block.index,"emitter" if self.snap.isSource() else "collector"

        # Determine what container (emitter or collector) you are in, so that 
        # you can link to its edges if necessary
        container = self.snap.block.visual.myEmitter if self.snap.isSource() else self.snap.block.visual.myCollector
        leftSpacer = container.getLeftSpacer(self.snap)
        rightSpacer = container.getRightSpacer(self.snap)
        # Once you have both spacers, make them link to their surrounding snaps
        leftSpacer.link()
        rightSpacer.link()
 
    def mousePressEvent(self,event):
        pos = event.pos()
        print "Snap:",self.snap.order

    def mouseMoveEvent(self, event):
        drag = QDrag(event.widget())
        mimeData = QMimeData()
        mimeData.setText(json.dumps({'block': self.snap.block.index,'container': "emitter" if self.snap.isSource() else "collector",'snap':self.snap.order}))
        drag.setMimeData(mimeData)
        drag.start()


    def mouseReleaseEvent(self,event):
        print "hi"
        self.setCursor(Qt.ArrowCursor)

    def paint(self,painter,option,widget):
        painter.setPen(Qt.red)
        painter.drawRect(self.rect())
        rect = self.geometry()
        if self.snap.posBandLink:
            painter.drawText(6,12,str(self.snap.posBandLink.altitude))
        if self.snap.negBandLink:
            painter.drawText(3,rect.height()-3,str(self.snap.negBandLink.altitude))




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
        self.topology = None
        self.visualBands = list()
        self.visualBlocks = list()
        self.visualSnaps = list()

        self.bandStack = BandStack(self)
        self.blockRibbon = BlockRibbon(self)
 
    def mousePressEvent(self,event):
        print "Spacers:",len(self.bandStack._spacers)+len(self.blockRibbon._spacers)


    def autoLayout(self,topology):
        """ Populates the visualBlocks and visualSnaps lists """
        self.topology = topology
        for altitude,band in topology.bands.items():
            print "adding band",altitude
            visualBand = BandItem(self,band)
            self.visualBands.append(visualBand)

        for index,block in topology.blocks.items():
            print "adding block",index
#             vertexBlock = MyBlock(self,block)
            vertexBlock = BlockItem(self,block)
            self.visualBlocks.append(vertexBlock)
            for snap in block.emitter.values()+block.collector.values():
                print "adding snap",snap.order
#                 mySnap = MySnap(self,snap)
                mySnap = SnapItem(self,snap)
                self.visualSnaps.append(mySnap)
        self.link()
        
    def link(self):
        """ Links up the anchored layouts """
        l = QGraphicsAnchorLayout()
        l.setSpacing(0)
        self.setLayout(l)


        # Anchor BandStack to Layout
        # Anchor BlockRibbon to BandStack
        self.layout().addAnchor(self.blockRibbon, Qt.AnchorTop, self.layout(), Qt.AnchorTop)
        self.layout().addAnchor(self.blockRibbon, Qt.AnchorLeft, self.layout(), Qt.AnchorLeft)
        self.layout().addAnchor(self.bandStack, Qt.AnchorLeft, self.blockRibbon, Qt.AnchorLeft)
        self.layout().addAnchor(self.bandStack, Qt.AnchorRight, self.blockRibbon, Qt.AnchorRight)

        # Start anchoring the other blocks
        print "\n\n__linking bands__"
        print "Current Spacers="
        for spacer in self.bandStack._spacers:
            print spacer.itemA.band.altitude if spacer.itemA else None,spacer.itemB.band.altitude if spacer.itemB else None
        print "End Spacers"
        for b in self.visualBands:
            b.link()
        print "\n\n__Linking blocks__"
        for b in self.visualBlocks:
            b.link()
        print "\n\n__Linking snaps__"
        for s in self.visualSnaps:
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

    def mouseReleaseEvent(self,event):
        pos = event.pos()
        print pos.x(),pos.y()
        super(GraphView,self).mouseReleaseEvent(event)



