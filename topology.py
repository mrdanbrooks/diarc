#!/usr/bin/python

import xml.etree.ElementTree as ET
import xml.dom.minidom

# t = Topology()
# v1 = Vertex(t,1)
# e1 = Edge(t,1) 
# v1.addEmitter(e1)

class Topology(object):
    def __init__(self):
        self._vertices = dict()     # 'vertex._class':Vertex
        self._edges = dict()        # 'edge._class':Edge

    def vertices(self):
        """ generates the list of vertices in index order """
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
        return ret

    def _addVertex(self,vertex):
        typecheck(vertex,Vertex,"vertex")
        for v in self._vertices.values():
            # Make sure new vertex has unique class
            if v._class == vertex._class:
                raise Exception("Vertex with _class %r already exists"%vertex._class)
            # Make sure new vertex has unique index
            if v._class == vertex._index:
                raise Exception("Vertex with index %d already exists"%vertex._index)
        # Add the vertex to the list
        self._vertices[vertex._class] = vertex
        
        #TODO: Link connections
        print "added vertex '%s' to topology with index %d"%(vertex._class,vertex._index)

    def _addEdge(self,edge):
        typecheck(edge,Edge,"edge")

        # Add the edge to the list
        self._edges[edge._class] = edge

class Vertex(object):
    def __init__(self,topology,_class,index,seperation=None,caption=None):
        typecheck(topology,Topology,"topology")
        self._topology = topology
        print "New vertex:",_class,index,seperation,caption
        self._index = index           # 0-indexed from left horizontal offset
        self._seperation = seperation or 2 # Seperation between Collectors and Emitters
        self._class = _class
        self._emitters = list()
        self._collectors = list()
        self._caption = caption or ""

        print "Created",self._class,self._index,self._seperation,self._caption

        # Add Vertex to topology
        self._topology._addVertex(self)

    def getIndex(self):
        return self._index

    def setIndex(self,value):
        pass
        
class Connection(object):
    def __init__(self,topology,rank=None,width=None):
        typecheck(topology,Topology,"topology")
        self._rank = rank or -1
        typecheck(self._rank,int,"rank")
        self._width = width or 1
        typecheck(self._width,int,"width")

class Edge(object):
    def __init__(self,topology,_class,rank=None,width=None,altitudes=None,caption=None):
        typecheck(topology,Topology,"topology")
        self._class = _class
        self._rank = rank or -1
        typecheck(self._rank,int,"rank")
        self._width = width or 1
        typecheck(self._width,int,"width")
        self._caption = caption or ""
        typecheck(self._caption,str,"caption")
        self._altitudes = altitudes or list()
        typecheck(self._altitudes,list,"altitudes")
        # Sanity Check
        # TODO: Check that rank is unique
        if not self._rank >= 0: raise Exception("Edge rank must be >= 0, got %r"%self._rank)
        if not self._width >= 0: raise Exception("Edge width must be >=0, got %r"%self._width)
        if not len(self._altitudes) > 0 and len(self._altitudes) <= 2: raise Exception()
            

def typecheck(obj,objtype,varname=None):
    """ Checks the type of obj against class objtype, optionally pass in a varname for debug purposes """
    varname = None or ""
    if not isinstance(obj,objtype):
        raise Exception("%s must be of type '%s', got %r"%(varname, objtype.__name__, obj.__class__.__name__))


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
        if index is None:
            raise Exception()
        v = Vertex(t,_class,index)

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
