from ros_topology import *

import rosgraph
import rosnode

QUIET_NAMES = ['/rosout']

# class RosTopologyGenerator(object):
#     def __init__(self):
def rsg_generator():
    # start blank topology
    rsg = RosSystemGraph()

    # Connect to the ROS master
    master = rosgraph.Master('/RosTopologyGenerator')

    # Compile a list of all published topics and their types
    for topicName, topicType in master.getPublishedTopics('/'):
        if topicName not in rsg.topics and topicName not in QUIET_NAMES:
            topic = Topic(rsg,topicName,topicType)

    # Compile a list of node names
    for name in rosnode.get_node_names():
        node = Node(rsg,name)
        try:
            node.location = master.lookupNode(name)
        except socket.error:
            raise Exception("Unable to communicate with master!")

    systemState = master.getSystemState()
    # Process publishers
    for topicName, publishersList in systemState[0]:
        if topicName in QUIET_NAMES: continue
        for nodeName in publishersList:
            publisher = Publisher(rsg,rsg.nodes[nodeName],rsg.topics[topicName])
    # Process subscribers
    for topicName, subscribersList in systemState[1]:
        if topicName in QUIET_NAMES: continue
        for nodeName in subscribersList:
            subscriber = Subscriber(rsg,rsg.nodes[nodeName],rsg.topics[topicName])

    return rsg


class RsgUpdater(object):
    def __init__(self):
        # Connect to the ROS master
        self._master = rosgraph.Master('/RosTopologyGenerator')

    def update(rsg):
        typecheck(rsg,RosSystemGraph,"rsg")
        # Query master and compile a list of all published topics and their types
        allCurrentTopics = self._master.getPublishedTopics('/')

        # Add any topics not currently in the Ros System Graph
        for topicName, topicType in allCurrentTopics:
            if topicName not in rsg.topics and topicName not in QUIET_NAMES:
                topic = Topic(rsg,topicName,topicType)




