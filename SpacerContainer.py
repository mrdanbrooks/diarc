from PyQt4.QtCore import *
from PyQt4.QtGui import *
from util import *
import sys


class SpacerContainer(QGraphicsWidget):
    """ Creates Spacers
    +--------+          +---------+          +--------+
    | Item A | Spacer A | Current | Spacer B | Item B |
    +--------+          +---------+          +--------+

    +--------+        +--------+
    | Item A | Spacer | Item B |
    +--------+        +--------+
    """
    def __init__(self,parent):
        super(SpacerContainer,self).__init__(parent=parent)
#         self.parent = typecheck(parent,DrawingBoard,"parent")
        self.parent = parent
        self._spacers = list()
        self._spacerType = SpacerContainer.Spacer

    def getSpacerA(self,item):
        print "A=",item
        sys.stdout.flush()
        # Determine if the item is currently being used
        isUsed = item.isUsed()
        # Find spacers where item is itemB (making this spacer A)
        ret = filter(lambda x: x.itemB == item, self._spacers)
        # Delete old unused spacers. Remove them from the QLayout system so 
        # they don't try to draw anymore and from our list of spacers so we
        # don't try to search it anymore.
        print "found ",len(ret)," matches"
        sys.stdout.flush()
        for spacer in ret:
            print spacer.itemA,"==",item.itemA(),"?"
            sys.stdout.flush()
            if (not spacer.itemA == item.itemA()) or (not isUsed):
                print "Removing old spacer",spacer.itemA.band.altitude if spacer.itemA else None,spacer.itemB.band.altitude if spacer.itemB else None
                sys.stdout.flush()
                spacer.setParent(None)
                self._spacers.remove(spacer)
        ret = filter(lambda x: x.itemB == item, self._spacers)
        # Once we have deleted old spacers, make sure we are using the band.
        # If we are not, don't return anything (just None)
        if not isUsed:
            print "#hspacers",len(self._spacers),"not used"
            sys.stdout.flush()
            return None
        # Return existing spacer if only one exists. There should not be extras
        if len(ret) == 1 and ret[0].itemA == item.itemA():
            print "#hspacers",len(self._spacers), "already exists"
            sys.stdout.flush()
            return ret[0]
        elif len(ret) >= 1:
            raise Exception("To many spacers found %d"%len(ret))
        # No existing spacers fit - create a new spacer in direction A
        spacer = self.spacerType(self)
        spacer.itemB = item
        spacer.itemA = item.itemA()
        self._spacers.append(spacer)
        print "#hspacers",len(self._spacers), "added one"
        sys.stdout.flush()
        return spacer

    def getSpacerB(self,item):
        print "B=",item
        sys.stdout.flush()
        """ Finds the spacer for an item in direction b """
        # Determine if the item is currently being used
        isUsed = item.isUsed()
        # Find spacers where item is itemA (making this spacer B)
        ret = filter(lambda x: x.itemA == item, self._spacers)
        # Delete old unused spacers. Remove them from the QLayout system so 
        # they don't try to draw anymore and from our list of spacers so we
        # don't try to search it anymore.
        print "found ",len(ret)," matches"
        sys.stdout.flush()
        for spacer in ret:
            print spacer.itemB,"==",item.itemB(),"?"
            sys.stdout.flush()
            if (not spacer.itemB == item.itemB()) or (not isUsed):
                print "Removing old spacer",spacer.itemA.band.altitude if spacer.itemA else None,spacer.itemB.band.altitude if spacer.itemB else None
                sys.stdout.flush()
                spacer.setParent(None)
                self._spacers.remove(spacer)
        # TODO: This next line may not be needed
        ret = filter(lambda x: x.itemA == item, self._spacers)
        # Once we have deleted old spacers, make sure we are using the band.
        # If we are not, don't return anything (just None)
        if not isUsed:
            print "#hspacers",len(self._spacers),"not used"
            sys.stdout.flush()
            return None
        # Return existing spacer if only one exists. There should not be extras
        if len(ret) == 1 and ret[0].itemB == item.itemB():
            print "#hspacers",len(self._spacers), "already exists"
            sys.stdout.flush()
            return ret[0]
        elif len(ret) >= 1:
            raise Exception("To many spacers found %d"%len(ret))
        # No existing spacers fit - create a new spacer in direction B
        spacer = self.spacerType(self)
        spacer.itemA = item
        spacer.itemB = item.itemB()
        self._spacers.append(spacer)
        print "#hspacers",len(self._spacers), "added one"
        sys.stdout.flush()
        return spacer

    def _get_spacerType(self):
        return self._spacerType
    def _set_spacerType(self,spacerType):
#         self._spacerType = typecheck(spacerType,SpacerContainer.Spacer,"spacerType")
        self._spacerType = spacerType
    spacerType = property(_get_spacerType,_set_spacerType)



    class Spacer(QGraphicsWidget):
        """ A Spacer between two items. """
        def __init__(self,parent):
            self.parent = typecheck(parent,SpacerContainer,"parent")
            self.parent = parent
            super(SpacerContainer.Spacer,self).__init__(parent=parent)
            self.itemA = None
            self.itemB = None

        def layout(self):
            return self.parent.parent.layout()

        def link(self):
            raise Exception("You must implement the linking to the spacersA and B")


    class Item(QGraphicsWidget):
        """ An Item with spacers around it """
        def __init__(self,parent,container):
#             self.parent = typecheck(parent,DrawingBoard,"parent")
            self.parent = parent
            self.container = typecheck(container,SpacerContainer,"container")
            super(SpacerContainer.Item,self).__init__(parent=parent)

        def itemA(self):
            raise Exception("You must implement a way to return itemA")

        def itemB(self):
            raise Exception("You must implement a way to return itemB")

        def isUsed(self):
            """ return if the item is currently being used or not - determines
            if the item will be visible or not 
            """
            raise Exception("You must implement a way to return if the item is used")

        def link(self):
            l = self.parent.layout()
            # Calculate Spacers A and B - deleteing old spacers to this item
            # when necessary, reusing existing spacers if possible, and otherwise
            # creating new spacers
            print "Looking for spacers"
            sys.stdout.flush()
            spacerA = self.container.getSpacerA(self)
            spacerB = self.container.getSpacerB(self)
            if isinstance(spacerA,types.NoneType) or isinstance(spacerB,types.NoneType):
                print "Not linking band",self.band.altitude
                sys.stdout.flush()
#                 self.setVisible(False)
                return
#             self.setVisible(True)
            spacerA.link()
            spacerB.link()



