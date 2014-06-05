#!/usr/bin/python
from topology import *
from util import *

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

    def insertRowAbove(self,row):
        """ add a new row above 'row' (shifting existing rows down) """
        keys = filter(lambda k: k[0] >= row,self.keys())
        self.__moveCells(keys,(1,0))

    def insertColToLeft(self,col):
        """ add a new column to the left of 'col' (shifting existing cols right """
        keys = filter(lambda k: k[1] >= col,self.keys())
        self.__moveCells(keys,(0,1))

    def __moveCells(self,keys,direction):
        """ Called by insertRowAbove...
        Moves all cells in 'keys' in 'direction'.
        Each key is 'keys' specified by (row,col). Direction specified by 
        (rowOffset,colOffset).
        """
        while len(keys) > 0:
            keys = self.__moveCell(keys[0],keys,direction)

    def __moveCell(self,srcKey,keys,direction):
        """ Called by __moveCells - recursively moves cells to move srcKey cell """
        self.__checkkey(srcKey)
        self.__checkkey(direction)
        destKey = (srcKey[0]+direction[0],srcKey[1]+direction[1])
#         print "Call to move %s"%str(srcKey)
        # If destination already exists
        if destKey in self:
            keys = self.__moveCell(destKey,keys,direction)
        # copy contents and pop key from self and tmp keylist
        self[destKey] = self[srcKey]
        self.pop(srcKey)
        keys.pop(keys.index(srcKey))
        return keys


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

    
    # Draw the vertices boxes
    vertices = topology.vertices()
    cidx = 0 # the leftmost column in which to draw the box
    for v in vertices:
        # Figure out how many connections are going inside this box
        conns = len(v.emitters)+len(v.collectors)
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
    topology = parseFile("example.xml")
    print "==== Drawing Topology ===="
    draw(topology)


