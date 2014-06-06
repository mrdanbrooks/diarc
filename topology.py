#!/usr/bin/python

from util import *

class Topology(object):
    def __init__(self):
        self.vertices = TypedList(Vertex)
        self.edges = TypedList(Edge)

    def getVertexByIndex(self,vertexIndex):
        """ get the vertex by its index value (not position in list) """
#         print "Looking for index",vertexIndex
        idxlist = [v.index for v in self.vertices]
        try: 
            return self.vertices[idxlist.index(vertexIndex)]
        except:
            raise Exception("Could not find vertex with index %d in topology"%vertexIndex)


class Vertex(object):
    def __init__(self,topology,index):
        typecheck(topology,Topology,"topology")
        typecheck(index,int,"index")
        self._topology = topology
        self._emitters = dict() # TypedList(Edge)
        self._collectors = dict() # TypedList(Edge)
        self.index = index

        # Add to Topology
        # Check that this vertex has a unique index
        if index in [v.index for v in self._topology.vertices]:
            raise Exception("Vertex with same index already exists")
        self._topology.vertices.append(self)

    def emitters(self,index=None):
        if index is None:
            return self._emitters.values()
        return self._emitters[index]

    def collectors(self,index=None):
        if index is None:
            return self._collectors.values()
        return self._collectors[index]
        
class Edge(object):
    def __init__(self,topology,altitude):
        typecheck(topology,Topology,"topology")
        typecheck(altitude,int,"altitude")
        self._topology = topology
        self._sources = dict() #TypedList(Vertex)
        self._sinks = dict() #TypedList(Vertex)
        self.altitude = altitude

        # Add to Topology
        # Check that this edge has a unique altitude
        if altitude in [e.altitude for e in self._topology.edges]:
            raise Exception("Edge with same altitude already exists!")
        self._topology.edges.append(self)

    def sources(self,index=None):
        if index is None:
            return self._sources.values()
        return self._sources[index]

    def sinks(self,index=None):
        if index is None:
            return self._sinks.values()
        return self._sinks[index]

    def addSource(self,vertex):
        typecheck(vertex,Vertex,"vertex")
        self._sources[vertex.index] = vertex
        vertex._emitters[self.altitude] = self

    def addSink(self,vertex):
        typecheck(vertex,Vertex,"vertex")
        self._sinks[vertex.index] = vertex
        vertex._collectors[self.altitude] = self
        
