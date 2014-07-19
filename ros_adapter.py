import rosgraph
import rosnode
QUIET_NAMES = ['/rosout','/tf']

from adapter import Adapter
# from ros_model import *
from ros_topology import *


class RosAdapter(Adapter):
    """ Implements the Adapter interface for the View and provides hooks for 
    populating and implementing the ros specific version of the topology.
    """

    def __init__(self,view):
        super(RosAdapter,self).__init__(RosSystemGraph(),view)
        self._topology.hide_disconnected_snaps = False
        self._master = rosgraph.Master('/RosSystemGraph')

        # These are caching lists so I can remember what I had last time I drew.
        # That way, if something becomes outdated, I have a thing to compare against.
        # These lists are updated at the end of _update_view()
        self._cached_block_item_indexes = list()
        self._cached_band_item_altitudes = list()
        self._cached_snap_item_snapkeys = list()


    def reorder_blocks(self,srcIdx,lowerIdx,upperIdx):
        """ reorders the index values of blocks and triggers the view to redraw.
        This also requires updating the corresponding block_items.
        """ 
        blocks = self._topology.blocks

        lastIdx = None
        currIdx = srcIdx
        # If we are moving to the right, lowerIdx is the target index.
        # Clear the dragged block's index, then shift all effected block
        # indices left.
        # NOTE: See issue #12
        if lowerIdx > srcIdx:
            while isinstance(currIdx,int) and currIdx < (upperIdx or lowerIdx+1): # In case upperIdx is None, use lower+1
                nextIdx = blocks[currIdx].rightBlock.index if blocks[currIdx].rightBlock else None
                blocks[currIdx].index = lastIdx
                print "%s -> %s"%(str(currIdx),str(lastIdx))
                lastIdx = currIdx
                currIdx = nextIdx
            assert lastIdx == lowerIdx, "%r %r"%(lastIdx,upperIdx)

        # If we are moving to the left, upperIdx is the target index.
        # Clear the dragged blocks index, then shift all effected blocks right
        elif upperIdx < srcIdx:
            while isinstance(currIdx,int) and currIdx > lowerIdx:
                nextIdx = blocks[currIdx].leftBlock.index if blocks[currIdx].leftBlock else None
                blocks[currIdx].index = lastIdx
                print "%s -> %s"%(str(currIdx),str(lastIdx))
                lastIdx = currIdx
                currIdx = nextIdx
            assert lastIdx == upperIdx, "%r %r"%(lastIdx,upperIdx)

        # Otherwise we are just dragging to the side a bit and nothing is 
        # really moving anywhere. Return immediately to avoid trying to give
        # the block a new index and unnecessary extra linking actions.
        else:
            print "No op!"
            return
        # Finally give the moved object its desired destination. Then make 
        # the TopologyWidget relink all the objects again.
        blocks[srcIdx].index = lastIdx
        self._update_view()


    def reorder_bands(self, srcAlt, lowerAlt, upperAlt):
        """ Reorders the altitude values of bands """
        bands = self._topology.bands

        lastAlt = None
        currAlt = srcAlt

        # If we are moving up, lowerAlt is the target altitude. 
        # Clear the dragged bands's altitude, then shift all effected bands
        # down. See issue #12
        if isinstance(lowerAlt,int) and lowerAlt > srcAlt:
            while isinstance(currAlt,int) and currAlt < (upperAlt or lowerAlt+1):
                tband = bands[currAlt].topBand
                nextAlt = tband.altitude if isinstance(tband,Band) else None
                bands[currAlt].altitude = lastAlt
                lastAlt = currAlt
                currAlt = nextAlt
            # Assertion check
            assert lastAlt == lowerAlt, "%r %r"%(lastAlt,lowerAlt)

        # If we are moving down, upperAlt is the target altitude.
        # Clear the dragged bands altitude, then shift all effected bands up.
        elif isinstance(upperAlt,int) and upperAlt <= srcAlt:
            while isinstance(currAlt,int) and currAlt > (lowerAlt or upperAlt-1):
                lband = bands[currAlt].bottomBand
                nextAlt = lband.altitude if isinstance(lband,Band) else None
                bands[currAlt].altitude = lastAlt
                lastAlt = currAlt
                currAlt = nextAlt
            # Assertion check
            assert lastAlt == upperAlt, "%r %r"%(lastAlt,upperAlt)

        else:
#             print "No op!"
            return

        # Finally, give the moved object its desired destination. Then make
        # the TopologyWidget relink all the objects again
        bands[srcAlt].altitude = lastAlt
        self._update_view()

    def reorder_snaps(self, blockIdx, container, srcIdx, lowerIdx, upperIdx):
        assert(container in ["emitter","collector"])
        block = self._topology.blocks[blockIdx]
        snaps = block.emitter if container == "emitter" else block.collector
        print snaps.keys()
        print "move snap",srcIdx,"between",lowerIdx,"and",upperIdx

        lastIdx = None
        currIdx = srcIdx
        # If we are moving to the right, lowerIdx is the target index.
        # Clear the dragged snaps's order, then shift all effected snap
        # indices left.
        # NOTE: see #12
        if lowerIdx > srcIdx:
            while isinstance(currIdx,int) and currIdx < (upperIdx or lowerIdx+1):
                nextIdx = snaps[currIdx].rightSnap.order if snaps[currIdx].rightSnap else None
                snaps[currIdx].order = lastIdx
                print "%s -> %s"%(str(currIdx),str(lastIdx))
                lastIdx = currIdx
                currIdx = nextIdx
            # Assertion check. TODO: Remove
            assert lastIdx == lowerIdx, "%r %r"%(lastIdx,lowerIdx)

        # If we are moving to the left, upperIdx is the target index.
        # Clear the dragged snaps order, then shift all effected snaps
        # indices right
        elif upperIdx < srcIdx:
            while isinstance(currIdx,int) and currIdx > lowerIdx:
                nextIdx = snaps[currIdx].leftSnap.order if snaps[currIdx].leftSnap else None
                snaps[currIdx].order = lastIdx
                print "%s -> %s"%(str(currIdx),str(lastIdx))
                lastIdx = currIdx
                currIdx = nextIdx
            # Assertion check. TODO remove
            assert lastIdx == upperIdx, "%r %r"%(lastIdx,upperIdx)

        # Otherwise we are just dragging to the side a bit and nothing is
        # really moving anywhere. Return immediately to avoid trying to
        # give the snap a new order and unnecessary extra linking actions.
        else:
            print "No op!"
            return

        # Finally give the moved object its desired destination. Then
        # make the TopologyWidget relink all the objects again.
        snaps[srcIdx].order = lastIdx
        self._update_view()



    def update_model(self):
        """ query the ros master for information about the state of the system """
        # Query master and compile a list of all published topics and their types
        allCurrentTopics = self._master.getPublishedTopics('/')
        allCurrentTopicNames = [x[0] for x in allCurrentTopics]
        # Get all the topics we currently know about
        rsgTopics = self._topology.topics

        # Remove any topics from Ros System Graph not currently known to master
        for topic in rsgTopics.values():
            if topic.name not in allCurrentTopicNames:
                print "Removing Topic",topic.name, "not found in ",allCurrentTopicNames
                topic.release()

        # Add any topics not currently in the Ros System Graph
        for topicName, topicType in allCurrentTopics:
            if topicName not in rsgTopics: # and topicName not in QUIET_NAMES:
                topic = Topic(self._topology,topicName,topicType)

        # Compile a list of node names
        allCurrentNodes = rosnode.get_node_names()
        # Get all nodes we currently know about
        rsgNodes = self._topology.nodes

        # Remove any nodes from RosSystemGraph not currently known to master
        for node in rsgNodes.values():
            if node.name not in allCurrentNodes:
                print "Removing Node",node.name, "not found in ",allCurrentNodes
                node.release()

        # Add any nodes not currently in the Ros System Graph
        for name in allCurrentNodes:
            if name not in rsgNodes: # and name not in QUIET_NAMES:
                node = Node(self._topology,name)
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
            rsgPublishers = self._topology.topics[topicName].publishers
            # Remove publishers that don't exist anymore
            for publisher in rsgPublishers:
                if publisher.node.name not in publishersList:
                    publisher.release()
            # Add publishers taht are not yet in the RosSystemGraph
            for nodeName in publishersList:
                if nodeName not in [pub.node.name for pub in rsgPublishers]:
                    publisher = Publisher(self._topology,self._topology.nodes[nodeName],self._topology.topics[topicName])

        # Process subscribers
        for topicName, subscribersList in systemState[1]:
            if topicName in QUIET_NAMES: 
                continue
            try:
                rsgSubscribers = self._topology.topics[topicName].subscribers
            except:
                print topicName,"not found in"
                continue
            # Remove subscribers that don't exist anymore
            for subscriber in rsgSubscribers:
                if subscriber.node.name not in subscribersList:
                    subscriber.release()
            # Add subscriber taht are not yet in the RosSystemGraph
            for nodeName in subscribersList:
                if nodeName not in [sub.node.name for sub in rsgSubscribers]:
                    subscriber = Subscriber(self._topology,self._topology.nodes[nodeName],self._topology.topics[topicName])

        self._update_view()





    def _update_view(self):
        """ updates the view - compute each items neigbors and then calls linking. """

        # Determine what items are in the model
        blocks = self._topology.blocks
        bands = self._topology.bands
        snaps = self._topology.snaps
        
        # Delete outdated BlockItems still in the view but no longer in the topology
        old_block_item_indexes = list(set(self._cached_block_item_indexes) - set(blocks.keys()))
        for index in old_block_item_indexes:
            self._view.remove_block_item(index)

        # Add new BlockItems for blocks in model that are not in view
        for index in blocks:
            if not self._view.has_block_item(index):
                self._view.add_block_item(index)

        # Update the BlockItem cache list
        self._cached_block_item_indexes = blocks.keys()

        # Delete outdated BandItems still in the view but not in the topology
        old_band_item_altitudes = list(set(self._cached_band_item_altitudes) - set(bands.keys()))
        for altitude in old_band_item_altitudes:
            self._view.remove_band_item(altitude)

        # Delete BandItems that exist, but are not being used, and add BandItems
        # that are being used, but are not yet in the view
        for altitude in bands:
            band = bands[altitude]
            isUsed = band.isUsed()
            if isUsed and not self._view.has_band_item(altitude):
                self._view.add_band_item(altitude,band.rank)
            elif not isUsed and self._view.has_band_item(altitude):
                self._view.remove_band_item(altitude)

        # Update the BandItem cache list
        self._cached_band_item_altitudes = bands.keys()

        # Delete outdated SnapItems still in the view but no longer in the topology
        old_snap_item_snapkeys = list(set(self._cached_snap_item_snapkeys) - set(snaps.keys()))
        for snapkey in old_snap_item_snapkeys:
            self._view.remove_snap_item(snapkey)

        # Delete SnapItems that exist, but are not being used, and add SnapItems
        # that are being used, but are not yet in the view
        for snapkey in snaps:
            snap = snaps[snapkey]
            isUsed = snap.isUsed()
            if isUsed and not self._view.has_snap_item(snapkey):
                self._view.add_snap_item(snapkey)
            elif not isUsed and self._view.has_snap_item(snapkey):
                self._view.remove_snap_item(snapkey)

        # Update the SnapItem cache list
        self._cached_snap_item_snapkeys = snaps.keys()

        # Compute left and right blocks
        for index in blocks:
            block = blocks[index]
            left_index = block.leftBlock.index if block.leftBlock is not None else None
            right_index = block.rightBlock.index if block.rightBlock is not None else None
            self._view.set_block_item_settings(index, left_index, right_index)
            # Compute left and right snaps, and what bands are being touched
            emitter = blocks[index].emitter
            collector = blocks[index].collector
            for snap in emitter.values() + collector.values():
                order = snap.order
                containername = "emitter" if snap.isSource() else "collector"
                if not snap.isUsed():
                    items = [item for item in self._view.layout_manager._snap_items if item.snap_order == order]
                    items = [item for item in items if item.container.strType() == containername]
                    items_orders = [item.snap_order for item in items if item.block_index == snap.block.index]
                    assert(order not in items_orders)
                    continue
                left_order = snap.leftSnap.order if snap.leftSnap is not None else None
                right_order = snap.rightSnap.order if snap.rightSnap is not None else None
                pos_alt = snap.posBandLink.altitude if snap.posBandLink else None
                neg_alt = snap.negBandLink.altitude if snap.negBandLink else None
                self._view.set_snap_item_settings(snap.snapkey(), left_order, right_order, pos_alt, neg_alt)
# 
        # Compute top and bottom bands, rank, leftmost, and rightmost snaps
        for altitude in bands:
            # Skip bands that don't have an item 
            if not bands[altitude].isUsed():
                item_alts = [a for a in self._view.layout_manager._band_items]
                assert(altitude not in item_alts)
                continue
            band = bands[altitude]
            top_alt = band.topBand.altitude if band.topBand else None
            bot_alt = band.bottomBand.altitude if band.bottomBand else None
            emitters = band.emitters
            collectors = band.collectors
            emitters.sort(lambda x,y: x.block.index - y.block.index)
            collectors.sort(lambda x,y: x.block.index - y.block.index)
#TODO: query for the corresponding SnapItem and assign it to the BandItem
            left_snap = None
            right_snap = None
            if band.isPositive:
                left_snap = emitters[0]
                right_snap = collectors[-1]
            else:
                left_snap = collectors[0]
                right_snap = emitters[-1]
            self._view.set_band_item_settings(altitude, band.rank, top_alt, bot_alt, left_snap.snapkey(), right_snap.snapkey() )



        self._view.update_view()



