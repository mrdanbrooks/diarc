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
#         self.diarcWidget.updater.update(self.topology)
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

#         for obj in gc.get_objects():
#             if isinstance(obj,BlockItem):
#                 count += 1
#         print count

        
class RosDiarcWidget(QGraphicsView):
    def __init__(self,context):
        super(RosDiarcWidget,self).__init__(context)
        # Instantiate a diarc topology
        self.rsg = LiveRosSystemGraph() 
        self.rsg.update()
        
        self.setScene(QGraphicsScene(self))
        self.topologyWidget = RosTopologyWidget(self.rsg,self)
        self.scene().addItem(self.topologyWidget)
        self.resize(1024,768)
        self.show()


