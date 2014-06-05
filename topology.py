#!/usr/bin/python

import xml.etree.ElementTree as ET
import xml.dom.minidom
from util import *

# t = Topology()
# v1 = Vertex(t,1)
# e1 = Edge(t,1) 
# v1.addEmitter(e1)

class Topology(object):
    def __init__(self):
        self._vertices = dict()     # 'vertex._class':Vertex
        self._edges = dict()        # 'edge._class':Edge

    def vertices(self):
        """ returns the list of vertices in index order """
        ret = list()
        for v in self._vertices.values():
            index = v._index
            # Expand list size if necessary
            print "vertex %s has index %d, current list size = %d"%(v._class,index,len(ret))
            while index >= len(ret):
                print "expanding list"
                ret.append(None)
                print "New size is %d"%len(ret)
            # Check index is not already occupied
            if not ret[index] is None:
                return Exception("Index %d already in use!"%index)
            # Insert the value at the index
            ret[index] = v
        # Check that there are no "None" values in the list
        if None in ret:
            raise Exception("Vertex list has holes in it!") # if this happens, maybe you are skipping indexes
        return ret

    def edges(self):
        """ returns the list of edges in rank order """
        ret = list()
        for e in self._edges.values():
            rank = e._rank
            # Expand list size if necessary
            print "edge %s has rank %d, current list size  = %d"%(e._class,rank,len(ret))
            while rank >= len(ret):
                print "expanding list"
                ret.append(None)
                print "new size is %d"%len(ret)
            # Check that rank is not already occupied
            if not ret[rank] is None:
                return Exception("Rank %d already in use!"%rank)
            # Insert value 
            ret[rank] = e
        if None in ret:
            raise Exception("Edge ranks have hole in them!")
        return ret

    def _addVertex(self,vertex):
        """ Used by Vertex.__init__() to add itself to the topology """
        typecheck(vertex,Vertex,"vertex")
        for v in self._vertices.values():
            # Make sure new vertex has unique class
            if v._class == vertex._class:
                raise Exception("Vertex with _class %r already exists"%vertex._class)
            # Make sure new vertex has unique index
            if v._index == vertex._index:
                raise Exception("Vertex with index %d already exists"%vertex._index)
        # Add the vertex to the list
        self._vertices[vertex._class] = vertex
        
        #TODO: Link connections
        print "added vertex '%s' to topology with index %d"%(vertex._class,vertex._index)

    def _addEdge(self,edge):
        """ Used by Edge.__init__() to add itself to the topology """
        typecheck(edge,Edge,"edge")

        for e in self._edges.values():
            # Make sure new edge has unique class
            if e._class == edge._class:
                raise Exception("Edge with _class %r already exists"%edge._class)
            # Make sure new edge has unique rank
            if e._rank == edge._rank:
                raise Exception("Edge with _rank %r already exists"%edge._rank)
            # Make sure new edge has unique altitudes
            if not edge.pAltitude is None and e.pAltitude == edge.pAltitude:
                raise Exception("Edge with pAltitude %d already exists"%edge.pAltitude)
            if not edge.nAltitude is None and e.nAltitude == edge.nAltitude:
                raise Exception("Edge with nAltitude %d already exists"%edge.nAltitude)

        # Add the edge to the list
        self._edges[edge._class] = edge

class Vertex(object):
    def __init__(self,topology,_class,index,caption=None,seperation=None):
        typecheck(topology,Topology,"topology")
        self._topology = topology
        print "New vertex:",_class,index,seperation,caption
        self._index = index           # 0-indexed from left horizontal offset
        self._seperation = seperation or 2 # Seperation between Collectors and Emitters
        self._class = _class
        self.emitters = TypedList(Connection)
        self.collectors = TypedList(Connection)
        self._caption = caption or ""

        print "Created",self._class,self._index,self._seperation,self._caption

        # Add Vertex to topology
        self._topology._addVertex(self)


class Connection(object):
    def __init__(self,topology,_class,width=None):
        typecheck(topology,Topology,"topology")
        self._class = _class 
        self._width = width or 1
        typecheck(self._width,int,"width")

class Edge(object):
    """ Represents an Edge Object. """
    def __init__(self,topology,_class,rank=None,width=None,caption=None,pAltitude=None,nAltitude=None):
        typecheck(topology,Topology,"topology")
        self._topology = topology
        self._class = _class
        self._rank = rank or -1
        typecheck(self._rank,int,"rank")
        self._width = width or 1
        typecheck(self._width,int,"width")
        self._caption = caption or ""
        typecheck(self._caption,str,"caption")
        self.pAltitude = pAltitude 
        self.nAltitude = nAltitude
        if not pAltitude is None:
            typecheck(pAltitude,int,"pAltitude")
            if pAltitude <= 0:
                raise Exception("pAltitude must be > 0")
        if not nAltitude is None:
            typecheck(nAltitude,int,"nAltitude")
            if nAltitude >= 0:
                raise Exception("nAltitude must be < 0")
        # Sanity Check
        # TODO: Check that rank is unique
        if not self._rank >= 0: raise Exception("Edge rank must be >= 0, got %r"%self._rank)
        if not self._width >= 0: raise Exception("Edge width must be >=0, got %r"%self._width)
            
        # add Edge to the topology
        self._topology._addEdge(self)









def parseFile(filename):
    return parseTree(ET.parse(filename))
    
def parseString(data):
    return parseTree(ET.fromstring(data))

def parseTree(tree):
    # Get XML Tree root and initialize topology
    root = tree.getroot()
    t = Topology()
    
    # Populate Vertices
    vertices = root.find("vertices").findall("vertex")
    print "Num Vertices Detected: %d"%len(vertices)
    for vertex in vertices:
        _class = vertex.find("class").text.strip()
        index = int(vertex.find("index").text.strip())
        caption = vertex.find("caption").text.strip()
        if index is None:
            raise Exception()
        v = Vertex(t,_class,index,caption)

        # Registers Emitters and Collectors
        emitters = vertex.find("emitters").findall("connection")
        for connection in emitters:
            _class = connection.find("class").text.strip()
            width = int(connection.find("width").text.strip())
            v.emitters.append(Connection(v._topology,_class,width))

        collectors = vertex.find("collectors").findall("connection")
        for connection in collectors:
            _class = connection.find("class").text.strip()
            width = int(connection.find("width").text.strip())
            v.collectors.append(Connection(v._topology,_class,width))

    # Populate Edges
    edges = root.find("edges").findall("edge")
    print "Num Edges Detected: %d"%len(edges)
    for edge in edges:
        _class = edge.find("class").text.strip()
        rank = int(edge.find("rank").text.strip())
        caption = edge.find("caption").text.strip()
        width = int(edge.find("width").text.strip())
        # Get altitudes
        pAltitude, nAltitude = None, None
        try: pAltitude = int(edge.find("altitudes").find("positive").text.strip())
        except: pass
        try: nAltitude = int(edge.find("altitudes").find("negative").text.strip())
        except: pass
        print "Edge %r p=%r n=%r"%(_class,pAltitude,nAltitude)
        e = Edge(t,_class,rank,width,caption,pAltitude,nAltitude)


    return t


# Search children of ETree 
def find_element_by_attribute(root,elementname,attribname,attribval):
    element_list = root.findall(elementname)
    if element_list is None:
        raise Exception("No Elements of name %s found"%elementname)
    for tmp in element_list:
        try:
            if tmp.attrib[attribname] == attribval:
                return tmp
        except:
            raise Exception("Element %s has not attribute %s"%(elementname,attribname))
    raise Exception("Could not find %s with %s=%s"%(elementname,attribname,attribval))


def xmlify(root):
    # Split continuous string by newlines
    content = xml.dom.minidom.parseString(ET.tostring(root)).toprettyxml().split("\n")
    # Remove right hand whitespace
    content = [str(l).rstrip() for l in content]
    # Filter Blank lines
    content = filter(lambda x: not x == "",content)
    # Repack as a single string
    content = "\n".join(content)
    return content


if __name__ == "__main__":
    parseFile('example.xml')
