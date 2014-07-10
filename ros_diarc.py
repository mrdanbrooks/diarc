from qtview import *
# from rosgraph_hooks import RsgUpdater
from ros_topology import *
import gc

class RosDrawingBoard(DrawingBoard):
    def __init__(self,diarcWidget):
        super(RosDrawingBoard,self).__init__()
        self.diarcWidget = diarcWidget
        self.topology = diarcWidget.rsg
        self.autoLayout(self.topology)
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
        self.rsg = RosSystemGraph() 
        self.rsg.update()
        
        self.setScene(QGraphicsScene(self))
        self.drawingBoard = RosDrawingBoard(self)
        self.scene().addItem(self.drawingBoard)
        self.resize(1024,768)
        self.show()

#     def autoLayout(self):
#         self.updater.update(self.rsg)
#         self.drawingBoard.autoLayout(self.rsg)

