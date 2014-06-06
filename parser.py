import xml.etree.ElementTree as ET
import xml.dom.minidom
from topology import *

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
        index = int(vertex.attrib['index'].strip())
        v = Vertex(t,index)

    # Populate Edges
    edges = root.find("edges").findall("edge")
    print "Num Edges Detected: %d"%len(edges)
    for edge in edges:
        altitude = int(edge.attrib["altitude"].strip())
        e = Edge(t,altitude)
        for src in edge.findall("source"):
            index = int(src.text.strip())
            e.addSource(t.getVertexByIndex(index))
        for sink in edge.findall("sink"):
            index = int(src.text.strip())
            e.addSink(t.getVertexByIndex(index))

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


