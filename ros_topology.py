from topology import *

class RosSystemGraph(Topology):
    def __init__(self):
        super(RosSystemGraph,self).__init__()
        # Renaming these things just for convenience
        self.nodes = self.vertices
#         self.topics = self.edges

    @property
    def topics(self):
        return dict(filter(lambda x: None not in x[0], [((topic.name,topic.msgType),topic) for topic in self.edges]))


    def nextFreeNodeIndex(self):
        """ returns the next available node index """
        return max(self.blocks.keys())+1 if len(self.blocks)>0 else 0
    
    def nextFreeAltitudes(self):
        """ returns a 2-tuple of (posAltitude,negAltitude) of the avaliable altitudes """
        altitudes = [band.altitude for band in self.bands.values()] + [0]
        return (max(altitudes)+1,min(altitudes)-1)



class Node(Vertex):
    def __init__(self,rsg):
        typecheck(rsg,RosSystemGraph,"rsg")
        super(Node,self).__init__(rsg)

        # dumb placement - just get the next free index
        self.block.index = rsg.nextFreeNodeIndex()

        self.name = None
        self.location = None
        self.pid = None
        self.publishers = self.sources
        self.subscribers = self.sinks

class Topic(Edge):
    def __init__(self,rsg):
        typecheck(rsg,RosSystemGraph,"rsg")
        super(Topic,self).__init__(rsg)
        
        # Dumb placement - just get the enxt free altitudes
        self.posBand.altitude,self.negBand.altitude = rsg.nextFreeAltitudes()
        self.posBand.rank = self.posBand.altitude
        self.negBand.rank = self.posBand.altitude

        self.name = None
        self.msgType = None

        self.publishers = self.sources
        self.subscribers = self.sinks

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

        self.topic = self.edge
        self.node = self.vertex

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

        self.topic = self.edge
        self.node = self.vertex


if __name__ == "__main__":
    ros = RosSystemGraph()
    joystick = Node(ros)
    velocity = Topic(ros)

