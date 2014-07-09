
class RosDiarcWidget(QWidget):
    def __init__(self,context):
        super(RosDiarcWidget,self).__init__(context)
        # Instantiate a diarc topology
        self.rsg = RosSystemGraph() 

