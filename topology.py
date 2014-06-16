from util import *
import types

class Topology(object):
    def __init__(self):
        self._vertices = TypedList(Vertex)
        self._edges = TypedList(Edge)


    def findBand(self,altitude):
        """ returns the band matching the queried altitude, or None """
        for band in self.bands:
            if band.altitude == altitude:
                return band
        return None

    @property
    def vertices(self):
        return self._vertices

    @property 
    def edges(self):
        return self._edges

    @property
    def blocks(self):
        """ Returns dictionary of all blocks who have a proper index value assigned """
        return dict(filter(lambda x: isinstance(x[0],int),[(v.block.index,v.block) for v in self._vertices]))

    @property
    def bands(self):
        """ Returns dictionary of all bands who have a proper altitude assigned """
        return dict([(band.altitude,band) for edge in self._edges for band in edge.bands])



class Vertex(object):
    """ A Vertex in a directional graph. 
    Sources - outgoing connections to Edges
    Sinks - incomming connections from Edges
    """
    def __init__(self,topology):
        self._topology = typecheck(topology,Topology,"topology")
        self._topology._vertices.append(self)
        # Visual Component
        self.block = Block(self)
        # Connections
        self.sources = TypedList(Source)
        self.sinks = TypedList(Sink)

class Edge(object):
    """ A directional multiple-input multiple-output edge in the graph.
    Sources - inputs from vertices
    Sinks - outputs to vertices
    """
    def __init__(self,topology):
        self._topology = typecheck(topology,Topology,"topology")
        self._topology._edges.append(self)
        # Visual Component
        self._pBand = None
        self._nBand = None
        # Connections
        self.sources = TypedList(Source)
        self.sinks = TypedList(Sink)

    def __get_posBand(self):
        # Initialize on first request
        if self._pBand is None:
            self._pBand = Band(self)
        return self._pBand

    def __get_negBand(self):
        # Initialize on first request
        if self._nBand is None:
            self._nBand = Band(self)
        return self._nBand

    def __get_bands(self):
        return filter(lambda x: isinstance(x,Band), [self._pBand,self._nBand])

    posBand = property(__get_posBand)
    negBand = property(__get_negBand)
    bands = property(__get_bands)

class Connection(object):
    """ Use Source or Sink """
    def __init__(self,topology,vertex,edge):
        self._topology = typecheck(topology,Topology,"topology")
        self._vertex = typecheck(vertex,Vertex,"vertex")
        self._edge = typecheck(edge,Edge,"edge")
        if not (isinstance(self,Source) or isinstance(self,Sink)):
            raise Exception("Do not create connections directly! Use Source or Sink")
        self._snap = Snap(self)

    @property
    def snap(self):
        return self._snap

    @property
    def edge(self): 
        return self._edge

    @property
    def vertex(self): 
        return self._vertex

class Source(Connection):
    """ Connection from Vertex to Edge """
    def __init__(self,topology,vertex,edge):
        super(Source,self).__init__(topology,vertex,edge)
        # Check to make sure there is not already a source going from this vertex to this edge
        for source in vertex.sources + edge.sources:
            if vertex == source.vertex and edge == source.edge:
                raise Exception("Duplicate Source!")
        # Add to Vertex and Edge. 
        vertex.sources.append(self)
        edge.sources.append(self)

class Sink(Connection):
    """ Connection from Edge to Vertex """
    def __init__(self,topology,vertex,edge):
        super(Sink,self).__init__(topology,vertex,edge)
        # Check to make sure there is not already a sink going from this edge to this vertex
        for sink in vertex.sinks + edge.sinks:
            if vertex == sink.vertex and edge == sink.edge:
                raise Exception("Duplicate Sink!")

        vertex.sinks.append(self)
        edge.sinks.append(self)


class Block(object):
    """ Visual Representation of a Vertex 
    Visual Parameters
    Index - 0-indexed order in which draw blocks
    """
    def __init__(self,vertex):
        self._vertex = typecheck(vertex,Vertex,"vertex")
        self._topology = vertex._topology
        # Visual Properties
        self._index = None

    @property
    def vertex(self):
        return self._vertex

    @property
    def emitter(self):
        return dict(filter(lambda x: isinstance(x[0],int),[(s.snap.order,s.snap) for s in self._vertex.sources]))

    @property
    def collector(self):
        return dict(filter(lambda x: isinstance(x[0],int),[(s.snap.order,s.snap) for s in self._vertex.sinks]))

    def __get_index(self):
        return self._index
    def __set_index(self,value):
        """ Check to see if a block with the same index already exists """
        if self._index == value:
            return
        if value is None:
            self._index = value
            return
        allVertices = self._topology._vertices
        allBlocks = [v.block for v in allVertices]
        if value in [b.index for b in allBlocks]:
            raise Exception("Block with index %r already exists!"%value)
        self._index = value

    index = property(__get_index,__set_index)

class Band(object):
    """ Visual Representation of an Edge.
    An Edge can have up to two Bands - one with positive altitude and one negative.
    Visual Parameters
    Rank - the Z drawing order
    Altitude - the distance above or below the Block ribbon
    """
    def __init__(self,edge):
        self._edge = typecheck(edge,Edge,"edge")
        self._topology = edge._topology
        # Visual Properties
        self._altitude = None
        self._rank = None
        # Visual Connections 
        self.sources = TypedList(Snap)
        self.sinks = TypedList(Snap)

    def __get_edge(self):
        return self._edge
    def __get_rank(self):
        return self._rank
    def __set_rank(self,val):
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
        # Make sure the altitude is unique among all bands 
        allEdges = self._topology._edges
        allBands = filter(lambda x: isinstance(x,Band),[band for edge in allEdges for band in edge.bands])
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
        if isinstance(self._connection,Source):
            for band in self._connection.edge.bands:
                band.sources.append(self)
        if isinstance(self._connection,Sink):
            for band in self._connection.edge.bands:
                band.sinks.append(self)
        self._order = None

    @property
    def posBand(self):
        # use pBand instead of posBand to keep from instantiating the Band object
        return self._connection.edge._pBand

    @property
    def negBand(self):
        # use nBand instead of negBand to keep from instantiating the Band object
        return self._connection.edge._nBand

    def __get_block(self):
        return self._connection.vertex.block

    def __get_bands(self):
        return filter(lambda x: isinstance(x,Band), [self.posBand,self.negBand])

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


    bands = property(__get_bands)
    block = property(__get_block)
    order = property(__get_order,__set_order)
 
