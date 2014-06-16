from topology import *

class RosSystemGraph(Topology):
    def __init__(self):
        super(RosSystemGraph,self).__init__()
        # Renaming these things just for convenience
        self.nodes = self.vertices
        self.topics = self.edges

    def nextFreeNodeIndex(self):
        """ returns the next available node index """
        return max(self.blocks.keys())+1 if len(self.blocks)>0 else 0
        
class Node(Vertex):
    def __init__(self,rsg):
        typecheck(rsg,RosSystemGraph,"rsg")
        super(Node,self).__init__(rsg)

        # dumb placement - just get the next free index
        self.block.index = rsg.nextFreeNodeIndex()

        self.publishers = self.sources
        self.subscribers = self.sinks

class Topic(Edge):
    def __init__(self,rsg):
        typecheck(rsg,RosSystemGraph,"rsg")
        super(Topic,self).__init__(rsg)
        self.publishers = self.sources
        self.subscribers = self.sinks
        self.msgType = None

class Publisher(Source):
    def __init__(self,rsg,node,topic):
        typecheck(rsg,RosSystemGraph,"rsg")
        typecheck(node,Node,"node")
        typecheck(topic,Topic,"topic")
        super(Publisher,self).__init__(rsg,node,topic)
        self.bandwidth = None
        self.msgType = None

class Subscriber(Sink):
    def __init__(self,rsg,node,topic):
        typecheck(rsg,RosSystemGraph,"rsg")
        typecheck(node,Node,"node")
        typecheck(topic,Topic,"topic")
        super(Subscriber,self).__init__(rsg,node,topic)
        self.bandwidth = None
        self.msgType = None


if __name__ == "__main__":
    ros = RosSystemGraph()
    joystick = Node(ros)
    velocity = Topic(ros)

