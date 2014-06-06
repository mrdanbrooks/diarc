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

    # Draw the edges
#     edges = topology.edges()
#     vridx = 1  # The center vertex row index
#     for e in edges:
#         p = e.pAltitude
#         n = e.nAltitude


    print grid


if __name__ == "__main__":
    topology = parseFile("full.xml")
    print "==== Drawing Topology ===="
    draw(topology)


