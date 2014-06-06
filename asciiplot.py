#!/usr/bin/python
from CharGrid import *
from topology import *
from parser import *

def draw(topology):
    """ Draw a topology """
    typecheck(topology,Topology,"topology")

    # Initialize Grid to use as a canvas
    grid = CharGrid()
    
    # Draw the vertices boxes
    cidx = 0 # the leftmost column in which to draw the box
    for v in topology.vertices:
        # Figure out how many connections are going inside this box
        conns = len(v._emitters)+len(v._collectors)
        grid.writeStr((0,cidx),"+-"+"--"*conns+"+")
        grid.writeStr((1,cidx),"| "+"  "*conns+"|")
        grid.writeStr((2,cidx),"+-"+"--"*conns+"+")
        # Move leftmost drawing index to start for next box
        cidx += 2+(2*conns)
        cidx += 5 # TODO: Add spacing according to specification

    # Draw the edges in order of |altitude|, connections from right to left

    # Calculate the new size of the grid
    altitudes = [e.altitude for e in topology.edges]
    maxAltitude = max(altitudes)
    minAltitude = min(altitudes)
    print "Max Altitudes:", maxAltitude
    print "Min Altitudes:", minAltitude
    grid.insertRowsAbove(0,maxAltitude+1)

    # calculate the row that has the center of the vertex boxes`
    vridx = 1+maxAltitude+1 
    print "Center",vridx
#     for e in topology.edges:

#     for e in edges:
#         p = e.pAltitude
#         n = e.nAltitude


    print grid


if __name__ == "__main__":
    topology = parseFile("full.xml")
    print "==== Drawing Topology ===="
    draw(topology)


