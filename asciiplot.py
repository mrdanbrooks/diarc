#!/usr/bin/python
from CharGrid import *
from topology import *
from parser import *

class GVertex(object):
    def __init__(self,vertex,leftIdx):
        typecheck(vertex,Vertex,"vertex")
        typecheck(leftIdx,int,"leftIdx")
        self._vertex = vertex
        self.leftIdx = leftIdx # Leftmost index of vertex box

        # Make a list of available columns
        self.collectorCols = dict() # altitude: column
        collectors = self._vertex.collectors()
        for i,c in zip(range(len(collectors)),collectors):
            self.collectorCols[c.altitude] = 2+(i*2)
        self.emitterCols = dict() # altitude: column
        emitters = self._vertex.emitters()
        for i,e in zip(range(len(emitters)),emitters):
            self.emitterCols[e.altitude] = 2+len(self.collectorCols)*2+(i*2)

class GEdge(object):
    def __init__(self,srcCol,sinkCol,row):
        self.srcCol = srcCol
        self.sinkCol = sinkCol
        self.row = row


def draw(topology):
    """ Draw a topology """
    typecheck(topology,Topology,"topology")

    # Initialize Grid to use as a canvas
    grid = CharGrid()

    vboxes = dict() # TypedList(GVertex)
    gedges = list() # TypedList(GEdge)
    
    # Draw the vertices boxes
    cidx = 0 # the leftmost column in which to draw the box
    for v in topology.vertices:
        vbox = GVertex(v,cidx)
        vboxes[v.index] = vbox
        # Figure out how many connections are going inside this box
        conns = len(v.emitters())+len(v.collectors())
        grid.writeStr((0,cidx),"+-"+"--"*conns+"+")
        grid.writeStr((1,cidx),"| "+"  "*conns+"|")
        grid.writeStr((2,cidx),"+-"+"--"*conns+"+")
        # Label collector and emitter columns
#         for col in vbox.collectorCols.values():
#             grid[(1,cidx+col)] = 'C'
#         for col in vbox.emitterCols.values():
#             grid[(1,cidx+col)] = 'E'

        # Move leftmost drawing index to start for next box
        cidx += 2+(2*conns)
        cidx += 5 # TODO: Add spacing according to specification

    # NOTE: Draw the edges in order of |altitude|, connections from right to left

    # Calculate the new size of the grid
    altitudes = [e.altitude for e in topology.edges]
    maxAltitude = max(altitudes)
    minAltitude = min(altitudes)
    grid.insertRowsAbove(0,maxAltitude+1)

    # Get the row that runs the center of the vertex boxes
    vridx = 1+maxAltitude+1 

    # Calculate edge connections
    for edge in topology.edges:
        altitude = edge.altitude
        row = vridx + (-altitude-2 if altitude > 0 else abs(altitude)+2)
        for srcVertex in edge.sources():
            src = vboxes[srcVertex.index]
            srcCol = src.emitterCols[altitude]+src.leftIdx
            for sinkVertex in edge.sinks():
                sink = vboxes[sinkVertex.index]
                sinkCol = sink.collectorCols[altitude]+sink.leftIdx
                gedges.append(GEdge(srcCol,sinkCol,row)) #TODO: This should be a row

    # Draw edges
    for gedge in gedges:
        if gedge.row < vridx:
           grid[(vridx-1,gedge.srcCol)] = 'A' 
#            grid[(vridx-2,gedge.srcCol)] = str(gedge.row)
           grid[(vridx-1,gedge.sinkCol)] = 'V'
#            grid[(vridx-2,gedge.sinkCol)] = str(gedge.row)

           dist = gedge.sinkCol - gedge.srcCol - 1
           # Draw altitude lines. The end of each line wraps down with a '.' and
           # the middle has '-' filling. Do not let the fill overwrite the end
           # markers
           grid[(gedge.row,gedge.srcCol+1)] = "."
           for i in range(dist-1):
               if not (gedge.row,gedge.srcCol+2+i) in grid:
                   grid[(gedge.row,gedge.srcCol+2+i)] = '-'
           grid[(gedge.row,gedge.srcCol+(dist-1)+1)] = "."

           # Draw the vertical connections
           for r in range(gedge.row+1,vridx-1):
               grid[(r,gedge.srcCol)] = '|'
               grid[(r,gedge.sinkCol)] = '|'

        if gedge.row > vridx:
           grid[(vridx+1,gedge.srcCol)] = 'V' 
#            grid[(vridx+2,gedge.srcCol)] = str(abs(gedge.row))
           grid[(vridx+1,gedge.sinkCol)] = 'A' 
#            grid[(vridx+2,gedge.sinkCol)] = str(abs(gedge.row))

           dist = gedge.srcCol - gedge.sinkCol - 1
           # Draw altitude lines. The end of each line wraps down with a '.' and
           # the middle has '-' filling. Do not let the fill overwrite the end
           # markers
           grid[(gedge.row,gedge.sinkCol+1)] = "'"
           for i in range(dist-1):
               if not (gedge.row,gedge.sinkCol+2+i) in grid:
                   grid[(gedge.row,gedge.sinkCol+2+i)] = '-'
           grid[(gedge.row,gedge.sinkCol+(dist-1)+1)] = "'"
           
           # Draw the vertical connections
           for r in range(vridx+2,gedge.row):
               grid[(r,gedge.srcCol)] = '|'
               grid[(r,gedge.sinkCol)] = '|'

    print grid


if __name__ == "__main__":
    topology = parseFile("full.xml")
    draw(topology)


