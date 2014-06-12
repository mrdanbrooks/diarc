from util import *

class Topology(object):
    """
    t = Topology()

    # Create two vertices
    v0 = Vertex(t,0)
    v1 = Vertex(t,1)

    # Add an edge with altitude 1 and rank 0
    e = Edge(t,1,0)
    
    # Connect v0 as source and v1 as sink for edge.
    v0.emitters[0] = EdgeTuple(e,None)
    v1.collectors[0] = EdgeTuple(e,None)

    """

    def __init__(self):
        self.vertices = TypedDict(int,Vertex)   # index: Vertex
        self.edges = TypedDict(int,Edge)        # altitude: Edge

               

class Vertex(object):
    """
    Vertices are drawn as a line of boxes through the middle of the plot. 

    INDEX: The horizontal ordering value of vertices. Left most value must be 0,
        with index values increasing towards the right. Must be unique.
    EMITTERS: A set of ordered EdgeTuples output from the vertex. 
    COLLECTORS: A set of ordered incoming EdgeTuples to the vertex.

    """
    def __init__(self,topology,index):
        typecheck(topology,Topology,"topology")
        typecheck(index,int,"index")
        self._topology = topology
        self.emitters = Vertex.Emitters(self)       # orderNum: [edge, ...]
        self.collectors = Vertex.Collectors(self)   # orderNum: edge
        self.index = index

        # Add to Topology
        # Check that this vertex has a unique index
        if index in self._topology.vertices:
            raise Exception("Vertex with same index already exists")
        self._topology.vertices[index] = self

    class Emitters(TypedDict):
        """ A dict of EdgeTuples representing edge sources. Key values represent
        the 0-indexed order in which the emitters are drawn. Because an emitter
        can be connected to both a positive and negative altitude, the values
        are stored as EdgeTuples.
        """
        def __init__(self,vertex):
            super(Vertex.Emitters,self).__init__(int,EdgeTuple)
            self._vertex = vertex

        def __setitem__(self,orderNum,edgeTuple):
            super(Vertex.Emitters,self).__setitem__(orderNum,edgeTuple)
            pEdge,nEdge = edgeTuple
            if pEdge and not self._vertex in pEdge.sources.values():
                pEdge.sources.insert(self._vertex)
            if nEdge and not self._vertex in nEdge.sources.values():
                nEdge.sources.insert(self._vertex)

        def reverseLookup(self,edge):
            """ returns the reverse lookup dictionary """
            for val,key in dict((v,k) for k,v in self.items()).items():
                if edge in val:
                    return key
            raise Exception("Edge not found")

        def allEdges(self):
            """ List all edges (not in tuple sets) """
            return [item for t in self.values() for item in t if item is not None]

    class Collectors(TypedDict):
        """ A dict of EdgeTuples representing edge sinks. Key values represent
        the 0-indexed order in which the collectors are drawn. Because a collector
        can be connected to both a positive and negative altitude, the values
        are stored as EdgeTuples.
        """
        def __init__(self,vertex):
            super(Vertex.Collectors,self).__init__(int,EdgeTuple)
            self._vertex = vertex

        def __setitem__(self,orderNum,edgeTuple):
            super(Vertex.Collectors,self).__setitem__(orderNum,edgeTuple)
            pEdge,nEdge = edgeTuple
            if pEdge and not self._vertex in pEdge.sinks.values():
                pEdge.sinks.insert(self._vertex)
            if nEdge and not self._vertex in nEdge.sinks.values():
                nEdge.sinks.insert(self._vertex)

        def reverseLookup(self,edge):
            """ returns the reverse lookup dictionary """
            for val,key in dict((v,k) for k,v in self.items()).items():
                if edge in val:
                    return key
            raise Exception("Edge not found")

        def allEdges(self):
            """ List all edges (not in tuple sets) """
            return [item for t in self.values() for item in t if item is not None]



class Edge(object):
    """ An edge represents a single 'class' of directional connections between
        vertices in a graph. It can be thought of as a MIMO connection.

    SOURCES: input vertices to this edge. Must be at least one source.
    SINKS: output vertices to this edge. Must be at least one sink.
    ALTITUDE: 'height' ordering of edge. Non-0 int value. Positive values are 
        above the vertex line, negave values are below. the larger the absolute
        value of the altitude the further away from the vertex line.
    RANK: 'z order' of edges. Positive, int values, edges with larger 
        values are drawn over top of of edges with lower values. Edges with the 
        same rank are considered to be the same edge. Therefore, each positive
        altitude edge must have a unique rank, and similar with negative edges.

    """
    def __init__(self,topology,altitude,rank):
        typecheck(topology,Topology,"topology")
        typecheck(altitude,int,"altitude")
        self._topology = topology
        self.sources = Edge.Sources(self)
        self.sinks = Edge.Sinks(self)
        self.altitude = altitude
        self.rank = rank

        # Add to Topology
        # Check that this edge has a unique altitude
        if altitude in self._topology.edges:
            raise Exception("Edge with same altitude already exists!")
        self._topology.edges[altitude] = self


    class Sources(TypedDict):
        """ A dict of references to source vertices. A Vertex cannot be added to 
        this list prior to this Edge object being added to Vertex's emitters.
        Keys are vertex index values.
        """

        def __init__(self,edge):
            super(Edge.Sources,self).__init__(int,Vertex)
            self._edge = edge
        
        def __checkForValue(self,vertex):
            typecheck(vertex,Vertex,"vertex")
            if vertex in self.values(): 
                raise Exception("Dict already contains the value being set",vertex)
            if not self._edge in vertex.emitters.allEdges():
                raise Exception("Edge must be added to vertex using Vertex.emitters first %r"%vertex.emitters.values())

        def __setitem__(self,index,vertex):
            self.__checkForValue(vertex)
            super(Edge.Sources,self).__setitem__(index,vertex)

        def insert(self,vertex):
            self.__checkForValue(vertex)
            super(Edge.Sources,self).__setitem__(vertex.index,vertex)

    class Sinks(TypedDict):
        """ A List of references to sink vertices. A Vertex cannot be added to 
        this list prior to this Edge object being added to Vertex's collectors.
        Keys are vertex index values.
        """
        def __init__(self,edge):
            super(Edge.Sinks,self).__init__(int,Vertex)
            self._edge = edge
        
        def __checkForValue(self,vertex):
            typecheck(vertex,Vertex,"vertex")
            if vertex in self.values(): 
                raise Exception("Dict already contains the value being set",vertex)
            if not self._edge in vertex.collectors.allEdges():
                raise Exception("Edge must be added to vertex using Vertex.collectors first")

        def __setitem__(self,index,vertex):
            self.__checkForValue(vertex)
            super(Edge.Sinks,self).__setitem__(index,vertex)

        def insert(self,vertex):
            self.__checkForValue(vertex)
            super(Edge.Sinks,self).__setitem__(vertex.index,vertex)


class EdgeTuple(tuple):
    """ A 2-tuple of edges (positive,negative) for a vertex emitter or collector """

    def __new__(cls,*args):
        """ If only one argument is supplied, automatically configure the EdgeTuple.
        If two arguments are supplied, they must be in the correct order. """
        pAltitude, nAltitude = None,None
        if len(args) <= 0:
            raise Exception("You must supply at least one Edge argument")
        elif len(args) == 1:
            typecheck(args[0],Edge,"argument")
            if args[0].altitude > 0:
                pAltitude = args[0]
            else:
                nAltitude = args[0]
        elif len(args) == 2:
            pAltitude,nAltitude = args
        elif len(args) > 2:
            raise Exception("Too many arguments - you can at most have EdgeTuple(positive,negative)")
        EdgeTuple.__checkTuple(pAltitude,nAltitude)
        return super(EdgeTuple,cls).__new__(cls,(pAltitude,nAltitude))


    @staticmethod
    def __checkTuple(p,n):
        if not isinstance(p,Edge) and not isinstance(p,types.NoneType):
            raise Exception("Bad positive type")
        if not isinstance(n,Edge) and not isinstance(n,types.NoneType):
            raise Exception("Bad negative type")
        if p and p.altitude < 1:
            raise Exception("Positive Edge altitude must be greater then 0")
        if n and n.altitude > -1:
            raise Exception("Negative Edge altitude must be less then 0")

    def __add__(self,other):
        """ Combine an EdgeTuple with only postive value with EdgeTuple with
        only negative value. """
        if self[0] is None and other[1] is None:
            return EdgeTuple(self[1],other[0])
        elif self[1] is None and other[0] is None:
            return EdgeTuple(self[0],other[1])
        raise Exception("Unsupported")




