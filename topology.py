# [db] dan@danbrooks.net
#
# Diarc topology objects
# 
# A Diarc topology consists of two types of objects - logical objects and graphical
# objects which visually represent logical objects. 
# 
# Logical objects:                  Graphical Objects:
#   Vertex                          Block
#   Edge                            Band(s)
#   Connection, Source, Sink        Snap(s)
# 
#
# TODO:
# - Document how to create a topology, and how to remove objects from it.
#
# t = Topology()
#
# v1 = Vertext(t)
# v2 = Vertext(t)
# v3 = Vertext(t)
#
# Create an edge from v1 to v2 
# e1 = Edge(t)
# src1 = Source(t,v1,e1)
# snk1 = Sink(t,v2,e1)
# 
# Add connect the edge to v3 as well
# snk2 = Sink(t,v3,e1)
#
# Add an edge from v3 to v1
# e2 = Edge(t)
# src2 = Source(t,v3,e2)
# snk3 = Sink(t,v1,e2)
#
# arrange the vertices in order v1 v2 v3 
# v1.block.index = 0
# v2.block.index = 1
# v3.block.index = 2


from util import *
import types

class Topology(object):
    def __init__(self):
        self._vertices = TypedList(Vertex)
        self._edges = TypedList(Edge)
        self._sources = TypedList(Source)
        self._sinks = TypedList(Sink)

    @property
    def vertices(self):
        """ returns an unordered list of vertex objects in the topology """
        return self._vertices

    @property 
    def edges(self):
        """ returns an unordered list of edge objects in the topology """
        return self._edges

    @property
    def blocks(self):
        """ Returns dictionary of all blocks who have a proper index value assigned """
        return dict(filter(lambda x: isinstance(x[0],int),[(v.block.index,v.block) for v in self._vertices]))

    @property
    def bands(self):
        """ Returns dictionary of all bands, by altitude. Bands which have not
        been assigned altitudes are not reported. However, bands that are not 
        being used (indicated by isUsed()) are shown. 
        """
        allBands = [band for edge in self._edges for band in [edge.posBand,edge.negBand]]
        if None is [band.altitude for band in allBands]:
            print "WARNING: There are bands lacking altitude information! Not all bands are represented"
        return dict([(band.altitude,band) for band in filter(lambda x: isinstance(x.altitude,int),allBands)])


class Vertex(object):
    """ A Vertex in a directional graph. 
    A vertex can connect to multiple edges as either an input (source) or output
    (sink) to the edge. It is graphically represented by a Block object.

    Sources - outgoing connections to Edges
    Sinks - incomming connections from Edges
    """
    def __init__(self,topology):
        self._topology = typecheck(topology,Topology,"topology")
        self._topology._vertices.append(self)
        # Visual Component
        self._block = Block(self)

    def release(self):
        print "releasing vertex %r"%self

        print "... removing from topology"
        # Release yourself from the topology and remove the reference. This
        # needs to be done before destroying blocks, since we preclaculate 
        # block neighbors and that depends on iterating over the vertex list.
        # If we don't cache block neighbors, then the order no longer matters.
        self._topology._vertices.remove(self)

        # Release connections to and from the vertex
        print "... destroying connections"
        for connection in  self._topology._sources + self._topology._sinks:
            if connection.vertex == self:
                connection.release()
        print "... releasing associated block"
        # Release the block object associated with this vertex 
        self._block._release()
        self._block = None
        print "... destroying reference to topology"
        self._topology = None

    @property
    def sources(self):
        """ Returns an unordered list of outgoing connections (Source objects)
        from this vertex.
        """
        return filter(lambda x: x.vertex == self, self._topology._sources)

    @property
    def sinks(self):
        """ Returns an unordered list of outgoing connections (Sink objects)
        from this vertex.
        """
        return filter(lambda x: x.vertex == self, self._topology._sinks)

    @property
    def block(self):
        """ Returns the relative graphical object (Block) for this Vertex. 
        The block cannot be changed 
        """
        return self._block

class Edge(object):
    """ A directional multiple-input multiGple-output edge in the graph. Inputs
    (sources) and outputs (sinks) are linked to vertices. An edge is represented 
    graphically by either 1 or 2 Band objects. 

    Sources - inputs from vertices
    Sinks - outputs to vertices
    """
    def __init__(self,topology):
        self._topology = typecheck(topology,Topology,"topology")
        self._topology._edges.append(self)
        # Visual Component
        self._pBand = Band(self,True)
        self._nBand = Band(self,False)

    def release(self):
        """ Removes this edge from the topology """
        print "releasing edge %r"%self
        # Release connections to and from this edge
        print "... destroying connections"
        for connection in self._topology._sources + self._topology._sinks:
            if connection.edge == self:
                connection.release()
        # Release each of your bands
        print "... releasing associated bands"
        self._pBand._release()
        self._nBand._release()
        # Remove references to your bands
        self._pBand = None
        self._nBand = None
        print "... removing from topology"
        # Release youself from the topology
        self._topology._edges.remove(self)
        # Remove reference to the topology
        self._topology = None

    @property
    def sources(self):
        """ returns list of all source connections to this edge """
        return filter(lambda x: x.edge == self, self._topology._sources)

    @property
    def sinks(self):
        """ returns list of all sink connections from this edge """
        return filter(lambda x: x.edge == self, self._topology._sinks)

    @property
    def posBand(self):
        return self._pBand

    @property
    def negBand(self):
        return self._nBand

class Connection(object):
    """ A base class for connecting a vertex to an edge, but without specifing 
    the nature of the connection (input or output). Rather then using this 
    class directly, Source or Sink objects should be used.
    
    """
    def __init__(self,topology,vertex,edge):
        self._topology = typecheck(topology,Topology,"topology")
        self._vertex = typecheck(vertex,Vertex,"vertex")
        self._edge = typecheck(edge,Edge,"edge")
        if (not isinstance(self,Source)) and (not isinstance(self,Sink)):
            raise Exception("Do not create connections directly! Use Source or Sink")
        self._snap = Snap(self)

    def release(self):
        """ Removes this connection between a vertex and an edge from the topology.
        This does NOT release either the vertex or the edge objects, it simply
        removes this particular reference to them. 
        """
        print "... releasing associated snap"
        # Release and remove the reference to your snap
        self._snap._release()
        self._snap = None
        print "... deleting pointer to vertex and edge"
        # Remove references to vertex and edge
        self._vertex = None
        self._edge = None


    @property
    def snap(self):
        return self._snap

    @property
    def edge(self): 
        return self._edge

    @property
    def vertex(self): 
        return self._vertex

    @property
    def block(self):
        return self.vertex.block

class Source(Connection):
    """ A logical connection from a Vertex to an Edge. Graphically represented 
    by a Snap object.
    """
    def __init__(self,topology,vertex,edge):
        super(Source,self).__init__(topology,vertex,edge)
        # Check to make sure there is not already a source going from this vertex to this edge
        for source in vertex.sources + edge.sources:
            if vertex == source.vertex and edge == source.edge:
                raise Exception("Duplicate Source!")
        self._topology._sources.append(self)

    def release(self):
        print "Releasing Source %r"%self
        super(Source,self).release()
        # Remove yourself from the topology
        print "... removing from topology"
        self._topology._sources.remove(self)
        self._topology = None

class Sink(Connection):
    """ A logical connection from an Edge to a Vertex. Graphically represented
    by a Snap object. 
    """
    def __init__(self,topology,vertex,edge):
        super(Sink,self).__init__(topology,vertex,edge)
        # Check to make sure there is not already a sink going from this edge to this vertex
        for sink in vertex.sinks + edge.sinks:
            if vertex == sink.vertex and edge == sink.edge:
                raise Exception("Duplicate Sink!")
        self._topology._sinks.append(self)

    def release(self):
        print "Releasing Sink %r"%self
        super(Sink,self).release()
        # Remove youself from the topology
        print "... removing from topology"
        self._topology._sinks.remove(self)
        self._topology = None


class Block(object):
    """ Visual Representation of a Vertex 
    Visual Parameters
    Index - Unique int value to determine order in which to draw blocks. 
            Lower values to the left, higher to the right. Indices do not 
            necessarily need to be consecutive.
    """
    def __init__(self,vertex):
        self._vertex = typecheck(vertex,Vertex,"vertex")
        self._topology = vertex._topology
        # Visual Properties
        self._index = None
        # blocks to left and right
#         self._leftBlock = None
#         self._rightBlock = None
        # Visual object
        self.visual = None

    def _release(self):
        """ releases this block from the topology.
        This should only be called by Vertex.release()
        """
        print "removing block %r"%self
        # Remove references of your visual component
        print "... releasing visual"
        if not isinstance(self.visual,types.NoneType):
            self.visual._release()
            self.visual = None
        print "... removing references to left and right blocks"
        #This needs to recalculate the left and right blocks on either side
        #NOTE: This does not collapse index values, so there becomes a "hole"
        # in the index values
#         if self._leftBlock:
#             self._leftBlock._updateNeighbors()
#         if self._rightBlock:
#             self._rightBlock._updateNeighbors()
        # Remove cached references to left and right blocks
#         self._leftBlock = None
#         self._rightBlock = None
        print "... remove reference to vertex"
        # We don't need to call release() on the vertex, it should already be
        # called, we just need to remove the reference
        self._vertex = None
        print "... removing reference to topology"
        self._topology = None





    @property
    def vertex(self):
        """ Returns the logical component (Vertex) for this relative object.
        The vertex is bound to this block, and cannot be changed.
        """
        return self._vertex

    @property
    def emitter(self):
        """ Dictionary of Snaps that represent source connections for this block.
        Only snaps which have been assigned an order value are represented, since
        the order is used as the dictionary key.
        """
        return dict(filter(lambda x: isinstance(x[0],int),[(s.snap.order,s.snap) for s in self._vertex.sources]))

    @property
    def collector(self):
        """ Dictionary of Snaps that represent sink connections for this block.
        Only snaps which have been assigned an order value are represented, since
        the order is used as the dictionary key.
        """
        return dict(filter(lambda x: isinstance(x[0],int),[(s.snap.order,s.snap) for s in self._vertex.sinks]))

    @property
    def leftBlock(self):
#         """ Returns the block to the left, determined by block wich has the next
#         lowest index value. This value is cached when the index is set.  
#         """
#         return self._leftBlock
        if not isinstance(self._index,int):
            return None
        blocks = self._topology.blocks
        if len(blocks) == 0:
            return None
        if self._index > min(blocks.keys()):
            return blocks[max([b for b in blocks.keys() if b < self._index])]
        # Else
        return None

    @property
    def rightBlock(self):
#         """ returns the block to the right, determined by block which has the next
#         highest index value. This  value is cached when the index is set. 
#         """
#         return self._rightBlock
        if not isinstance(self._index,int):
            return None
        blocks = self._topology.blocks
        if len(blocks) == 0:
            return None
        if self._index < max(blocks.keys()):
            return blocks[min([b for b in blocks.keys() if b > self._index])]
        # Else:
        return None



#     def _updateNeighbors(self):
#         """ Update leftIndex and rightIndex, as well as previous neighbors """
#         blocks = self._topology.blocks
#         # First update your former neighbor's left and right values
#         # If there was an item to the left, it needs a new right hand value
#         if len(blocks) > 0:
#             # update old neighbors
#             if not isinstance(self._leftBlock,types.NoneType):
#                 if self._leftBlock.index < max(blocks.keys()):
#                     self._leftBlock._rightBlock = blocks[min([b for b in blocks.keys() if b > self._leftBlock.index])]
#                 else:
#                     self._leftBlock._rightBlock = None
# 
#             if not isinstance(self._rightBlock,types.NoneType):
#                 if self._rightBlock.index > min(blocks.keys()):
#                     self._rightBlock._leftBlock = blocks[max([b for b in blocks.keys() if b < self._rightBlock.index])]
# 
#                 else: 
#                     self._rightBlock._leftBlock = None
# 
#         # Set my current neighbors
#         if isinstance(self._index,types.NoneType):
#             self._leftBlock = None
#             self._rightBlock = None
#         else:
#             # Calculate new values of left and right blocks
#             # update the right value of the left block and left value of the right block
#             # If you are on an edge, leave the value at None
#             if self._index > min(blocks.keys()):
#                 self._leftBlock = blocks[max([b for b in blocks.keys() if b < self._index])]
#                 self._leftBlock._rightBlock = self
#             else:
#                 self._leftBlock = None
# 
#             if self._index < max(blocks.keys()):
#                 self._rightBlock = blocks[min([b for b in blocks.keys() if b > self._index])]
#                 self._rightBlock._leftBlock = self
#             else:
#                 self._rightBlock = None


    def __get_index(self):
        return self._index
    def __set_index(self,value):
        """ Check to see if a block with the same index already exists """
        if self._index == value:
            return
        if isinstance(value,types.NoneType):
            self._index = value
#             self._updateNeighbors()
            return
        allVertices = self._topology._vertices
        allBlocks = [v.block for v in allVertices]
        if value in [b.index for b in allBlocks]:
            raise Exception("Block with index %r already exists!"%value)
        self._index = value
#         self._updateNeighbors()

    index = property(__get_index,__set_index)

class Band(object):
    """ Visual Representation of an Edge.
    An Edge can have up to two Bands - one with positive altitude and one negative.
    Visual Parameters
    Rank - the Z drawing order (higher values closer to user)
    Altitude - the distance above or below the Block ribbon
    """
    def __init__(self,edge,isPositive):
        self._edge = typecheck(edge,Edge,"edge")
        self._topology = edge._topology
        # Visual Properties
        self._isPositive = isPositive
        self._altitude = None
        self._rank = None
        # Visual Connections 
        self.visual = None

    def _release(self):
        """ Release all dependent references this object holds """
        print "removing band %r"%self
        print "... removing visual"
        if not isinstance(self.visual,types.NoneType):
            self.visual._release()
            self.visual = None
        print "... removing edge reference"
        self._edge = None
        print "... removing reference to topology"
        self._topology = None


    @property
    def emitters(self):
        """ returns a list of source snaps that reach this band """
        # We compare the position of each source against the position of the furthest
        # away sink (depending on pos/neg altitude).
        sinkBlockIndices = [s.block.index for s in self.edge.sinks]
        sinkBlockIndices = filter(lambda x: isinstance(x,int), sinkBlockIndices)
        sources = list()
        # Find Sources if this is a  Positive Bands
        if self._altitude and self._altitude > 0:
            maxSinkIndex = max(sinkBlockIndices)
            sources = filter(lambda src: src.block.index < maxSinkIndex, self.edge.sources)
        # Find Sources if this is a  Negative Bands
        elif self._altitude and self._altitude < 0:
            minSinkIndex = min(sinkBlockIndices)
            sources = filter(lambda src: src.block.index >= minSinkIndex, self.edge.sources)
        return [s.snap for s in sources]

    @property
    def collectors(self):
        """ returns list of sink snaps that reach this band """
        sourceBlockIndices = [s.block.index for s in self.edge.sources]
        sourceBlockIndices = filter(lambda x: isinstance(x,int), sourceBlockIndices)
        sinks = list()
        # Find Sinks if this is a  Positive Bands
        if self._altitude and self._altitude > 0:
            minSourceIndex = min(sourceBlockIndices)
            sinks = filter(lambda sink: sink.block.index > minSourceIndex, self.edge.sinks)
        # Find Sinks if this is a  Negative Bands
        elif self._altitude and self._altitude < 0:
            maxSourceIndex = max(sourceBlockIndices)
            sinks = filter(lambda sink: sink.block.index <= maxSourceIndex, self.edge.sinks)
        return [s.snap for s in sinks]

    def isUsed(self):
        """ returns true if this band is needed to represent connections on
        its edge, else false. This is determined by checking if any sources
        reach this band.
        """
        # This should be equivalent to checking if any sinks reach this band,
        # but this has not been tested or proven. 
        sinkBlockIndices = [s.block.index for s in self.edge.sinks if isinstance(s.block.index,int)]
        sourceBlockIndices = [s.block.index for s in self.edge.sources if isinstance(s.block.index,int)]
        if len(sinkBlockIndices) == 0 or len(sourceBlockIndices) == 0:
            return False
        # If positive and there is a sink to the left of any source
        if self._isPositive and max(sinkBlockIndices) >= min(sourceBlockIndices):
            return True
        elif (not self._isPositive) and min(sinkBlockIndices) < max(sourceBlockIndices):
            return True
        else:
            return False

    @property
    def isPositive(self):
        return self._isPositive

    @property
    def topBand(self):
        """ Returns the band with the next highest altitude, or None if either
        there is no band above this one or the block ribbon is above it.
        """
        if not isinstance(self._altitude,int):
            return None
        bands = self._topology.bands
        available = [altitude for altitude in bands.keys() if altitude > self._altitude]
        if self._isPositive:
            # TODO: we probably dont need band._isPositive if altitude > self._altitude
            available = [altitude for altitude in available if bands[altitude]._isPositive and bands[altitude].isUsed()]
        else: 
            available = [altitude for altitude in available if (not bands[altitude]._isPositive) and bands[altitude].isUsed()]
        return bands[min(available)] if len(available) > 0 else None

#         posMax = max([band.altitude for band in bands.values() if band.isUsed()])
#         negVals = [altitude for altitude in bands.keys() if altitude < 0]
#         negMax = max(negVals) if len(negVals) > 0 else 0
#         if (self._isPositive and self._altitude < posMax) or ((not self._isPositive) and self._altitude < negMax) :
#             return bands[min([a for a in bands.keys() if a > self._altitude])]
#         return None

    @property
    def bottomBand(self):
        """ Returns the band with the next lowest altitude, or None if either
        there is no band below this one or the block ribbon is below it.
        """
        if not isinstance(self._altitude,int):
            return None
        bands = self._topology.bands
        available = [altitude for altitude in bands.keys() if altitude < self._altitude]
        if self._isPositive:
            available = [altitude for altitude in available if bands[altitude]._isPositive and bands[altitude].isUsed()]
        else:
            available = [altitude for altitude in available if (not bands[altitude]._isPositive) and bands[altitude].isUsed()]
        return bands[max(available)] if len(available) > 0 else None

#         posVals = [altitude for altitude in bands.keys() if altitude > 0]
#         posMin = min(posVals) if len(posVals) > 0 else 0
#         negMin = min(bands.keys())
#         if (self._isPositive and self._altitude > posMin) or ((not self._isPositive) and self._altitude > negMin):
#             return bands[max([a for a in bands.keys() if a < self._altitude])]
#         return None

    def __get_edge(self):
        return self._edge
    def __get_rank(self):
        return self._rank
    def __set_rank(self,val):
        typecheck(val,int,"val")
        if val < 0:
            raise Exception("Rank must be >= 0, received %d"%val)
        self._rank = val
    
    def __get_altitude(self):
        return self._altitude
    def __set_altitude(self,value):
        if self._altitude == value:
            return
        # Always allow "unsetting" value
        if value is None:
            self._altitude = value
            return
        if self._isPositive and value <= 0:
            raise Exception("Altitude must be positive")
        if (not self._isPositive) and value >= 0:
            raise Exception("Altitude must be negative")
        # Make sure the altitude is unique among all bands 
        allEdges = self._topology._edges
        allBands = filter(lambda x: isinstance(x,Band),[band for edge in allEdges for band in [edge.posBand,edge.negBand]])
        if value in [b.altitude for b in allBands]:
            raise Exception("Band with altitude %d already exists!"%value)
        self._altitude = value

    edge = property(__get_edge)
    rank = property(__get_rank,__set_rank)
    altitude = property(__get_altitude,__set_altitude)

class Snap(object):
    """ Visual Representation of a Source or Sink.
    Snaps are layedout horizontally inside of an Emitter or Collector of a Block.
    A Snap provides a mapping between a Source/Sink and one or two Bands associated with a single Edge.
    Visual Layout Paramters
    Order - 0-indexed order in which to draw snaps within an Emitter or Collector 
    """
    def __init__(self,connection):
        self._connection = typecheck(connection,Connection,"connection")
        self._order = None
        self.visual = None

    def _release(self):
        """ This should only be called by a Connection.release() """
        print "releasing snap %r"%self
        print "... releasing visual"
        if not isinstance(self.visual,types.NoneType):
            self.visual._release()
            self.visual = None
        # the connection should 
        print "... removing reference to connection"
        self._connection = None
        print "... removing reference to topology"
        self._topology = None

    @property
    def posBandLink(self):
        """ returns the positive band connection - if it exists. 
        Just because a positive band link exists does not mean that it should
        be drawn. The check for if we should draw the connection happens at drawing
        time when we decide if we should be using positive or negative"""
        pBand = self._connection.edge._pBand
        # If you are a source snap and there is a sink snap to the right, you connect to this band
        if self.isSource(): 
            indices =  [sink.block.index for sink in pBand.collectors]
            if len(indices) > 0 and max(indices) > self.block.index:
                return pBand
        # if you are a sink snap and there is a source snap to your left, connect to this band
        elif self.isSink():
            indices =[source.block.index for source in pBand.emitters]
            if len(indices) > 0 and min(indices) < self.block.index:
                return pBand
        return None

    @property
    def negBandLink(self):
        """ returns the negative band connection - if it exists. See posBand for
        more details."""
        nBand = self._connection.edge._nBand
        # If you are a source snap and there is a sink snap to the left, connect to this band
        if self.isSource():
            indices = [sink.block.index for sink in nBand.collectors]
            if len(indices) > 0 and min(indices) <= self.block.index:
                return nBand
        # if you are a sink snap and there is a source snap to the right, connect to this band
        elif self.isSink(): 
            indices = [source.block.index for source in nBand.emitters]
            if len(indices) > 0 and max(indices) >= self.block.index:
                return nBand
        return None

    @property
    def block(self):
        return self._connection.vertex.block

    @property
    def connection(self):
        return self._connection

    @property
    def bandLinks(self):
        return filter(lambda x: isinstance(x,Band), [self.posBandLink,self.negBandLink])

    def isSource(self):
        return isinstance(self._connection,Source)

    def isSink(self):
        return isinstance(self._connection,Sink)


    @property
    def leftSnap(self):
        """ Returns the snap directly to the left of this snap within either an emitter or collector. Returns None if this is leftmost snap. """
        snaps = self.block.emitter if self.isSource() else self.block.collector
        if isinstance(self._order,int) and self._order > min(snaps.keys()):
            return snaps[max([s for s in snaps.keys() if s < self._order])]
        else:
            return None

    @property
    def rightSnap(self):
        """ Returns the snap directly to the right of this snap within either an emitter or collector. Returns None if this is rightmost snap. """
        snaps = self.block.emitter if self.isSource() else self.block.collector
        if isinstance(self._order,int) and self._order < max(snaps.keys()):
            return snaps[min([s for s in snaps.keys() if s > self._order])]
        else:
            return None

    def __get_order(self):
        return self._order
    def __set_order(self,value):
        """ Check to see if a snap with the same order already exists """
        if self._order == value:
            return
        # Always allow "unsetting values"
        if value is None:
            self._order = value
            return
        snaps = list()
        # Check to see if the order value exists in this emitter or collector
        if isinstance(self._connection,Source):
            snaps = [e.snap for e in self._connection.vertex.sources]
        if isinstance(self._connection,Sink):
            snaps = [e.snap for e in self._connection.vertex.sinks]
        orders = filter(lambda x: not isinstance(x,types.NoneType),[s.order for s in snaps])
        if value in orders:
            raise Exception("Order value %d already exists!"%value)
        # Update value
        self._order = value

    order = property(__get_order,__set_order)
 
