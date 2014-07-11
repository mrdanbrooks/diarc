from qtview import *
# from rosgraph_hooks import RsgUpdater
from ros_topology import *
import gc

class RosTopologyWidget(TopologyWidget):
    def __init__(self,topology,diarcWidget):
        super(RosTopologyWidget,self).__init__(topology)
        self.diarcWidget = diarcWidget
        self.autoLayout()

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
    def __init__(self,context):
        super(RosDiarcWidget,self).__init__(context)
        # Instantiate a diarc topology
        self.rsg = LiveRosSystemGraph() 
        self.rsg.new_object_callback = lambda x: self.new_object_callback(x)

        # Set up the scene and add the topology widget to it 
        self.setScene(QGraphicsScene(self))
        self.topologyWidget = RosTopologyWidget(self.rsg,self)
        self.scene().addItem(self.topologyWidget)

        # Update the RosSystemGraph and do initial linking of objects
        self.rsg.update()
        self.topologyWidget.link()

        self.resize(1024,768)
        self.show()

    def new_object_callback(self,obj):
        print "new object is a ",type(obj)
        if isinstance(obj,Topic):
            print "Adding Band",obj.posBand.altitude
            BandItem(self.topologyWidget,obj.posBand)
            print "Adding Band",obj.negBand.altitude
            BandItem(self.topologyWidget,obj.negBand)
        elif isinstance(obj,Node):
            print "Adding Block",obj.block.index
            BlockItem(self.topologyWidget,obj.block)
        elif isinstance(obj,Publisher) or isinstance(obj,Subscriber):
            print "adding snap",obj.snap.order
            SnapItem(self.topologyWidget,obj.snap)
        else:
            raise Exception("Unexpected type %r"%type(obj))
            

