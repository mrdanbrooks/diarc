#!/usr/bin/python
from topology import *

class CharGrid(dict):
    """ Grid of single characters for drawing ascii art.
    Keys are (row,col) """
    def __init__(self):
        self.maxRow = 0  # total number of rows
        self.maxCol = 0  # total number of cols
        self._defaultVal = ' '

    def __checkkey(self,key):
        """ Make sure key is a valid key """
        if not isinstance(key,tuple):
            raise Exception("Key must be 2-tuple, got %r"%key)
        if not len(key) == 2:
            raise Exception("Key must be 2-tuple, got %d-tuple"%len(key))
        if not (isinstance(key[0],int) and isinstance(key[1],int)):
            raise Exception("Key value must be of type (int,int), got (%s,%s)"%(key[0].__class__.__name__,key[1].__class__.__name__))

    def __getitem__(self,key):
        """ Get a single character from the grid """
        self.__checkkey(key)
        # If value does not already exist - send back default value
        # Increase our 'size' to report if necessary
        # Don't add it though - this unnecessarily increases the size
        if not key in self:
            self.maxRow = max(key[0],self.maxRow)
            self.maxCol = max(key[1],self.maxCol)
            return self._defaultVal
        return super(CharGrid,self).__getitem__(key)

    def __setitem__(self,key,val):
        """ Set a single character into the grid """
        self.__checkkey(key)
        if not isinstance(val,str):
            raise Exception("Val must be 'str', got %r"%val)
        if len(val) > 1 or len(val) < 1:
            raise Exception("Val must be 1 character long, got %d (%s)"%(len(val),val))
        # Update size values if necessary
        if not key in self:
            self.maxRow = max(key[0],self.maxRow)
            self.maxCol = max(key[1],self.maxCol)
        # Set value
        super(CharGrid,self).__setitem__(key,val)

    def writeStr(self,key,val):
        """ write a string of multiple characters from left to right starting at key """
        for c in val:
            self[key] = c
            key = (key[0],key[1]+1)


    def __str__(self):
        imgbuf = ""
        for r in range(self.maxRow+1):
            rowbuf = list()
            for c in range(self.maxCol+1):
                rowbuf.append(self[(r,c)])
            imgbuf+= "".join(rowbuf)+"\n"
        return imgbuf





def draw(topology):
    """ Draw a topology """
    typecheck(topology,Topology,"topology")

    # Initialize Grid to use as a canvas
    grid = CharGrid()

    vertices = topology.vertices()
    
    # Draw the vertices boxes
    cidx = 0 # the leftmost column in which to draw the box
    for v in vertices:
        # Draw left side of box
        grid.writeStr((0,cidx),"+-")
        grid.writeStr((1,cidx),"| ")
        grid.writeStr((2,cidx),"+-")
        # Expand to fit connections
        conns = len(v._emitters)+len(v._collectors)
        grid.writeStr((0,cidx+2),"--"*conns)
        grid.writeStr((2,cidx+2),"--"*conns)
        # Draw right side of box
        grid[(0,cidx+2+(2*conns))] = "+"
        grid[(1,cidx+2+(2*conns))] = "|"
        grid[(2,cidx+2+(2*conns))] = "+"
        # Move leftmost drawing index to start for next box
        cidx += 2+(2*conns)
        cidx += 5 # TODO: Add spacing according to specification
        
    print grid


if __name__ == "__main__":
    topology = parseFile("example.xml")
    print "==== Drawing Topology ===="
    draw(topology)


