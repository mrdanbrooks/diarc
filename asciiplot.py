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



# def calcVertexWidth(vertex):
#     """ Calculate the total width of a vertex. Base width is 5
#     +-+-+ with additional 2 spaces per connection.
#     | | |
#     +-+-+
#     """
#     return 5+2*(len(vertex.emitters)+len(vertex.collectors))

class Plot(object):
    def __init__(self,topology):
        self.topology = topology
        # Width of the entire plot
        self.height =  len(self.topology.edges)+5
        # height of the entire plot
        self.width =  vertexSpacing*(len(self.topology.vertices)-1) + sum([self.vertexWidth(v) for v in self.topology.vertices])
        # Row of the center of the vertex boxes
        self.vline = len(filter(lambda x: x.altitude >0,self.topology.edges.values())) + 2

    def vertexWidth(self,index):
        """ Calculate the total width of a vertex. Base width is 5
        +-+-+ with additional 2 spaces per connection.
        | | |
        +-+-+
        """
        vertex = self.topology.vertices[index]
        return 5+2*(len(vertex.emitters)+len(vertex.collectors))

    def vertexLeftCol(self,index):
        """ Calculates the left column index for this vertex index """
        vertex = self.topology.vertices[index]
        return sum([self.vertexWidth(i) for i in range(index)]) + vertexSpacing*index

    def vertexCenterCol(self,index):
        """ Calculates the center column index for this vertex index """
        vertex = self.topology.vertices[index]
        return self.vertexLeftCol(index)+4+(2*max(vertex.collectors))

    def vertexRightCol(self,index):
        """ Calculates the right column index for this vertex index """
        vertex = self.topology.vertices[index]
        return self.vertexCenterCol(index)+4+(2*max(vertex.emitters))

    def vertexCollectorCol(self,vIndex,order):
        """ Calculates the column index for a collector at 'order' in vertex vIndex """
        return self.vertexLeftCol(vIndex)+2+(order*2)

    def vertexEmitterCol(self,vIndex,order):
        """ Calculates the column index for an emitter at 'order' in vertex vIndex """
        return self.vertexCenterCol(vIndex)+2+(order*2)



def draw(topology):
    """ Draw a topology """
    typecheck(topology,Topology,"topology")

    # Initialize Grid to use as a canvas
    grid = CharGrid()

    # Calculate the number of rows needed for the drawing:
    # 3 rows for vertices
    # 2 rows as space (for above above and below vertices)
    # 1 row per edge
    p = Plot(topology)
    print "height=",p.height

    # Calculate the number of columns needed
    print "width=",p.width

    # Draw the vertex boxes - count number of positive altitude lines, add 2
    print "vline=",p.vline
    vline = p.vline

    
    # TODO: Check that there are no negative value keys

    for k in topology.vertices.keys():
        vertex = topology.vertices[k]
        leftCol = p.vertexLeftCol(k)

        # Draw the left side of the box
        grid[(p.vline-1,leftCol)] = '+-'
        grid[(p.vline,leftCol)] = '| '
        grid[(p.vline+1,leftCol)] = '+-'

        # Draw Collector connections
        for o in vertex.collectors:
            for edge in vertex.collectors[o]:
                if edge is None:
                    continue
                col = p.vertexCollectorCol(k,o)
                if edge.altitude > 0:
                    grid[(p.vline-1,col)] = 'V-'
                    grid[(p.vline+1,col)] = '--'
                elif edge.altitude < 0:
                    grid[(p.vline+1,col)] = 'A-'
                    grid[(p.vline-1,col)] = '--'

        # Draw the middle line
        centerCol = p.vertexCenterCol(k)
        grid[(p.vline-1,centerCol)] = '+-'
        grid[(p.vline,centerCol)] = '| '
        grid[(p.vline+1,centerCol)] = '+-'

        # Draw the emitter connections
        for o in vertex.emitters:
            for edge in vertex.emitters[o]:
                if edge is None:
                    continue
                col = p.vertexEmitterCol(k,o)
                if edge.altitude > 0:
                    grid[(p.vline-1,col)] = 'A-'
                    if not (p.vline+1,col) in grid:
                        grid[(p.vline+1,col)] = '--'
                elif edge.altitude < 0:
                    grid[(p.vline+1,col)] = 'V-'
                    if not (p.vline-1,col) in grid:
                        grid[(p.vline-1,col)] = '--'

        # Draw the right line
        rightCol = p.vertexRightCol(k)
        grid[(p.vline-1,rightCol)] = '+'
        grid[(p.vline,rightCol)] = '|'
        grid[(p.vline+1,rightCol)] = '+'


    # Draw Edge Lines
    for key in topology.edges:
        edge = topology.edges[key]
        altitude = edge.altitude




            

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


