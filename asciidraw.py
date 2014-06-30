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



class AsciiBand(AsciiObject):
    def __init__(self,band):
        self.band = typecheck(band,Band,"band")
        self.band.visual = self
        self.above = None
        self.below = None

        # Visual parameters
        self._row = None
        self._startCol = None
        self._endCol = None
        self._isUsed = False

    @property
    def row(self):
        if self._row is None: self.layout()
        return self._row

    @property
    def startCol(self):
        if self._startCol is None: self.layout()
        return self._startCol

    @property
    def endCol(self):
        if self._endCol is None: self.layout()
        return self._endCol


    def layout(self):
        if self.above.row is None:
            self.above.layout()

        self._isUsed = self.band.isUsed()
        if not self._isUsed:
            # Just give the above values
            self._row = self.above.row
            return

        self._row = self.above.row + 1
        print "laying out band",self.band.altitude

        # Determine start and stop columns
        srcSnaps = dict([(s.block.index,s) for s in self.band.emitters])
        sinkSnaps = dict([(s.block.index,s) for s in self.band.collectors])

        # Figure out the binding snaps
        startSnap = None
        endSnap = None
        if self.band.altitude > 0:
            startSnap = srcSnaps[min(srcSnaps.keys())]
            endSnap = sinkSnaps[max(sinkSnaps.keys())]
        else:
            startSnap = sinkSnaps[min(sinkSnaps.keys())]
            endSnap = srcSnaps[max(srcSnaps.keys())]


        # Get the snap positions
        if startSnap.visual.col is None:
            startSnap.visual.layout()
        if endSnap.visual.col is None:
            endSnap.visual.layout()
        self._startCol = startSnap.visual.col+2
        self._endCol = endSnap.visual.col-2
           

    def draw(self,grid):
        if self._isUsed:
            grid[(self.row,0)] = str(self.band.altitude)
            grid[(self.row,self.startCol)] = '-'*((self.endCol-self.startCol)+1)



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
        self.centerRow = None
        self.posBandRow = None
        self.negBandRow = None

    def layout(self):
        # Determine your col location
        # First, figure out what to offset against
        if self.snap.isSource():
            self.col = self.snap.block.visual.centerCol 
        elif self.snap.isSink():
            self.col = self.snap.block.visual.leftCol 
        else:
            raise Exception("Snap isnt Source or Sink")

        # Then add the order offset
        # TODO: This assumes that there are no skipped order values, which 
        # would leave holes when drawing. The correct way would be to get relative 
        # ordering of the order values and take into account missing values.
        self.col += 2 + 2*self.snap.order

        # Get the center row
        self.centerRow = self.snap.block.visual.centerRow

        # Get the band rows (may require doing layout)
        #TODO: row = posBand.visual.row etc should be calculated here instead of in draw


    def draw(self,grid):
        centerRow = self.centerRow
        col = self.col
        posBand = self.snap.posBand
        negBand = self.snap.negBand
        if self.snap.isSink():
            if posBand:
                # Draw a Positive Sink Snap
                row = posBand.visual.row
                grid[(centerRow-1,col)] = 'V-'
                grid[(row,col-1)] = '.'
                for i in range(centerRow-2-row):
                    grid[(centerRow-2-i,col)] = '|'
            if negBand:
                # Draw a Negative Sink Snap
                row = negBand.visual.row
                grid[(centerRow+1,col)] = 'A-'
                grid[(row,col+1)] = "'"
                for i in range(row-(centerRow+2)):
                    grid[(centerRow+2+i,col)] = '|'
        elif self.snap.isSource():
            if posBand:
                # Draw a Positive Source Snap
                row = posBand.visual.row
                grid[(centerRow-1,col)] = 'A-'
                grid[(row,col+1)] = '.'
                for i in range(centerRow-2-row):
                    grid[(centerRow-2-i,col)] = '|'
            if negBand:
                # Draw a Negative Source Snap
                row = negBand.visual.row
                grid[(centerRow+1,col)] = 'V-'
                grid[(row,col-1)] = "'"
                for i in range(row-(centerRow+2)):
                    grid[(centerRow+2+i,col)] = '|'
        else:
            raise Exception("Snap is not source or sink")

class TopLine(AsciiObject):
    def __init__(self,topology):
        self._topology = topology
        self.row = 0

        #Adjoining bands
        self.below = None

    def layout(self):
        self.row = 0

    def draw(self):
        pass


class CornerStone(AsciiObject):
    """ What everything tries to be relative to """
    def __init__(self,topology):
        self._topology = topology
        #Adjoining blocks
        self.rightBlock = None
        # Adjoining bands
        self.above = None
        self.below = None
        # Positioning Parameters
        self.leftCol = None
        self.centerCol = None
        self.rightCol = None
        self.topRow = None
        self.centerRow = None
        self.botRow = None

    @property
    def row(self):
        """ return a calculated row since the spacing here is non-standard. Basically
        we return the empty row below the band of Blocks. This is used for band layout """
        if not self.botRow:
            self.layout()
        return self.botRow+1
        

    def layout(self):
        # TODO: topRow should be replaced with finding height of adjacent bands bottom
        if self.above.row is None:
            self.above.layout()
        self.topRow = self.above.row + 2
#         self.topRow = len(filter(lambda x: x.altitude > 0, self._topology.bands.values())) + 1
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
    cornerStone = CornerStone(topology)
   
    # Create posBands
    bands = topology.bands
    altitudes = bands.keys()
    posAlts = filter(lambda x: x>0,altitudes)
    posAlts.sort(lambda x,y:y-x)# sort ascending
    lastBand = TopLine(topology)
    for band in [bands[a] for a in posAlts]:
        asciiBand = AsciiBand(band)
        asciiBand.above = lastBand
        lastBand.below = asciiBand
        lastBand = asciiBand

    cornerStone.above = lastBand
    lastBand.below = cornerStone

    # Create negBands
    negAlts = filter(lambda x: x<0,altitudes)
    negAlts.sort(lambda x,y:y-x)# sort descending
    lastBand = cornerStone
    for band in [bands[a] for a in negAlts]:
        asciiBand = AsciiBand(band)
        asciiBand.above = lastBand
        lastBand.below = asciiBand
        lastBand = asciiBand

    # Create Blocks and snaps
    lastBlock = cornerStone
    for index,block in topology.blocks.items():
        vertexBlock = AsciiBlock(block)
        vertexBlock.leftBlock = lastBlock
        lastBlock.rightBlock = vertexBlock
        lastBlock = vertexBlock

        collector = block.collector
        for snap in collector.values():
            asciiSnap = AsciiSnap(snap)

        emitter = block.emitter
        for snap in emitter.values():
            asciiSnap = AsciiSnap(snap)
    

    # Perform Layouts
    blocks = topology.blocks
    for k in blocks:
        blocks[k].visual.layout()
    
    for k in bands:
        print "laying out ",bands[k].altitude
        bands[k].visual.layout()

    snaps = [c.snap for c in topology._sources+topology._sinks]
    for snap in snaps:
        snap.visual.layout()

    # Draw
    grid = CharGrid()
    blocks = topology.blocks
    bands = topology.bands
    for k in blocks:
        blocks[k].visual.draw(grid)
    #TODO: Bands and associated snaps should be drawn in rank order
    for k in bands:
        bands[k].visual.draw(grid)
    for snap in snaps:
        snap.visual.draw(grid)

        
    print grid



    
