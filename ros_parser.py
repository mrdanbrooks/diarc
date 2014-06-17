import xml.etree.ElementTree as ET
import xml.dom.minidom
from ros_topology import *

def parseFile(filename):
    return parseTree(ET.parse(filename))

def parseTree(tree):
    root = tree.getroot()
    
    ros = RosSystemGraph()

    for xmlNode in root.findall("node"):
        # Create new node
        n = Node(ros)
        n.name = xmlNode.attrib["name"].strip()
        n.location = xmlNode.attrib["location"].strip()
        n.pid = xmlNode.attrib["pid"].strip()

        # Setup Publishers and Subscribers
        # Before we can create a connection, we need to add the topic
        # to our SystemGraph. 
        for xmlTopic in xmlNode.find("topics")

    # Get Topics
    for topic in root.findall("topic"):
        t = Topic(ros)
        t.name = topic.attrib["name"].strip()
        t.msgType = topic.attrib["type"].strip()


    # Get Nodes
    nodes = root.findall("node")
    for node in root.findall("node"):
        n = Node(ros)
        n.name = node.attrib["name"].strip()

        for topic in node.find("topics").findall("publishes"):
            tName = topic.attrib["name"]
            tMsgType = topic.attrib["type"]
            Publisher(ros,n,ros.topics[(tName,tMsgType)])

    return ros
