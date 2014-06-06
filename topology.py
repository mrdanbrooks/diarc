#!/usr/bin/python

from util import *

class Topology(object):
    def __init__(self):
        self.vertices = TypedList(Vertex)
        self.edges = TypedList(Edge)

    def getVertexByIndex(self,vertexIndex):
        idxlist = [v.index for v in self.vertices]
        return self.vertices[idxlist.index(vertexIndex)]

class Vertex(object):
    def __init__(self,topology,index):
        typecheck(topology,Topology,"topology")
        typecheck(index,int,"index")
        self._topology = topology
        self._emitters = TypedList(Edge)
        self._collectors = TypedList(Edge)
        self.index = index

        # Add to Topology
        # Check that this vertex has a unique index
        if index in [v.index for v in self._topology.vertices]:
            raise Exception("Vertex with same index already exists")
        self._topology.vertices.append(self)
        
class Edge(object):
    def __init__(self,topology,altitude):
        typecheck(topology,Topology,"topology")
        typecheck(altitude,int,"altitude")
        self._topology = topology
        self._sources = TypedList(Vertex)
        self._sinks = TypedList(Vertex)
        self.altitude = altitude

        # Add to Topology
        # Check that this edge has a unique altitude
        if altitude in [e.altitude for e in self._topology.edges]:
            raise Exception("Edge with same altitude already exists!")
        self._topology.edges.append(self)

    def addSource(self,vertex):
        typecheck(vertex,Vertex,"vertex")
        self._sources.append(vertex)
        vertex._emitters.append(self)

    def addSink(self,vertex):
        typecheck(vertex,Vertex,"vertex")
        self._sinks.append(vertex)
        vertex._collectors.append(self)
        
