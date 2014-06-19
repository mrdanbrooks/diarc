from topology import *
from CharGrid import *


block_spacing = 5


class AsciiObject(object):
    def layout(self):
        """ Determine your location based on neighbor AsciiObjects, calling their layout() method if their values are outdated or non-existant. Next you can call layout on your child objects, finally you should set your own values """
        raise Exception("Not implemented")

    def draw(self,grid):
        """ Draw your contents onto the grid object """
        raise Exception("Not Implemented")



class AsciiBlock(AsciiObject):
    def __init__(self,block):
        self.block = typecheck(block,Block,"block")
        # Create back reference from Block 
        self.block.visual = self

        self.leftBlock = None
        self.rightBlock = None

        # Layout properties
        self._leftCol = None
        self._centerCol = None
        self._rightCol = None
        self._topRow = None
        self._centerRow = None
        self._botRow = None

    @property
    def leftCol(self):
        if self._leftCol is None: self.layout()
        return self._leftCol
        
    @property
    def centerCol(self):
        if self._centerCol is None: self.layout()
        return self._centerCol

    @property
    def rightCol(self):
        if self._rightCol is None: self.layout()
        return self._rightCol

    @property
    def topRow(self):
        if self._topRow is None: self.layout()
        return self._topRow

    @property
    def centerRow(self):
        if self._centerRow is None: self.layout()
        return self._centerRow

    @property
    def botRow(self):
        if self._botRow is None: self.layout()
        return self._botRow

    def layout(self):
        if None in [self.leftBlock.topRow,self.leftBlock.centerRow,self.leftBlock.topRow]:
            self.leftBlock.layout()
        self._topRow = self.leftBlock.topRow
        self._centerRow = self.leftBlock.centerRow
        self._botRow = self.leftBlock.botRow

        if None in [self.leftBlock.leftCol,self.leftBlock.centerCol,self.leftBlock.rightCol]:
            self.leftBlock.layout()
        self._leftCol = self.leftBlock.rightCol + block_spacing + 1
        self._centerCol =  self.leftCol + 2 + 2*len(self.block.collector)
        self._rightCol = self.centerCol + 2 + 2*len(self.block.emitter) 


    def draw(self,grid):
        """ draw this Block into the grid """
        # Draw the left side of the box
        grid[(self.topRow,self.leftCol)] = '+-'
        grid[(self.centerRow,self.leftCol)] = '| '
        grid[(self.botRow,self.leftCol)] = '+-'

        # Draw Collector spacers
        grid[(self.topRow,self.leftCol+1)] = "-"*(self.centerCol-self.leftCol-1)
        grid[(self.botRow,self.leftCol+1)] = "-"*(self.centerCol-self.leftCol-1)

        # Draw the middle line
        grid[(self.topRow,self.centerCol)] = '+-'
        grid[(self.centerRow,self.centerCol)] = '| '
        grid[(self.botRow,self.centerCol)] = '+-'

        # Draw the emitter spacers
        grid[(self.topRow,self.centerCol+1)] = "-"*(self.rightCol-self.centerCol-1)
        grid[(self.botRow,self.centerCol+1)] = "-"*(self.rightCol-self.centerCol-1)
 
        # Draw the right line
        grid[(self.topRow,self.rightCol)] = '+'
        grid[(self.centerRow,self.rightCol)] = '|'
        grid[(self.botRow,self.rightCol)] = '+'

    
class AsciiSnap(AsciiObject):
    def __init__(self,snap):
        self.snap = typecheck(snap,Snap,"snap")
        self.snap.visual = self

        self.leftSnap = None
        self.rightSnap = None

        # Layout properties
        self.col = None

    def layout(self):
        # TODO: Make sure parent layout has values

        # Determine your col location
        # First, figure out what to offset against
        if self.snap.isSource():
            self.col = self.snap.block.visual.leftCol 
        elif self.snap.isSink():
            self.col = self.snap.block.visual.centerCol 
        else:
            raise Exception("Snap isnt Source or Sink")

        # Then add the order offset
        # TODO: This assumes that there are no skipped order values, which 
        # would leave holes when drawing. The correct way would be to get relative 
        # ordering of the order values and take into account missing values.
        self.col + 2 + 2*self.snap.order

#     def draw(self,grid):
#         # Draw a Sink Snap
#         # ================
#         if self.snap.isSink():
#             if self.snap.posBand.edge.sinks
# 
# 
#         # Draw a Source Snap
#         # ==================
#         elif self.snap.isSource():
#             
# 
#         else:
#             raise Exception("Snap is not source or sink")



class AsciiBand(AsciiObject):
    def __init__(self,band):
        self.band = typecheck(band,Band,"band")
        self.band.visual = self
        self.above = None
        self.below = None

    def layout(self):
        pass

    def draw(self,grid):
        pass
   
class LeftIndexBlock(AsciiObject):
    def __init__(self,topology):
        self._topology = topology
        #Adjoining blocks
        self.rightBlock = None
        # Positioning Parameters
        self.leftCol = None
        self.centerCol = None
        self.rightCol = None
        self.topRow = None
        self.centerRow = None
        self.botRow = None

    def layout(self):
        # TODO: topRow should be replaced with finding height of adjacent bands bottom
        self.topRow = len(filter(lambda x: x.altitude > 0, self._topology.bands.values())) + 1
        self.centerRow = self.topRow+1
        self.botRow = self.centerRow+1
        
        self.leftCol = -block_spacing-1
        self.centerCol = -block_spacing-1
        self.rightCol = -block_spacing-1

    def draw(self,grid):
        # This is not a real thing, don't draw anything
        pass




def draw(topology):
    
    # Initialize Visual Elements
    lastBlock = LeftIndexBlock(topology)
    for k in topology.blocks:
        vertexBlock = AsciiBlock(topology.blocks[k])
        vertexBlock.leftBlock = lastBlock
        lastBlock.rightBlock = vertexBlock
        lastBlock = vertexBlock


    # Perform Layouts
    blocks = topology.blocks
    for k in blocks:
        blocks[k].visual.layout()

    # Draw
    grid = CharGrid()
    blocks = topology.blocks
    for k in blocks:
        blocks[k].visual.draw(grid)
        
    print grid



    
