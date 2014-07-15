from qtview import *
# from rosgraph_hooks import RsgUpdater
from ros_topology import *
import gc

class RosBandItem(BandItem):
    def mousePressEvent(self,event):
        print self.band.edge.name

    def paint(self,painter,option,widget):
        brush = QBrush()
        brush.setStyle(Qt.SolidPattern)
        brush.setColor(Qt.white)
        painter.fillRect(self.rect(),brush)
        if self.band.isUsed():
            painter.setPen(Qt.red)
        else:
            painter.setPen(Qt.blue)
        rect = self.geometry()
        painter.drawRect(self.rect())
        painter.drawText(0,rect.height()-2,self.band.edge.name)


class RosTopologyWidget(TopologyWidget):
    def __init__(self,topology,diarcWidget):
        super(RosTopologyWidget,self).__init__(topology)
        self.diarcWidget = diarcWidget
        self.topology.new_object_callback = lambda x: self.new_object_callback(x)
        self.topology.hide_disconnected_snaps = True

    def new_object_callback(self,obj):
        print "new object is a ",type(obj)
        if isinstance(obj,Topic):
            print "Adding Band",obj.posBand.altitude
            RosBandItem(self,obj.posBand)
            print "Adding Band",obj.negBand.altitude
            RosBandItem(self,obj.negBand)
        elif isinstance(obj,Node):
            print "Adding Block",obj.block.index
            BlockItem(self,obj.block)
        elif isinstance(obj,Publisher) or isinstance(obj,Subscriber):
            print "adding snap",obj.snap.order
            SnapItem(self,obj.snap)
        else:
            raise Exception("Unexpected type %r"%type(obj))
 
    def mousePressEvent(self,event):
        self.topology.update()
        self.link()
        print "#########################"
        objTypes = dict()
        for i in range(self.layout().count()):
            t = type(self.layout().itemAt(i))
            if t not in objTypes:
                objTypes[t] = 1
            else:
                objTypes[t] += 1
        for t in objTypes:
            print t,objTypes[t]
        print "total:",self.layout().count()

       
class RosDiarcWidget(QGraphicsView):
    def __init__(self):
        super(RosDiarcWidget,self).__init__(None)
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        # Instantiate a diarc topology
        self.rsg = LiveRosSystemGraph() 

        # Set up the scene and add the topology widget to it 
        self.setScene(QGraphicsScene(self))
        self.topologyWidget = RosTopologyWidget(self.rsg,self)
        self.scene().addItem(self.topologyWidget)

        # Update the RosSystemGraph and do initial linking of objects
        self.rsg.update()
        self.topologyWidget.link()

        self.resize(1024,768)
        self.show()

#     def mousePressEvent(self,event):
#         if event.button() == Qt.MidButton:
#             print "what"
#             print event.modifiers()
#             fakeevent = QMouseEvent(event.type(),event.pos(),Qt.LeftButton,Qt.LeftButton,event.modifiers())
# #             fakeevent.setModifier(Qt.ShiftModifier)
# #             self.mousePressEvent()
#             super(RosDiarcWidget,self).mousePressEvent(fakeevent)
#         elif event.modifiers() == Qt.ShiftModifier:
#             print "now!"
#         else:
#             super(RosDiarcWidget,self).mousePressEvent(event)
# 
#     def mouseReleaseEvent(self,event):
#         if event.button() == Qt.MidButton:
#             self.mouseReleaseEvent(QMouseEvent(event.type(),event.pos(),Qt.LeftButton,Qt.LeftButton,event.modifiers()))
#         else:
#             super(RosDiarcWidget,self).mouseReleaseEvent(event)



    def wheelEvent(self,event):
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        scaleFactor = 1.15
        if event.delta() > 0:
            self.scale(scaleFactor, scaleFactor)
        else:
            self.scale(1.0/scaleFactor, 1.0/scaleFactor)
