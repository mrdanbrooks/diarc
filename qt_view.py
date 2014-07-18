from util import *
from SpacerContainer import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import types
import json
import sys

class BandStack(SpacerContainer):
    def __init__(self, parent):
        super(BandStack, self).__init__(parent)
        self.setSizePolicy(QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Preferred))
        self.setMinimumWidth(15)
        self.spacerType = BandSpacer

class BandSpacer(SpacerContainer.Spacer):
    def __init__(self, parent):
        super(BandSpacer, self).__init__(parent)
        self._layout_manager = parent.parent
        self._view = parent.parent.view()
        self._adapter = parent.parent.adapter()
        self.dragOver = False
        self.setSizePolicy(QSizePolicy(QSizePolicy.Preferred, QSizePolicy.MinimumExpanding))
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
        # Link To your Top! If you have a band above, connect
        if self.topBand:
            l.addAnchor(self, Qt.AnchorTop, self.topBand, Qt.AnchorBottom)
        # Otherwise, if it is a positive band, connect to the top of the BandStack
        elif self.bottomBand.isPositive():
            l.addAnchor(self, Qt.AnchorTop, self.parent, Qt.AnchorTop)
        # Otherwise, if it is a negative band, connect to Block Container
        elif not self.bottomBand.isPositive(): 
            l.addAnchor(self, Qt.AnchorTop, self._layout_manager.block_container, Qt.AnchorBottom)

        # Link to your bottom! If you have a band below, connect
        if self.bottomBand:
            l.addAnchor(self, Qt.AnchorBottom, self.bottomBand, Qt.AnchorTop)
        # Otherwise, if it is a positive band, connect to the block ribbon
        elif self.topBand.isPositive():
            l.addAnchor(self, Qt.AnchorBottom, self._layout_manager.block_container, Qt.AnchorTop)
        elif not self.topBand.isPositive():
            l.addAnchor(self, Qt.AnchorBottom, self.parent, Qt.AnchorBottom)
        
        # Connect sides
        l.addAnchor(self, Qt.AnchorLeft, self.parent, Qt.AnchorLeft)
        l.addAnchor(self, Qt.AnchorRight, self.parent, Qt.AnchorRight)

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
        topAltitude = self.topBand.altitude if self.topBand else 0
        bottomAltitude = self.bottomBand.altitude if self.bottomBand else 0
        # Accept a positive altitude band
        if data['band'] > 0 and (topAltitude > 0 or bottomAltitude > 0):
            event.setAccepted(True)
            self.dragOver = True
            self.update()
            print "Drag Positive ENTER"
        # Accept a negative altitude band
        elif data['band'] < 0 and (topAltitude < 0 or bottomAltitude < 0):
            event.setAccepted(True)
            self.dragOver = True
            self.update()
            print "Drag Negative ENTER"
        else:
            event.setAccepted(False)
        self.setZValue(max([self.topBand.altitude if self.topBand else None,
                            self.bottomBand.altitude if self.bottomBand else None]))

    def dragLeaveEvent(self,event):
        self.dragOver = False
        self.update()

    def dropEvent(self,event):
        self.dragOver = False
        self.update()
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
        topAltitude = self.topBand.altitude if self.topBand else None
        bottomAltitude = self.bottomBand.altitude if self.bottomBand else None
        self._adapter.reorder_bands(srcAlt,bottomAltitude,topAltitude)

    def paint(self,painter,option,widget):
        if self.dragOver:
            pen = QPen()
            pen.setBrush(Qt.lightGray)
            pen.setStyle(Qt.DashLine)
            painter.setPen(pen)
        else:
            painter.setPen(Qt.NoPen)
        painter.drawRect(self.rect())



class BandItem(SpacerContainer.Item):
    def __init__(self, parent, altitude, rank):
        self._layout_manager = typecheck(parent, LayoutManagerWidget, "parent")
        self._view = parent.view()
        self._adapter = parent.adapter()
        super(BandItem,self).__init__(parent,parent.bandStack)

        # Band properties - these must be kept up to date with topology
        self.altitude = altitude
        self.rank = rank
        self.top_band = None
        self.bot_band = None
        self.left_most_snap = None
        self.right_most_snap = None

        # Set Qt properties
        self.setContentsMargins(5,5,5,5)
        self.setSizePolicy(QSizePolicy(QSizePolicy.Preferred, QSizePolicy.MinimumExpanding))
        self.setPreferredHeight(15)
        self.setMinimumHeight(15)
        self.setZValue(rank)

    def itemA(self):
        """ Set itemA to be the topBand """
        # This is computed and assigned by the adapter prior to linking
        return self.top_band

    def itemB(self):
        """ Set itemB to be the bottomBand """
        # This is computed and assigned by the adapter prior to linking
        return self.bot_band

    def isUsed(self):
        """ Deprecated """
        return True

    def isPositive(self):
        return True if self.altitude > 0 else False

    def link(self):
        sys.stdout.flush()
        # Assign the vertical anchors
        super(BandItem,self).link()
        # Assign the horizontal Anchors
        l = self.parent.layout()
        l.addAnchor(self, Qt.AnchorLeft, self.left_most_snap, Qt.AnchorLeft)
        l.addAnchor(self, Qt.AnchorRight, self.right_most_snap, Qt.AnchorRight)

    def mouseMoveEvent(self, event):
        if event.buttons() != Qt.LeftButton:
            super(BandItem,self).mouseMoveEvent(event)
        else:
            drag = QDrag(event.widget())
            mimeData = QMimeData()
            mimeData.setText(json.dumps({'band':self.altitude}))
            drag.setMimeData(mimeData)
            drag.start()

    def paint(self,painter,option,widget):
        brush = QBrush()
        brush.setStyle(Qt.SolidPattern)
        brush.setColor(Qt.white)
        painter.fillRect(self.rect(),brush)
        painter.setPen(Qt.red)
        painter.drawRect(self.rect())
        rect = self.geometry()
        painter.drawText(0,rect.height(),str(self.altitude))




class BlockContainer(SpacerContainer):
    def __init__(self, parent):
        super(BlockContainer,self).__init__(parent)
        self.spacerType = BlockSpacer
        self.parent = typecheck(parent,LayoutManagerWidget, "parent")
        self._view = parent.view()
        self._adapter = parent.adapter()
        self.setSizePolicy(QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Preferred))
        self.setMinimumWidth(15)

    def paint(self, painter, option, widget):
        painter.setPen(Qt.green)
        painter.drawRect(self.rect())

class BlockSpacer(SpacerContainer.Spacer):
    def __init__(self,parent):
        super(BlockSpacer,self).__init__(parent)
        self._view = parent.parent.view()
        self._adapter = parent.parent.adapter()
        self.dragOver = False
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
            self.update()
        else:
            event.setAccepted(False)

    def dragLeaveEvent(self, event):
        self.dragOver = False
        self.update()

    def dropEvent(self, event):
        """ Dropping a 'block' on a BlockSpacer triggers a reordering event """
        self.dragOver = False
        self.update()
        # Dragged Index
        data = json.loads(str(event.mimeData().text()))
        if not 'block' in data:
            raise Exception("Wrong drag data type!")
        srcIdx = data['block']
        # Left Index
        lowerIdx = self.leftBlock.block.index if self.leftBlock else None
        upperIdx = self.rightBlock.block.index if self.rightBlock else None
        self._adapter.reorder_blocks(srcIdx, lowerIdx, upperIdx)

    def paint(self, painter, option, widget):
        if self.dragOver:
            pen = QPen()
            pen.setBrush(Qt.lightGray)
            pen.setStyle(Qt.DashLine)
            painter.setPen(pen)
        else:
            painter.setPen(Qt.NoPen)
        painter.drawRect(self.rect())


class BlockItem(SpacerContainer.Item):
    """ This is a QGraphicsWidget for a Diarc Block. """
    #TODO: Item Release() and impelemnt the snap containers
    def __init__(self, parent, block_index):
        self._layout_manager = typecheck(parent, LayoutManagerWidget, "parent")
        self._view = parent.view()
        self._adapter = parent.adapter()
        super(BlockItem, self).__init__(parent, parent.block_container)

        # Qt Settings
        self.setSizePolicy(QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding))
        self.setPreferredHeight(5)
        self.setMinimumHeight(5)
        self.setContentsMargins(5,5,5,5)

        # Properties - these values must be kept up-to-date whenever the model changes
        self.block_index = block_index
        self.left_block = None
        self.right_block = None

        # We want to have a little space above and below the Emitter/Collector,
        # Set up top and bottom margin to give that space. 
        self._topMargin = BlockItem.HorizontalSpacer(self)
        self._botMargin = BlockItem.HorizontalSpacer(self)
        self._middleSpacer = BlockItem.MiddleSpacer(self)

        # Set up Emitter and Collector Containers. They will sit "inside" the 
        # block margins
        self.myEmitter = MyEmitter(self)
        self.myCollector = MyCollector(self)

    def itemA(self):
        """ We use itemA for the BlockItem to the left. """
        # Get the index to our left, and return the BlockItem with that value
#         left_index = self._adapter.get_left_block_index(self.block_index)
#         if isinstance(left_index, types.NoneType):
#             return None
#         return self._layout_manager.get_block_item(left_index)  
        return self.left_block

    def itemB(self):
        """ We use itemB for the BlockItem to the right. """
        # Get the index to our right, and return the BlockItem with that value
#         right_index = self._adapter.get_right_block_index(self.block_index)
#         if isinstance(right_index, types.NoneType):
#             return None
#         return self._layout_manager.get_block_item(right_index)
        return self.right_block

    def isUsed(self):
        return True

    def link(self):
        """ Link to other objects around you. In addition to linking to other 
        blocks, we need to link to our top and bottom margins, and the emitter
        and collector containers 
        """
        # Link with other BlockItems
        super(BlockItem, self).link()
        
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

        l.addAnchor(self._middleSpacer, Qt.AnchorTop, self.myEmitter, Qt.AnchorTop)
        l.addAnchor(self._middleSpacer, Qt.AnchorTop, self.myCollector, Qt.AnchorTop)
        l.addAnchor(self._middleSpacer, Qt.AnchorBottom, self.myEmitter, Qt.AnchorBottom)
        l.addAnchor(self._middleSpacer, Qt.AnchorBottom, self.myCollector, Qt.AnchorBottom)

        l.addAnchor(self, Qt.AnchorLeft, self.myCollector, Qt.AnchorLeft)
        l.addAnchor(self, Qt.AnchorRight, self.myEmitter, Qt.AnchorRight)
        l.addAnchor(self.myCollector, Qt.AnchorRight, self._middleSpacer, Qt.AnchorLeft)
        l.addAnchor(self._middleSpacer, Qt.AnchorRight, self.myEmitter, Qt.AnchorLeft)

    def mouseMoveEvent(self, event):
        """ Creates a drag event with the block information """
        if event.buttons() != Qt.LeftButton:
            super(BlockItem, self).mouseMoveEvent(event)
        else:
            drag = QDrag(event.widget())
            mimeData = QMimeData()
            mimeData.setText(json.dumps({'block': self.block_index}))
            drag.setMimeData(mimeData)
            drag.start()

    def paint(self,painter,option,widget):
        painter.setPen(Qt.red)
        painter.drawRect(self.rect())

    class MiddleSpacer(QGraphicsWidget):
        def __init__(self,parent):
            super(BlockItem.MiddleSpacer,self).__init__(parent=parent)
            # NOTE: I originally tried to set this to Preferred, MinimumExpanding
            # but ran into trouble when the layout could not compute itself when
            # it set that mode. For some reason, it was very unhappy about giving
            # it height policy information.
            self.blockItem = parent
            self.setSizePolicy(QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred))
            self.setPreferredWidth(20)
            self.setMinimumWidth(20)

        def paint(self,painter,option,widget):
            painter.setPen(Qt.NoPen)
            painter.drawRect(self.rect())

    class HorizontalSpacer(QGraphicsWidget):
        def __init__(self,parent):
            super(BlockItem.HorizontalSpacer,self).__init__(parent=parent)
            self.setSizePolicy(QSizePolicy(QSizePolicy.MinimumExpanding,QSizePolicy.Preferred))
            self.setPreferredHeight(5)
            self.setMinimumHeight(5)
            self.setMaximumHeight(5)
            self.setMinimumWidth(5)

class SnapContainer(SpacerContainer):
    def __init__(self,parent):
        super(SnapContainer, self).__init__(parent.parent)
        self.parentBlock = typecheck(parent, BlockItem, "parent")

        self.spacerType = SnapSpacer
        self.setSizePolicy(QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Preferred))
        self.setMinimumWidth(15)
    
    def strType(self):
        """ prints the container type as a string """
        return "emitter" if isinstance(self,MyEmitter) else "collector" if isinstance(self,MyCollector) else "unknown"

    def paint(self,painter,option,widget):
        painter.setPen(Qt.green)
        painter.drawRect(self.rect())

class MyEmitter(SnapContainer):
    def paint(self, painter, option, widget):
        painter.setPen(Qt.blue)
        painter.drawRect(self.rect())
   
class MyCollector(SnapContainer):
    def paint(self, painter, option, widget):
        painter.setPen(Qt.green)
        painter.drawRect(self.rect())
 

class SnapSpacer(SpacerContainer.Spacer):
    def __init__(self,parent):
        super(SnapSpacer,self).__init__(parent)
        self.dragOver = False
        
        # Qt Properties
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
            l.addAnchor(self, Qt.AnchorTop, self.leftSnap, Qt.AnchorTop)
            l.addAnchor(self, Qt.AnchorBottom, self.leftSnap, Qt.AnchorBottom)
        # Otherwise connect to left container edge
        else:
            l.addAnchor(self, Qt.AnchorLeft, self.parent, Qt.AnchorLeft)
            l.addAnchor(self, Qt.AnchorTop, self.parent, Qt.AnchorTop)
            l.addAnchor(self, Qt.AnchorBottom, self.parent, Qt.AnchorBottom)
        # if you have a snap to your right, connect
        if self.rightSnap:
            l.addAnchor(self, Qt.AnchorRight, self.rightSnap, Qt.AnchorLeft)
            l.addAnchor(self, Qt.AnchorTop, self.rightSnap, Qt.AnchorTop)
            l.addAnchor(self, Qt.AnchorBottom, self.rightSnap, Qt.AnchorBottom)
        # Otherwise connect to the right container edge
        else:
            l.addAnchor(self, Qt.AnchorRight, self.parent, Qt.AnchorRight)
            l.addAnchor(self, Qt.AnchorTop, self.parent, Qt.AnchorTop)
            l.addAnchor(self, Qt.AnchorBottom, self.parent, Qt.AnchorBottom)

    def dragEnterEvent(self, event):
        """ Decides whether or not the information being dragged can be placed here"""
        if not event.mimeData().hasText():
            event.setAccepted(False)
            return
        data = json.loads(str(event.mimeData().text()))
        if not set(['block', 'container', 'snap']).issubset(set(data.keys())):
            event.setAccepted(False)
            return
        if not data['block'] == self.parent.parentBlock.block_index:
            event.setAccepted(False)
            return
        if not self.parent.strType() == data['container']:
            event.setAccepted(False)
            return
        event.setAccepted(True)
        self.dragOver = True
        self.update()

    def dragLeaveEvent(self, event):
        self.dragOver = False
        self.update()

    def dropEvent(self,event):
        """ Relocates a MySnap to this position """
        data = json.loads(str(event.mimeData().text()))
        assert(data['block'] == self.parent.parentBlock.block_index)
        assert(data['container'] == self.parent.strType())

        srcIdx = data['snap']
        lowerIdx = self.left_snap.snap_order if self.left_snap else None
        upperIdx = self.right_snap.snap_order if self.right_snap else None
        self._adapter.reorder_snaps(data['block'], data['container'], srcIdx, lowerIdx, upperIdx)

    def paint(self, painter, option, widget):
        painter.setPen(Qt.NoPen)
        painter.drawRect(self.rect())

class SnapItem(SpacerContainer.Item):
    def __init__(self, parent, block_index, container_name, snap_order):
        self._layout_manager = typecheck(parent, LayoutManagerWidget, "parent")
        self._view = parent.view()
        self._adapter = parent.adapter()

        # 
        assert(container_name in ["emitter","collector"])
        self.block_index = block_index
        self.snap_order = snap_order
        self.block_item = self._layout_manager.get_block_item(block_index)
        self.container = self.block_item.myEmitter if container_name == "emitter" else self.block_item.myCollector
        # SnapItems to the left and to the right - populated by the adapter
        self.left_snap = None
        self.right_snap = None
        # Positive and Negative BandItems this snap connects to - only exists if
        # the band is being used - populated by the adapter
        self.posBandItem = None
        self.negBandItem = None
        super(SnapItem,self).__init__(parent,self.container)

        # Qt Properties
        self.setSizePolicy(QSizePolicy(QSizePolicy.Preferred,QSizePolicy.Preferred))
        self.setPreferredWidth(20)
        self.setPreferredHeight(40)
        self.setMaximumHeight(40)

        #Create two SnapBandLinks - one for each band
        self.upLink = SnapBandLink(None)
        self.downLink = SnapBandLink(None)
 
    def itemA(self):
        """ We use itemA for the SnapItem to the left """
        return self.left_snap
#         return self.snap.leftSnap.visual if self.snap.leftSnap else None

    def itemB(self):
        """ We use itemB for the SnapItem to the right """
        # When we don't display unused snaps, we are still reporting unused snaps to 
        # our left and right here - only they don't visually exists which causes problems
        return self.right_snap
#         return self.snap.rightSnap.visual if self.snap.rightSnap else None

    def isUsed(self):
        """ Deprecated """
        return True

    def link(self):
        super(SnapItem, self).link()
        l = self.parent.layout()
#         print "linking snap",self.snap.order,"in block",self.snap.block.index
        l.addAnchor(self, Qt.AnchorTop, self.container, Qt.AnchorTop)
        l.addAnchor(self, Qt.AnchorBottom, self.container, Qt.AnchorBottom)

        #Connect bandlinks
        if self.posBandItem:
            self.upLink.setVisible(True)
            self.upLink.setZValue(self.posBandItem.rank+0.5)
            l.addAnchor(self, Qt.AnchorTop, self.upLink, Qt.AnchorBottom)
            l.addAnchor(self.posBandItem, Qt.AnchorBottom, self.upLink, Qt.AnchorTop)
            l.addAnchor(self, Qt.AnchorLeft, self.upLink, Qt.AnchorLeft)
            l.addAnchor(self, Qt.AnchorRight, self.upLink, Qt.AnchorRight)
        else:
            self.upLink.setVisible(False)
            self.upLink.setParent(None)

        if self.negBandItem:
            self.downLink.setVisible(True)
            self.downLink.setZValue(self.negBandItem.rank+0.5)
            l.addAnchor(self, Qt.AnchorBottom, self.downLink, Qt.AnchorTop)
            l.addAnchor(self.negBandItem, Qt.AnchorTop, self.downLink, Qt.AnchorBottom)
            l.addAnchor(self, Qt.AnchorLeft, self.downLink, Qt.AnchorLeft)
            l.addAnchor(self, Qt.AnchorRight, self.downLink, Qt.AnchorRight)
        else:
            self.downLink.setVisible(False)
            self.downLink.setParent(None)

    def mouseMoveEvent(self, event):
        if event.buttons() != Qt.LeftButton:
            super(SnapItem,self).mouseMoveEvent(event)
        else:
            drag = QDrag(event.widget())
            mimeData = QMimeData()
            mimeData.setText(json.dumps({'block': self.block_index,'container': self.container.strType(),'snap':self.snap_order}))
            drag.setMimeData(mimeData)
            drag.start()

    def paint(self, painter, option, widget):
        painter.setPen(Qt.red)
        painter.drawRect(self.rect())
        rect = self.geometry()
        if self.posBandItem:
            painter.drawText(6,12,str(self.posBandItem.altitude))
        if self.negBandItem:
            painter.drawText(3,rect.height()-3,str(self.negBandItem.altitude))


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








class LayoutManagerWidget(QGraphicsWidget):
    """ Holds the actual qt anchoredlayout and top level SpacerContainers """
    def __init__(self, view):
        super(LayoutManagerWidget, self).__init__(parent=None)
        self._view = view
        self.resize(0,0)
        
        # Top Level Layout Containers
        self.block_container = BlockContainer(self)
        self.bandStack = BandStack(self)

        # Visual Object we are tracking
        self._block_items = TypedList(BlockItem)
        self._band_items = TypedList(BandItem)
        self._snap_items = TypedList(SnapItem)

    def add_block_item(self, index):
        """ create a new BlockItem """
        # Check to make sure the object does not exist
        items = self._find_block_items(index)
        if len(items) > 0:
            raise Exception("%d Block Item with index %d already exists"%(len(items), index))
        # Create the new item
        item = BlockItem(self, index)
        self._block_items.append(item)
        return item

    def get_block_item(self, index):
        """ Returns a BlockItem with specified index """
        items = self._find_block_items(index)
        if len(items) < 1:
            raise LookupError("Block Item with index %d not found"%index)
        elif len(items) == 1:
            return items[0]
        else:
            raise Exception("Found %d objects reporting to have index %d"%(len(items), index))

    def _find_block_items(self, index):
        """ return a list of all block items that meet this criteria """
        return [item for item in self._block_items if item.block_index == index]


    def add_band_item(self, altitude, rank):
        """ Create a new drawable object to correspond to a Band. """
        # Make sure band does not exist
        items = self._find_band_items(altitude)
        if len(items) > 0:
            raise Exception("%d BandItem with altitude %d already exists"%(len(items), altitude))
        item = BandItem(self, altitude, rank)
        self._band_items.append(item)
        return item

    def remove_band_item(self, altitude):
        """ Remove the drawable object to correspond to a band """ 
        raise NotImplementedError()

    def get_band_item(self, altitude):
        """ Returns the BandItem with the given altitude """
        items = self._find_band_items(altitude)
        if len(items) < 1:
            raise LookupError("Band Item with altitude %d not found"%altitude)
        elif len(items) == 1:
            return items[0]
        else:
            raise Exception("Found %d objects reporting to have altitude %d"%(len(items), altitude))

    def _find_band_items(self, altitude):
        """ return a list of all BandItems that meet this criteria """
        return [item for item in self._band_items if item.altitude == altitude]

    def add_snap_item(self, block_index, container, order):
        # Make sure item does not exist
        items = self._find_snap_items(block_index, container, order)
        if len(items) > 0:
            raise Exception("%d BandItem with altitude %d already exists"%(len(items), altitude))
        item = SnapItem(self, block_index, container, order)
        self._snap_items.append(item)
        return item

    def get_snap_item(self, block_index, container, order):
        """ Return the SnapItem """
        items = self._find_snap_items(block_index, container, order)
        if len(items) < 1:
            raise LookupError("Snap Item with order %d for block %d %s not found"%(
                    order, block_index, container))
        elif len(items) == 1:
            return items[0]
        else:
            raise Exception("Found %d objects reporting to have order %d for block %d %s not found"%(
                    len(items), order, block_index, container))

    def _find_snap_items(self, block_index, container, order):
        """ return a list of all SnapItems that meets the following criteria """
        items = [item for item in self._snap_items if item.block_index == block_index]
        items = [item for item in items if item.container.strType() == container]
        items = [item for item in items if item.snap_order == order]
        return items


    def view(self):
        return self._view

    def adapter(self):
        return self._view.adapter

    def link(self):
        # Create a new anchored layout. Until I can figure out how to remove
        # objects from the layout, I need to make a new one each time
        l = QGraphicsAnchorLayout()
        l.setSpacing(0.0)
        self.setLayout(l)

        # Anchor BandStack to Layout, and BlockContainer to BandStack
        self.layout().addAnchor(self.block_container, Qt.AnchorTop, self.layout(), Qt.AnchorTop)
        self.layout().addAnchor(self.block_container, Qt.AnchorLeft, self.layout(), Qt.AnchorLeft)
        self.layout().addAnchor(self.bandStack, Qt.AnchorLeft, self.block_container, Qt.AnchorLeft)
        self.layout().addAnchor(self.bandStack, Qt.AnchorRight, self.block_container, Qt.AnchorRight)

        # Link block items
        for item in self._block_items:
            item.link()

        # Link band items
        for item in self._band_items:
            item.link()

        # Link Snap Items
        for item in self._snap_items:
            item.link()
