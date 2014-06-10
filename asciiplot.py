#!/usr/bin/python
from CharGrid import *
from topology import *
from parser import *

vertexSpacing = 5

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


def calcVertexWidth(vertex):
    """ Calculate the total width of a vertex. Base width is 5
    +-+-+ with additional 2 spaces per connection.
    | | |
    +-+-+
    """
    return 5+2*(len(vertex.emitters)+len(vertex.collectors))
    

def draw(topology):
    """ Draw a topology """
    typecheck(topology,Topology,"topology")

    # Initialize Grid to use as a canvas
    grid = CharGrid()

    # Calculate the number of rows needed for the drawing:
    # 3 rows for vertices
    # 2 rows as space (for above above and below vertices)
    # 1 row per edge
    height = len(topology.edges)+5
    print "height=",height

    # Calculate the number of columns needed
    width = vertexSpacing*(len(topology.vertices)-1) + sum([calcVertexWidth(v) for v in topology.vertices.values()])
    print "width=",width

    # Draw the vertex boxes - count number of positive altitude lines, add 3
    vline = len(filter(lambda x: x.altitude >0,topology.edges.values())) + 3
    print "vline=",vline

    # TODO: These keys need to be sorted before printing
    vkeys = topology.vertices.keys()
    
    # TODO: Check that there are no negative value keys

    for k in vkeys:
        vertex = topology.vertices[k]
        leftCol = sum([calcVertexWidth(topology.vertices[i]) for i in range(k)]) + vertexSpacing*k

        # Draw the left side of the box
        grid[(vline-1,leftCol)] = '+-'
        grid[(vline,leftCol)] = '| '
        grid[(vline+1,leftCol)] = '+-'

        # Draw Collector connections
        for o in vertex.collectors:
            edge = vertex.collectors[o]
            if edge.altitude > 0:
                grid[(vline-1,leftCol+2+(o*2))] = 'V-'
                grid[(vline+1,leftCol+2+(o*2))] = '--'
            elif edge.altitude < 0:
                grid[(vline+1,leftCol+2+(o*2))] = 'A-'
                grid[(vline-1,leftCol+2+(o*2))] = '--'

        # Draw the middle line
        centerCol = leftCol+4+(2*max(vertex.collectors))
        grid[(vline-1,centerCol)] = '+-'
        grid[(vline,centerCol)] = '| '
        grid[(vline+1,centerCol)] = '+-'

        # Draw the emitter connections
        for o in vertex.emitters:
            edge = vertex.emitters[o]
            if edge.altitude > 0:
                grid[(vline-1,centerCol+2+(o*2))] = 'A-'
                grid[(vline+1,centerCol+2+(o*2))] = '--'
            elif edge.altitude < 0:
                grid[(vline+1,centerCol+2+(o*2))] = 'V-'
                grid[(vline-1,centerCol+2+(o*2))] = '--'

        # Draw the right line
        rightCol = centerCol+4+(2*max(vertex.emitters))
        grid[(vline-1,rightCol)] = '+'
        grid[(vline,rightCol)] = '|'
        grid[(vline+1,rightCol)] = '+'



            

    print grid
        
    




    exit(0)
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
        # Move leftmost drawing index to start for next box
        cidx += 2+(2*conns)
        cidx += 5

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
                gedges.append(GEdge(srcCol,sinkCol,row)) 
    # Draw edges
    for gedge in gedges:
        if gedge.row < vridx:
           grid[(vridx-1,gedge.srcCol)] = 'A' 
           grid[(vridx-1,gedge.sinkCol)] = 'V'
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
           grid[(vridx+1,gedge.sinkCol)] = 'A' 

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
    topology = parseFile("v3.xml")
    draw(topology)


