from ros_topology import *

import rosgraph
import rosnode

QUIET_NAMES = ['/rosout']

class RsgUpdater(object):
    def __init__(self):
        # Connect to the ROS master
        self._master = rosgraph.Master('/RosTopologyGenerator')
        self.visualBlockType = None
        self.visualBandType = None
        self.visualSnapType = None

    def update(self,rsg):
        print "*** UPDATING GRAPH ***"
        typecheck(rsg,RosSystemGraph,"rsg")
        # Query master and compile a list of all published topics and their types
        allCurrentTopics = self._master.getPublishedTopics('/')
        allCurrentTopicNames = [x[0] for x in allCurrentTopics]
        # Get all the topics we currently know about
        rsgTopics = rsg.topics

        # Remove any topics from Ros System Graph not currently known to master
        for topic in rsgTopics.values():
            if topic.name not in allCurrentTopicNames:
                print "Removing Topic",topic.name, "not found in ",allCurrentTopicNames
                topic.release()

        # Add any topics not currently in the Ros System Graph
        for topicName, topicType in allCurrentTopics:
            if topicName not in rsgTopics: # and topicName not in QUIET_NAMES:
                topic = Topic(rsg,topicName,topicType)
                topic.posBand.visual = self.visualBandType()

        # Compile a list of node names
        allCurrentNodes = rosnode.get_node_names()
        # Get all nodes we currently know about
        rsgNodes = rsg.nodes

        # Remove any nodes from RosSystemGraph not currently known to master
        for node in rsgNodes.values():
            if node.name not in allCurrentNodes:
                print "Removing Node",node.name, "not found in ",allCurrentNodes
                node.release()

        # Add any nodes not currently in the Ros System Graph
        for name in allCurrentNodes:
            if name not in rsgNodes: # and name not in QUIET_NAMES:
                node = Node(rsg,name)
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
            rsgPublishers = rsg.topics[topicName].publishers
            # Remove publishers that don't exist anymore
            for publisher in rsgPublishers:
                if publisher.node.name not in publishersList:
                    publisher.release()
            # Add publishers taht are not yet in the RosSystemGraph
            for nodeName in publishersList:
                if nodeName not in [pub.node.name for pub in rsgPublishers]:
                    publisher = Publisher(rsg,rsg.nodes[nodeName],rsg.topics[topicName])

        # Process subscribers
        for topicName, subscribersList in systemState[1]:
            if topicName in QUIET_NAMES: 
                continue
            rsgSubscribers = rsg.topics[topicName].subscribers
            # Remove subscribers that don't exist anymore
            for subscriber in rsgSubscribers:
                if subscriber.node.name not in subscribersList:
                    subscriber.release()
            # Add subscriber taht are not yet in the RosSystemGraph
            for nodeName in subscribersList:
                if nodeName not in [sub.node.name for sub in rsgSubscribers]:
                    subscriber = Subscriber(rsg,rsg.nodes[nodeName],rsg.topics[topicName])
        print "*** FINISHED UPDATING ***"
        return rsg




