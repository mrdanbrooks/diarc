# [db] dan@danbrooks.net
#
# diarc topology data structures for ROS
# This renames some things into ROS terminology to be more conveient, and also
# adds some attributes we want to track. 
#
# Renaming Looks like this
#   Vertex = Node
#   Edge = Topic
#   Sink = Subscriber
#   Source = Publisher
#
from topology import *
import rosgraph
import rosnode
QUIET_NAMES = ['/rosout']

class RosSystemGraph(Topology):
    def __init__(self):
        super(RosSystemGraph,self).__init__()

    @property
    def nodes(self):
        return dict([(v.name,v) for v in self.vertices])

    @property
    def topics(self):
        return dict(filter(lambda x: None not in x, [(topic.name,topic) for topic in self.edges]))

    def nextFreeNodeIndex(self):
        """ returns the next available node index """
        return max(self.blocks.keys())+1 if len(self.blocks)>0 else 0
    
    def nextFreeAltitudes(self):
        """ returns a 2-tuple of (posAltitude,negAltitude) of the avaliable altitudes """
        altitudes = [band.altitude for band in self.bands.values()] + [0]
        return (max(altitudes)+1,min(altitudes)-1)



class LiveRosSystemGraph(RosSystemGraph):
    def __init__(self):
        super(LiveRosSystemGraph,self).__init__()
        self._master = rosgraph.Master('/RosSystemGraph')

    def update(self):
        print "*** UPDATING GRAPH ***"
        # Query master and compile a list of all published topics and their types
        allCurrentTopics = self._master.getPublishedTopics('/')
        allCurrentTopicNames = [x[0] for x in allCurrentTopics]
        # Get all the topics we currently know about
        rsgTopics = self.topics

        # Remove any topics from Ros System Graph not currently known to master
        for topic in rsgTopics.values():
            if topic.name not in allCurrentTopicNames:
                print "Removing Topic",topic.name, "not found in ",allCurrentTopicNames
                topic.release()

        # Add any topics not currently in the Ros System Graph
        for topicName, topicType in allCurrentTopics:
            if topicName not in rsgTopics: # and topicName not in QUIET_NAMES:
                topic = Topic(self,topicName,topicType)
#                 topic.posBand.visual = self.visualBandType()

        # Compile a list of node names
        allCurrentNodes = rosnode.get_node_names()
        # Get all nodes we currently know about
        rsgNodes = self.nodes

        # Remove any nodes from RosSystemGraph not currently known to master
        for node in rsgNodes.values():
            if node.name not in allCurrentNodes:
                print "Removing Node",node.name, "not found in ",allCurrentNodes
                node.release()

        # Add any nodes not currently in the Ros System Graph
        for name in allCurrentNodes:
            if name not in rsgNodes: # and name not in QUIET_NAMES:
                node = Node(self,name)
                try:
                    node.location = self._master.lookupNode(name)
                except socket.error:
                    raise Exception("Unable to communicate with master!")

        # Check for added or removed connections
        systemState = self._master.getSystemState()
        # Process publishers
        for topicName, publishersList in systemState[0]:
            if topicName in QUIET_NAMES: 
                continue
            rsgPublishers = self.topics[topicName].publishers
            # Remove publishers that don't exist anymore
            for publisher in rsgPublishers:
                if publisher.node.name not in publishersList:
                    publisher.release()
            # Add publishers taht are not yet in the RosSystemGraph
            for nodeName in publishersList:
                if nodeName not in [pub.node.name for pub in rsgPublishers]:
                    publisher = Publisher(self,self.nodes[nodeName],self.topics[topicName])

        # Process subscribers
        for topicName, subscribersList in systemState[1]:
            if topicName in QUIET_NAMES: 
                continue
            rsgSubscribers = self.topics[topicName].subscribers
            # Remove subscribers that don't exist anymore
            for subscriber in rsgSubscribers:
                if subscriber.node.name not in subscribersList:
                    subscriber.release()
            # Add subscriber taht are not yet in the RosSystemGraph
            for nodeName in subscribersList:
                if nodeName not in [sub.node.name for sub in rsgSubscribers]:
                    subscriber = Subscriber(self,self.nodes[nodeName],self.topics[topicName])
        print "*** FINISHED UPDATING ***"







class Node(Vertex):
    def __init__(self,rsg,name=None):
        typecheck(rsg,RosSystemGraph,"rsg")
        super(Node,self).__init__(rsg)

        # dumb placement - just get the next free index
        self.block.index = rsg.nextFreeNodeIndex()

        self.name = name
        self.location = None
        self.pid = None

    @property
    def publishers(self):
        # NOTE: This must be a property function (instead of just saying 
        # self.publishers = self.sources in the constructor) because self.sources
        # just returns a static list once, and we need this to be dynamically
        # queried every time we ask. This is because Vertex.sources and Edge.sources
        # are just syntax sugar for functions that are being called.
        return self.sources

    @property
    def subscribers(self):
        return self.sinks


class Topic(Edge):
    def __init__(self,rsg,name=None,msgType=None):
        typecheck(rsg,RosSystemGraph,"rsg")
        super(Topic,self).__init__(rsg)
        
        # Dumb placement - just get the enxt free altitudes
        self.posBand.altitude,self.negBand.altitude = rsg.nextFreeAltitudes()
        self.posBand.rank = self.posBand.altitude
        self.negBand.rank = self.posBand.altitude

        self.name = name
        self.msgType = msgType

    @property
    def publishers(self):
        # NOTE: See note on Node class about why this MUST be a property.
        return self.sources

    @property
    def subscribers(self):
        # NOTE: See note on Node class about why this MUST be a property.
        return self.sinks




class Publisher(Source):
    def __init__(self,rsg,node,topic):
        typecheck(rsg,RosSystemGraph,"rsg")
        typecheck(node,Node,"node")
        typecheck(topic,Topic,"topic")
        super(Publisher,self).__init__(rsg,node,topic)
        # Dumb placement
        self.snap.order = max(filter(lambda x: isinstance(x,int), [pub.snap.order for pub in node.publishers] + [-1]))+1

        self.bandwidth = None
        self.msgType = None

    @property
    def topic(self):
        # NOTE: See note on Node class about why this MUST be a property.
        return self.edge

    @property
    def node(self):
        # NOTE: See note on Node class about why this MUST be a property.
        return self.vertex

class Subscriber(Sink):
    def __init__(self,rsg,node,topic):
        typecheck(rsg,RosSystemGraph,"rsg")
        typecheck(node,Node,"node")
        typecheck(topic,Topic,"topic")
        super(Subscriber,self).__init__(rsg,node,topic)

        # Dumb placement
        self.snap.order = max(filter(lambda x: isinstance(x,int), [sub.snap.order for sub in node.subscribers] + [-1]))+1

        self.bandwidth = None
        self.msgType = None

    @property
    def topic(self):
        # NOTE: See note on Node class about why this MUST be a property.
        return self.edge

    @property
    def node(self):
        # NOTE: See note on Node class about why this MUST be a property.
        return self.vertex



if __name__ == "__main__":
    ros = RosSystemGraph()
    joystick = Node(ros)
    velocity = Topic(ros)

