#!/usr/bin/python

from util import *

class Topology(object):
    def __init__(self):
        self.vertices = TypedDict(int,Vertex)   # index: Vertex
        self.edges = TypedDict(int,Edge)        # altitude: Edge

               

class Vertex(object):
    """
    Vertices are drawn as a line of boxes through the middle of the plot. 

    INDEX: The horizontal ordering value of vertices. Left most value must be 0,
        with index values increasing towards the right. Must be unique.
    EMITTERS: A set of ordered edges output from the vertex. 
    COLLECTORS: A set of ordered incoming edges to the vertex.

    """
    def __init__(self,topology,index):
        typecheck(topology,Topology,"topology")
        typecheck(index,int,"index")
        self._topology = topology
        self.emitters = Vertex.Emitters(self)       # orderNum: edge
        self.collectors = Vertex.Collectors(self)   # orderNum: edge
        self.index = index

        # Add to Topology
        # Check that this vertex has a unique index
        if index in self._topology.vertices:
            raise Exception("Vertex with same index already exists")
        self._topology.vertices[index] = self

    class Emitters(TypedDict):
        def __init__(self,vertex):
            super(Vertex.Emitters,self).__init__(int,Edge)
            self._vertex = vertex
        
        def __setitem__(self,orderNum,edge):
#             if orderNum in self.keys() and self.values().count(self[orderNum]) == 1:
#                 print "removing only occurance of ",self[orderNum]
#                 edge.sources.remove(self[orderNum])
            super(Vertex.Emitters,self).__setitem__(orderNum,edge)
            if not self._vertex in edge.sources:
                edge.sources.append(self._vertex)


 
    class Collectors(TypedDict):
        def __init__(self,vertex):
            super(Vertex.Collectors,self).__init__(int,Edge)
            self._vertex = vertex
        
        def __setitem__(self,orderNum,edge):
#             if orderNum in self.keys() and self.values().count(self[orderNum]) == 1:
#                 print "removing only occurance of "
#                 edge.sinks.remove(self[orderNum])
            super(Vertex.Collectors,self).__setitem__(orderNum,edge)
            if not self._vertex in edge.sources:
                edge.sinks.append(self._vertex)

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


    class Sources(TypedList):
        def __init__(self,edge):
            super(Edge.Sources,self).__init__(Vertex)
            self._edge = edge
        
        def __checkForValue(self,vertex):
            typecheck(vertex,Vertex,"vertex")
            if vertex in self: 
                raise Exception("List already contains the value being set",vertex)
            if not self._edge in vertex.emitters.values():
                raise Exception("Edge must be added to vertex using Vertex.emitters first")

        def __setitem__(self,index,vertex):
            self.__checkForValue(vertex)
            super(Edge.Sources,self).__setitem__(index,vertex)

        def insert(self,index,vertex):
            self.__checkForValue(vertex)
            super(Edge.Sources,self).insert(index,vertex)

        def append(self,vertex):
            self.__checkForValue(vertex)
            super(Edge.Sources,self).append(vertex)

    class Sinks(TypedList):
        def __init__(self,edge):
            super(Edge.Sinks,self).__init__(Vertex)
            self._edge = edge
        
        def __checkForValue(self,vertex):
            typecheck(vertex,Vertex,"vertex")
            if vertex in self: 
                raise Exception("List already contains the value being set",vertex)
            if not self._edge in vertex.collectors.values():
                raise Exception("Edge must be added to vertex using Vertex.collectors first")

        def __setitem__(self,index,vertex):
            self.__checkForValue(vertex)
            super(Edge.Sinks,self).__setitem__(index,vertex)

        def insert(self,index,vertex):
            self.__checkForValue(vertex)
            super(Edge.Sinks,self).insert(index,vertex)

        def append(self,vertex):
            self.__checkForValue(vertex)
            super(Edge.Sinks,self).append(vertex)


