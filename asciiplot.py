#!/usr/bin/python
# [db] dan@danbrooks.net 
# Draws an ascii art graph of the visualization
#

from CharGrid import *
from topology import *
from parser import *

vertexSpacing = 5



class Plot(object):
    def __init__(self,topology):
        self.topology = topology
        # height of the entire plot
        self.height =  len(self.topology.bands)+5
        # Width of the entire plot
        self.width =  vertexSpacing*(len(self.topology.blocks)-1) + sum([self.blockWidth(v) for v in self.topology.blocks])
        # Row of the center of the vertex boxes
        self.vline = len(filter(lambda x: x.altitude >0,self.topology.bands.values())) + 2

    def blockWidth(self,index):
        """ Calculate the total width of a vertex block. Base width is 5
        +-+-+ with additional 2 spaces per connection.
        | | |
        +-+-+
        """
        vertexBlock = self.topology.blocks[index]
        return 5+2*(len(vertexBlock.emitter)+len(vertexBlock.collector))

    def blockLeftCol(self,index):
        """ Calculates the left column index for this vertex block index """
        return sum([self.blockWidth(i) for i in range(index)]) + vertexSpacing*index

    def blockCenterCol(self,index):
        """ Calculates the center column index for this vertex index """
        vertexBlock = self.topology.blocks[index]
        return self.blockLeftCol(index)+2+(2*len(vertexBlock.collector))

    def blockRightCol(self,index):
        """ Calculates the right column index for this vertex index """
        vertexBlock = self.topology.blocks[index]
        return self.blockCenterCol(index)+2+(2*len(vertexBlock.emitter))

    def blockCollectorCol(self,vIndex,order):
        """ Calculates the column index for a collector at 'order' in vertex vIndex """
        return self.blockLeftCol(vIndex)+2+(order*2)

    def blockEmitterCol(self,vIndex,order):
        """ Calculates the column index for an emitter at 'order' in vertex vIndex """
        return self.blockCenterCol(vIndex)+2+(order*2)

    def bandRow(self,altitude):
        """ Returns the row index for this altitude """
        magnitude = 2 + abs(altitude)
        return self.vline-magnitude if altitude > 0 else self.vline+magnitude

def draw(topology):
    """ Draw a topology """
    typecheck(topology,Topology,"topology")

    # Initialize Grid to use as a canvas
    grid = CharGrid()

    # Generate plot calculator
    p = Plot(topology)

    # Draw the vertex boxes
    # TODO: Check that there are no negative value keys
    vline = p.vline
    for k in topology.blocks:
        vertexBlock = topology.blocks[k]
        leftCol = p.blockLeftCol(k)

        # Draw the left side of the box
        grid[(p.vline-1,leftCol)] = '+-'
        grid[(p.vline,leftCol)] = '| '
        grid[(p.vline+1,leftCol)] = '+-'

        # Draw Collector spacers
        for o in vertexBlock.collector:
            col = p.blockCollectorCol(k,o)
            grid[(p.vline+1,col)] = '--'
            grid[(p.vline-1,col)] = '--'
 
        # Draw the middle line
        centerCol = p.blockCenterCol(k)
        grid[(p.vline-1,centerCol)] = '+-'
        grid[(p.vline,centerCol)] = '| '
        grid[(p.vline+1,centerCol)] = '+-'

        # Draw the emitter spacers
        for o in vertexBlock.emitter:
            col = p.blockEmitterCol(k,o)
            grid[(p.vline+1,col)] = '--'
            grid[(p.vline-1,col)] = '--'
 
        # Draw the right line
        rightCol = p.blockRightCol(k)
        grid[(p.vline-1,rightCol)] = '+'
        grid[(p.vline,rightCol)] = '|'
        grid[(p.vline+1,rightCol)] = '+'


    # Draw Edge Lines
    # Calculate Edge Lines (but don't draw yet)
    pBands = dict() # rank: [(srcCol,sinkCol,row,altitude), (x,x,x,x), ...]
    nBands = dict() # rank: [(srcCol,sinkCol,row,altitude), 
    for edge in topology.edges:
        for source in edge.sources:
            srcSnap = source.snap
            srcOrder = source.snap.order
            srcCol = p.blockEmitterCol(srcSnap.block.index,srcOrder)
            for sink in edge.sinks:
                sinkSnap = sink.snap
                sinkOrder = sinkSnap.order
                sinkCol = p.blockCollectorCol(sinkSnap.block.index,sinkOrder)

                # Determine if connection should be on top or bottom
                # Positive band connection
                if source.block.index < sink.block.index and edge._pBand is not None:
                    altitude = edge.posBand.altitude
                    row = p.bandRow(altitude)
                    # Initialize rank if it does not already exist
                    if edge.posBand.rank not in pBands:
                        pBands[edge.posBand.rank] = list()
                    # Add arc to rank
                    pBands[edge.posBand.rank] += [(srcCol,sinkCol,row,altitude)]

                # Negative band connection
                elif source.block.index >= sink.block.index and edge._nBand is not None: 
                    altitude = edge.negBand.altitude
                    row = p.bandRow(altitude)
                    if edge.negBand.rank not in nBands:
                        nBands[edge.negBand.rank] = list()
                    nBands[edge.negBand.rank] += [(srcCol,sinkCol,row,altitude)]
                else:
                    print "WARNING: Could not place band!"
                    continue

    # Draw Positive Edges in rank order
    bands = pBands.keys()
    bands.sort(lambda x,y: x-y)
    for rank in bands:
        for srcCol,sinkCol,row,altitude in pBands[rank]:
#             grid[(row,0)] = str(altitude)

            # Draw the vertical source line
            grid[(p.vline-1,srcCol)] = 'A-'
            grid[(row,srcCol+1)] = '.'
            for i in range(vline-2-row):
                grid[(vline-2-i,srcCol)] = '|'

            # Draw the vertical sink line
            grid[(p.vline-1,sinkCol)] = 'V-'
            grid[(row,sinkCol-1)] = '.'
            for i in range(vline-2-row):
                grid[(vline-2-i,sinkCol)] = '|'

            # Draw the horizontal filler
            for x in range(sinkCol-srcCol-3):
                if not (row,srcCol+2+x) in grid or grid[(row,srcCol+2+x)] == "|":
                    grid[(row,srcCol+2+x)] = '-'

    # Draw Negative Edges in rank order
    bands = nBands.keys()
    bands.sort(lambda x,y: x-y)
    for rank in bands:
        for srcCol,sinkCol,row,altitude in nBands[rank]:
#             grid[(row,0)] = str(altitude)

            # Draw the vertical source line
            grid[(p.vline+1,srcCol)] = 'V-'
            grid[(row,srcCol-1)] = "'"
            for i in range(row-(vline+2)):
                grid[(vline+2+i,srcCol)] = '|'

            # Draw the vertical sink line
            grid[(p.vline+1,sinkCol)] = 'A-'
            grid[(row,sinkCol+1)] = "'"
            for i in range(row-(vline+2)):
                grid[(vline+2+i,sinkCol)] = '|'

            # Draw the horizontal filler
            for x in range(srcCol-sinkCol-3):
                if not (row,sinkCol+2+x) in grid or grid[(row,sinkCol+2+x)] == "|":
                    grid[(row,sinkCol+2+x)] = '-'


    print grid
 
    
if __name__ == "__main__":
    topology = parseFile("data/v5.xml")
    print ""
    draw(topology)
