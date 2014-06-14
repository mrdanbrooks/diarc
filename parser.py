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
 
    # Populate Edges
    edges = root.find("edges").findall("edge")

    print "Num Edges Detected:",len(edges)

    for edge in edges:
        altitude = int(edge.attrib["altitude"].strip())
        rank = int(edge.attrib["rank"].strip())
        matches = filter(lambda x: x.rank==rank,t.bands)
        if len(matches) <= 0:
            print "creating new edge",
            e = Edge(t)
            print e
        else:
            print "found %d matches"%len(matches)
            e = matches[0].edge
        band = e.posBand if altitude > 0 else e.negBand
        band.altitude = altitude
        band.rank = rank

   
    # Populate Vertices
    vertices = root.find("vertices").findall("vertex")
    print "Num Vertices Detected: %d"%len(vertices)
    for vertex in vertices:
        index = int(vertex.attrib['index'].strip())
        print "Creating Vertex with index=",index,
        v = Vertex(t)
        print v
        v.block.index = index

        # Make edge connections to this vertex
        for sink in vertex.find("collector").findall("sink"):
            order = int(sink.attrib["order"].strip())
            altitude = int(sink.attrib["altitude"].strip())
            e = t.findBand(altitude).edge
            if v in [s.vertex for s in e.sinks]:
                print "Existing Vertex found!"
            else:
                tmp = Sink(t,v,e)
                tmp.snap.order = order
                print "Creating sink with order=",order,"altitude=",altitude,tmp

        for source in vertex.find("emitter").findall("source"):
            order = int(source.attrib["order"].strip())
            altitude = int(source.attrib["altitude"].strip())
            e = t.findBand(altitude).edge
            if v in [src.vertex for src in e.sources]:
                print "Existing Vertex found"
            else:
                tmp = Source(t,v,e)
                tmp.snap.order = order
                print "Creating source with order=",order,"altitude=",altitude,tmp
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


