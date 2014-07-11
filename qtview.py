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

    def dragEnterEvent(self,event):
        if not event.mimeData().hasText():
            event.setAccepted(False)
            return
        data = json.loads(str(event.mimeData().text()))
        if not 'band' in data:
            event.setAccepted(False)
            return
        # To know if the band being dragged is on the same side of the blockRibbon,
        # we look at the altitudes of the bands on either side of the spacer. 
        # We need to look at both because neither is guarenteed to be a real band
        # (the furthest and closest bands to the blockRibbon will each have a 
        # non existant band on one side).
        topAltitude = self.topBand.band.altitude if self.topBand else 0
        bottomAltitude = self.bottomBand.band.altitude if self.bottomBand else 0
        # Accept a positive altitude band
        if data['band'] > 0 and (topAltitude > 0 or bottomAltitude > 0):
            event.setAccepted(True)
            self.dragOver = True
            print "Drag Positive ENTER"
        # Accept a negative altitude band
        elif data['band'] < 0 and (topAltitude < 0 or bottomAltitude < 0):
            event.setAccepted(True)
            self.dragOver = True
            print "Drag Negative ENTER"
        else:
            event.setAccepted(False)

    def dragLeaveEvent(self,event):
        self.dragOver = False

    def dropEvent(self,event):
        """ Reorder the band altitudes to put the dropped band in the new position"""
        # Not all bands are necessarily being shown due to the fact that depending
        # on the ordering of the blocks, edge connections could travel different 
        # directions. When reordering bands, we need to take into account ALL
        # the bands (both shown and not shown). 

        # Decode the drag metadata into a dict
        data = json.loads(str(event.mimeData().text()))
        # Get the altitude of the band that was dragged
        srcAlt = data['band']
        # Get the altitudes of the bands displayed above and below this spacer.
        topAltitude = self.topBand.band.altitude if self.topBand else None
        bottomAltitude = self.bottomBand.band.altitude if self.bottomBand else None

        print "topAltitude=",topAltitude,"bottomAltitude=",bottomAltitude

        # Get a copy of the dictionary of bands in the topology
        bands = self.parent.parent.topology.bands

        # These don't necessarily exist if the band is adjacent to the block ribbon
        # or either the top or bottom of the BandStack. In these cases, the values
        # will remain None, so we need to look at both in case one is not good
        # (e.g. currAlt < (upperAlt or lowerAlt+1))
        lowerAlt = None
        upperAlt = None

        # The dragEnterEvent() should prevent positive altitude bands from being
        # dragged below the block ribbon and vice versa. This is necessary because
        # having multiple positive or negative bands for a single edge defeats the
        # purpose of have one band of each edge. So we only need to deal with 
        # reordering all positive or all negative bands. We also need to
        # determine exactly where we want to place the band by determining the 
        # bands on we want to put the dragged band between. For positive bands,
        # we want to be just above the spacer's bottom band. For negative bands
        # we want to be just below the spacer's top band. 
        if srcAlt > 0:
            lowerAlt = bottomAltitude 
            if isinstance(lowerAlt,int):
                tband = bands[lowerAlt].topBand # only calculate topBand once...
                upperAlt = tband.altitude if isinstance(tband,Band) else None
            else:
                # If lowerAlt is None, we are just above the block ribbon
                upperAlt = 1
        else:
            # top altitude is None if we are just below the block ribbon.
            # In that case, we want to be as close to the ribbon as possible.
            upperAlt = topAltitude 
            if isinstance(upperAlt,int):
                lband = bands[upperAlt].bottomBand # only calculate topBand once...
                lowerAlt = lband.altitude if isinstance(lband,Band) else None
            else:
                # If upperAlt is None, we are just below the block ribbon
                lowerAlt = -1

        print "Moving band",srcAlt,"between",lowerAlt, "and",upperAlt

        lastAlt = None
        currAlt = srcAlt

        # If we are moving up, lowerAlt is the target altitude. 
        # Clear the dragged bands's altitude, then shift all effected bands
        # down. See issue #12
        if isinstance(lowerAlt,int) and lowerAlt > srcAlt:
            print "Moving positive up"
            while isinstance(currAlt,int) and currAlt < (upperAlt or lowerAlt+1):
                tband = bands[currAlt].topBand
                nextAlt = tband.altitude if isinstance(tband,Band) else None
                bands[currAlt].altitude = lastAlt
                print "%s -> %s"%(str(currAlt),str(lastAlt))
                lastAlt = currAlt
                currAlt = nextAlt
            # Assertion check
            assert lastAlt == lowerAlt, "%r %r"%(lastAlt,lowerAlt)

        # If we are moving down, upperAlt is the target altitude.
        # Clear the dragged bands altitude, then shift all effected bands up.
        elif isinstance(upperAlt,int) and upperAlt <= srcAlt:
            print "Moving positive down"
            while isinstance(currAlt,int) and currAlt > (lowerAlt or upperAlt-1):
                lband = bands[currAlt].bottomBand
                nextAlt = lband.altitude if isinstance(lband,Band) else None
                bands[currAlt].altitude = lastAlt
                print "%s -> %s"%(str(currAlt),str(lastAlt))
                lastAlt = currAlt
                currAlt = nextAlt
            # Assertion check
            assert lastAlt == upperAlt, "%r %r"%(lastAlt,upperAlt)

        else:
            print "No op!"
            return

        # Finally, give the moved object its desired destination. Then make
        # the TopologyWidget relink all the objects again
        bands[srcAlt].altitude = lastAlt
        self.parent.parent.link()


    def paint(self,painter,option,widget):
#         pen = QPen()
#         pen.setBrush(Qt.lightGray)
#         pen.setStyle(Qt.DotLine)
#         painter.setPen(pen)
        painter.setPen(Qt.NoPen)
        painter.drawRect(self.rect())

class BandItem(SpacerContainer.Item):
    def __init__(self,parent,band):
#         typecheck(parent,DrawingBoard,"parent")
        typecheck(parent,TopologyWidget,"parent")
        super(BandItem,self).__init__(parent,parent.bandStack)
        self.band = band
        self.band.visual = self
        self.setContentsMargins(5,5,5,5)
        self.setSizePolicy(QSizePolicy(QSizePolicy.Preferred,QSizePolicy.MinimumExpanding))
        self.setPreferredHeight(15)
        self.setMinimumHeight(15)
        self.setZValue(self.band.rank)

    def _release(self):
        self.band = None
        super(BandItem,self)._release()

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
        
        # TODO: This needs optimized because the isUsed call is expensive. we 
        # should see if we can call it once at the begining of link perhaps? 
        # then we could cache the value?
        if self.band.isUsed():
            l = self.parent.layout()
            emitters = self.band.emitters
            collectors = self.band.collectors
            emitters.sort(lambda x,y: x.block.index - y.block.index)
            collectors.sort(lambda x,y: x.block.index - y.block.index)
            print "emitters=",[s.block.index for s in emitters]
            print "collectors=",[s.block.index for s in collectors]
            if self.band.isPositive:
                l.addAnchor(self, Qt.AnchorLeft, emitters[0].visual, Qt.AnchorLeft)
                l.addAnchor(self, Qt.AnchorRight, collectors[-1].visual, Qt.AnchorRight)
            else:
                l.addAnchor(self, Qt.AnchorLeft, collectors[0].visual, Qt.AnchorLeft)
                l.addAnchor(self, Qt.AnchorRight, emitters[-1].visual, Qt.AnchorRight)

    def mousePressEvent(self,event):
        pos = event.pos()
        print "Band:",self.band.altitude
        sys.stdout.flush()
        self.setCursor(Qt.ClosedHandCursor)

    def mouseMoveEvent(self, event):
        drag = QDrag(event.widget())
        mimeData = QMimeData()
        mimeData.setText(json.dumps({'band':self.band.altitude}))
        drag.setMimeData(mimeData)
        drag.start()

    def mouseReleaseEvent(self,event):
        print "hi",
        self.setCursor(Qt.ArrowCursor)

    def paint(self,painter,option,widget):
        brush = QBrush()
        brush.setStyle(Qt.SolidPattern)
        brush.setColor(Qt.white)
        painter.fillRect(self.rect(),brush)
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
#         self.parent = typecheck(parent,DrawingBoard,"parent")
        self.parent = typecheck(parent,TopologyWidget,"parent")
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
        # the TopologyWidget relink all the objects again.
        blocks[srcIdx].index = lastIdx
        self.parent.parent.link()

    def paint(self,painter,option,widget):
        painter.setPen(Qt.NoPen)
        painter.drawRect(self.rect())


class BlockItem(SpacerContainer.Item):
    """ This is a QGraphicsWidget for a Diarc Block. """
    def __init__(self,parent,block):
#         typecheck(parent,DrawingBoard,"parent")
        typecheck(parent,TopologyWidget,"parent")
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
    
    def _release(self):
        super(BlockItem,self)._release()
        print "releasing BlockItem %r"%self
        self._topMargin.setParent(None)
        self._botMargin.setParent(None)
        self._topMargin = None
        self._botMargin = None
        self.myEmitter._release()
        self.myCollector._release()
        self.myEmitter = None
        self.myCollector = None
        self.block  = None

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
    
    def _release(self):
        super(SnapContainer,self)._release()
        self.parentBlock = None

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
        # make the TopologyWidget relink all the objects again.
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
#         typecheck(parent,DrawingBoard,"parent")
        typecheck(parent,TopologyWidget,"parent")
        self.snap = snap
        self.snap.visual = self
        # Determine which container you are in
        container = snap.block.visual.myEmitter if snap.isSource() else snap.block.visual.myCollector
        super(SnapItem,self).__init__(parent,container)
        self.setSizePolicy(QSizePolicy(QSizePolicy.Preferred,QSizePolicy.Preferred))
        self.setPreferredWidth(20)
        self.setPreferredHeight(40)
        self.setMaximumHeight(40)

        #Create two SnapBandLinks - one for each band
        self.upLink = SnapBandLink(None)
        self.downLink = SnapBandLink(None)
 
    def _release(self):
        print "releasing SnapItem %r"%self
        self.upLink.setParent(None)
        self.downLink.setParent(None)
        self.upLink = None
        self.downLink = None
        self.snap = None
        self.setVisible(False)
        super(SnapItem,self)._release()


    def itemA(self):
        """ We use itemA for the SnapItem to the left """
        return self.snap.leftSnap.visual if self.snap.leftSnap else None

    def itemB(self):
        """ We use itemB for the SnapItem to the right """
        return self.snap.rightSnap.visual if self.snap.rightSnap else None

    def isUsed(self):
        return True

    def link(self):
        super(SnapItem,self).link()

        #Connect bandlinks
        l = self.parent.layout()
        if self.snap.posBandLink:
            self.upLink.setVisible(True)
            self.upLink.setZValue(self.snap.posBandLink.rank+0.5)
            l.addAnchor(self, Qt.AnchorTop, self.upLink, Qt.AnchorBottom)
            l.addAnchor(self.snap.posBandLink.visual, Qt.AnchorBottom, self.upLink, Qt.AnchorTop)
            l.addAnchor(self, Qt.AnchorLeft, self.upLink, Qt.AnchorLeft)
            l.addAnchor(self, Qt.AnchorRight, self.upLink, Qt.AnchorRight)
        else:
            self.upLink.setVisible(False)
            self.upLink.setParent(None)

        if self.snap.negBandLink:
            self.downLink.setVisible(True)
            self.downLink.setZValue(self.snap.negBandLink.rank+0.5)
            l.addAnchor(self, Qt.AnchorBottom, self.downLink, Qt.AnchorTop)
            l.addAnchor(self.snap.negBandLink.visual, Qt.AnchorTop, self.downLink, Qt.AnchorBottom)
            l.addAnchor(self, Qt.AnchorLeft, self.downLink, Qt.AnchorLeft)
            l.addAnchor(self, Qt.AnchorRight, self.downLink, Qt.AnchorRight)
        else:
            self.downLink.setVisible(False)
            self.downLink.setParent(None)
            

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


class SnapBandLink(QGraphicsWidget):
    def __init__(self,parent):
        super(SnapBandLink,self).__init__(parent=parent)
        self.setVisible(False)
        self.setSizePolicy(QSizePolicy(QSizePolicy.MinimumExpanding,QSizePolicy.MinimumExpanding))
        self.setPreferredWidth(5)
        self.setMinimumWidth(5)
        self.setPreferredHeight(5)
        self.setMinimumHeight(5)
 
    def paint(self,painter,option,widget):
        brush = QBrush()
        brush.setStyle(Qt.SolidPattern)
        brush.setColor(Qt.white)
        painter.fillRect(self.rect(),brush)
        pen = QPen()
        pen.setBrush(Qt.red)
        pen.setStyle(Qt.DashLine)
        painter.setPen(pen)
        painter.drawRect(self.rect())







class TopologyWidget(QGraphicsWidget):
    def __init__(self,topology):
        super(TopologyWidget,self).__init__(parent=None)
        self.setAcceptedMouseButtons(Qt.LeftButton)
        self.resize(0,0)
        self.topology = topology

        self.bandStack = BandStack(self)
        self.blockRibbon = BlockRibbon(self)
 
    def autoLayout(self):
        """ Populates the visualBlocks and visualSnaps lists """
        topology = self.topology
        for altitude,band in topology.bands.items():
            print "adding band",altitude
            visualBand = BandItem(self,band)

        for index,block in topology.blocks.items():
            print "adding block",index
            vertexBlock = BlockItem(self,block)
            for snap in block.emitter.values()+block.collector.values():
                print "adding snap",snap.order
                mySnap = SnapItem(self,snap)
        self.link() 

    def mousePressEvent(self,event):
        print "Spacers:",len(self.bandStack._spacers)+len(self.blockRibbon._spacers)

    def link(self):
        """ Links up the anchored layouts """
        l = QGraphicsAnchorLayout()
        l.setSpacing(0.0)
        self.setLayout(l)


        # Anchor BandStack to Layout
        # Anchor BlockRibbon to BandStack
        self.layout().addAnchor(self.blockRibbon, Qt.AnchorTop, self.layout(), Qt.AnchorTop)
        self.layout().addAnchor(self.blockRibbon, Qt.AnchorLeft, self.layout(), Qt.AnchorLeft)
        self.layout().addAnchor(self.bandStack, Qt.AnchorLeft, self.blockRibbon, Qt.AnchorLeft)
        self.layout().addAnchor(self.bandStack, Qt.AnchorRight, self.blockRibbon, Qt.AnchorRight)

        # Start anchoring the other blocks
        print "Current Spacers="
        for spacer in self.bandStack._spacers:
            print spacer.itemA.band.altitude if spacer.itemA else None,spacer.itemB.band.altitude if spacer.itemB else None
        print "End Spacers"
        print "\n\n__Linking blocks__"
        for block in self.topology.blocks.values():
            block.visual.link()
            # TODO: This could be optimized by implementing a topology.connections
            for snap in block.emitter.values()+block.collector.values():
                snap.visual.link()
        print "\n\n__linking bands__"
        for band in self.topology.bands.values():
            band.visual.link()
        self.layout().invalidate()
        
    def paint(self,painter,option,widget):
        painter.setPen(Qt.blue)
        painter.drawRect(self.rect())


# 
# class DrawingBoard(QGraphicsWidget):
#     """ corresponds with the topology """
#     def __init__(self):
#         super(DrawingBoard,self).__init__(parent=None)
#         self.setAcceptedMouseButtons(Qt.LeftButton)
#         self.resize(0,0)
#         self.topology = None
# 
#         self.bandStack = BandStack(self)
#         self.blockRibbon = BlockRibbon(self)
#  
#     def mousePressEvent(self,event):
#         print "Spacers:",len(self.bandStack._spacers)+len(self.blockRibbon._spacers)
# 
# 
#     def autoLayout(self,topology):
#         """ Populates the visualBlocks and visualSnaps lists """
#         self.topology = topology
#         for altitude,band in topology.bands.items():
#             print "adding band",altitude
#             visualBand = BandItem(self,band)
# 
#         for index,block in topology.blocks.items():
#             print "adding block",index
#             vertexBlock = BlockItem(self,block)
#             for snap in block.emitter.values()+block.collector.values():
#                 print "adding snap",snap.order
#                 mySnap = SnapItem(self,snap)
#         self.link()
#         
#     def link(self):
#         """ Links up the anchored layouts """
#         l = QGraphicsAnchorLayout()
#         l.setSpacing(0.0)
#         self.setLayout(l)
# 
# 
#         # Anchor BandStack to Layout
#         # Anchor BlockRibbon to BandStack
#         self.layout().addAnchor(self.blockRibbon, Qt.AnchorTop, self.layout(), Qt.AnchorTop)
#         self.layout().addAnchor(self.blockRibbon, Qt.AnchorLeft, self.layout(), Qt.AnchorLeft)
#         self.layout().addAnchor(self.bandStack, Qt.AnchorLeft, self.blockRibbon, Qt.AnchorLeft)
#         self.layout().addAnchor(self.bandStack, Qt.AnchorRight, self.blockRibbon, Qt.AnchorRight)
# 
#         # Start anchoring the other blocks
#         print "Current Spacers="
#         for spacer in self.bandStack._spacers:
#             print spacer.itemA.band.altitude if spacer.itemA else None,spacer.itemB.band.altitude if spacer.itemB else None
#         print "End Spacers"
#         print "\n\n__Linking blocks__"
#         for block in self.topology.blocks.values():
#             block.visual.link()
#             # TODO: This could be optimized by implementing a topology.connections
#             for snap in block.emitter.values()+block.collector.values():
#                 snap.visual.link()
#         print "\n\n__linking bands__"
#         for band in self.topology.bands.values():
#             band.visual.link()
#         self.layout().invalidate()
#         
#         
# 
#     def paint(self,painter,option,widget):
#         painter.setPen(Qt.blue)
#         painter.drawRect(self.rect())
# 
# 
class GraphView(QGraphicsView):
    def __init__(self,topology):
        super(GraphView,self).__init__(parent=None)
        self.setScene(QGraphicsScene(self))
        # We might want to do this later to speed things up
        self.topologyWidget = TopologyWidget(topology)

        self.scene().addItem(self.topologyWidget)
        # Basically, I'm not sure how to tell a widget where to go inside a scene.
        # But widgets placed inside widgets seem to be pretty reliable.

        # Set the size of the window
        self.resize(1024,768)

        # Show the window
        self.show()

    def autoLayout(self):
        self.topologyWidget.autoLayout()

    def mousePressEvent(self,event):
        pos = event.pos()
        print pos.x(),pos.y()
        super(GraphView,self).mousePressEvent(event)

    def mouseReleaseEvent(self,event):
        pos = event.pos()
        print pos.x(),pos.y()
        super(GraphView,self).mouseReleaseEvent(event)



