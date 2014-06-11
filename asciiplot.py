#!/usr/bin/python
from CharGrid import *
from topology import *
from parser import *

vertexSpacing = 5

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

    def edgeRow(self,altitude):
        """ Returns the row index for this altitude """
        magnitude = 2 + abs(altitude)
        return self.vline-magnitude if altitude > 0 else self.vline+magnitude

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
    # Go through each line segment (a source to a sink) and draw the line
    for key in topology.edges:
        edge = topology.edges[key]
        altitude = edge.altitude
        row = p.edgeRow(altitude)
        grid[(row,0)] = str(altitude)
        if altitude > 0:
            # Drawing Routings for lines above the vertex boxes
            for src in edge.sources:
                srcOrder = edge.sources[src].emitters.reverseLookup(edge)
                srcCol = p.vertexEmitterCol(src,srcOrder)

                # Draw the vertical source line
                grid[(row,srcCol+1)] = '.'
                for i in range(vline-2-row):
                    grid[(vline-2-i,srcCol)] = '|'

                for sink in edge.sinks:
                    sinkOrder = edge.sinks[sink].collectors.reverseLookup(edge)
                    sinkCol = p.vertexCollectorCol(sink,sinkOrder)

                    # Draw the vertical sink line
                    grid[(row,sinkCol-1)] = '.'
                    for i in range(vline-2-row):
                        grid[(vline-2-i,sinkCol)] = '|'

                    # Draw the horizontal filler
                    for x in range(sinkCol-srcCol-2):
                        if not (row,srcCol+2+x) in grid:
                            grid[(row,srcCol+2+x)] = '-'

        elif altitude < 0:
            # Drawing routines for linse below the vertex boxes
            for src in edge.sources:
                srcOrder = edge.sources[src].emitters.reverseLookup(edge)
                srcCol = p.vertexEmitterCol(src,srcOrder)

                # Draw the vertical source line
                grid[(row,srcCol-1)] = "'"
                for i in range(row-(vline+2)):
                    grid[(vline+2+i,srcCol)] = '|'

                for sink in edge.sinks:
                    sinkOrder = edge.sinks[sink].collectors.reverseLookup(edge)
                    sinkCol = p.vertexCollectorCol(sink,sinkOrder)

                    # Draw the vertical sink line
                    grid[(row,sinkCol+1)] = "'"
                    for i in range(row-(vline+2)):
                        grid[(vline+2+i,sinkCol)] = '|'

                    # Draw the horizontal filler
                    for x in range(srcCol-sinkCol-2):
                        if not (row,sinkCol+2+x) in grid:
                            grid[(row,sinkCol+2+x)] = '-'


        else:
            raise Exception("invalid altitude")

    print grid
        
    
if __name__ == "__main__":
    topology = parseFile("v3.xml")
    draw(topology)


