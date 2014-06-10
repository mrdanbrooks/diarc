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
        self.emitters = Vertex.Emitters(self)       # orderNum: [edge, ...]
        self.collectors = Vertex.Collectors(self)   # orderNum: edge
        self.index = index

        # Add to Topology
        # Check that this vertex has a unique index
        if index in self._topology.vertices:
            raise Exception("Vertex with same index already exists")
        self._topology.vertices[index] = self

    class Emitters(TypedDict):
        def __init__(self,vertex):
            super(Vertex.Emitters,self).__init__(int,EdgePair)
            self._vertex = vertex
        
        def __getitem__(self,orderNum):
            # The edge pair will return the one correct value, or both
            return super(Vertex.Emitters,self).__getitem__(orderNum).get()

        def values(self):
            values = list()
            for x in super(Vertex.Emitters,self).values():
                val = x.get()
                if isinstance(val,list):
                    values+=val
                else:
                    values.append(val)
            return values

        def __setitem__(self,orderNum,edge):
#             if orderNum in self.keys() and self.values().count(self[orderNum]) == 1:
#                 print "removing only occurance of ",self[orderNum]
#                 edge.sources.remove(self[orderNum])

            # Initialize the list if this is the first item
            if not orderNum in self.keys():
                super(Vertex.Emitters,self).__setitem__(orderNum,EdgePair())

            # Inset the value into the Edge pair
            super(Vertex.Emitters,self).__getitem__(orderNum).set(edge)
            if not self._vertex in edge.sources:
                edge.sources.append(self._vertex)

    class Collectors(TypedDict):
        def __init__(self,vertex):
            super(Vertex.Collectors,self).__init__(int,EdgePair)
            self._vertex = vertex
        
        def __getitem__(self,orderNum):
            return super(Vertex.Collectors,self).__getitem(orderNum).get()

        def values(self):
            values = list()
            for x in super(Vertex.Collectors,self).values():
                val = x.get()
                if isinstance(val,list):
                    values+=val
                else:
                    values.append(val)
            return values

        def __setitem__(self,orderNum,edge):
            # Initialize list if empty
            if not orderNum is self.keys():
                super(Vertex.Collectors,self).__setitem__(orderNum,EdgePair())

            # Insert the value
            super(Vertex.Collectors,self).__getitem__(orderNum).set(edge)
            if not self._vertex in edge.sources:
                edge.sinks.append(self._vertex)
 
#     # Old Style Emitter/Collector - was much cleaner but didn't let you have
#     # two values (positive and negative) for a single dictionary key :( 
#     class Collectors(TypedDict):
#         def __init__(self,vertex):
#             super(Vertex.Collectors,self).__init__(int,Edge)
#             self._vertex = vertex
#         
#         def __setitem__(self,orderNum,edge):
#             super(Vertex.Collectors,self).__setitem__(orderNum,edge)
#             if not self._vertex in edge.sources:
#                 edge.sinks.append(self._vertex)

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
                raise Exception("Edge must be added to vertex using Vertex.emitters first %r"%vertex.emitters.values())

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


class EdgePair(object):
    """ A pair of two edges, one with positive altitude, one with negative"""
    # TODO: Should I enfore matching ranks?
    def __init__(self):
        self.pAltitude = None
        self.nAltitude = None

    def get(self):
        if isinstance(self.pAltitude ,Edge) and not isinstance(self.nAltitude,Edge):
            return self.pAltitude
        elif not isinstance(self.pAltitude ,Edge) and isinstance(self.nAltitude,Edge):
            return self.nAltitude
        elif isinstance(self.pAltitude ,Edge) and isinstance(self.nAltitude,Edge):
            return [self.pAltitude,self.nAltitude]
        else:
            raise Exception("wow")

    def set(self,edge):
        """ Automatically track positive and negative edges """ 
        typecheck(edge,Edge,"edge")
        if edge.altitude >= 1:
            self.pAltitude = edge
        elif edge.altitude <= -1:
            self.nAltitude = edge
        else:
            raise Exception("Invalid Edge altitude %d"%edge.altitude)


