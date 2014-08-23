:mod:`topology` - the diarc graph data structure
================================================
.. module:: topology
  :synopsis: the diarc graph data structure

This module contains the graph data structures used by diarc.

.. class:: Topology

    Storage container for describing the graph and diagram 

    .. attribute:: vertices

        An unordered list of all :py:class:`Vertex` objects.

    .. attribute:: edges

        An unordered list of all :py:class:`Edge` objects

    .. attribute:: blocks

        A dictionary of :py:class:`Block` objects indexed by :py:attr:`Block.index`. 
        The dictionary is generated every time it is requested. Only blocks with proper :py:attr:`Block.index` values are included. 

    .. attribute:: bands

        A dictionary of :py:class:`Band` objects, listed by :py:attr:`Band.altitude`.
        Bands which have not been assigned altitudes are not reported. All bands that have an altitude
        (regardless of if they are being used (indicated by isUsed) are reported. 

    .. attribute:: snaps

        A dictionary of :py:class:`Snap` objects, by snapkey. Snaps which have not been
        assigned an order are not reported. All snaps that have an order regardless
        of if they are being used (indicated by isUsed) are reported. 

    .. attribute:: hide_disconnected_snaps

.. class:: Vertex

    A Vertex in a directional graph. 
    A vertex can connect to multiple edges as either an input (source) or output
    (sink) to the edge. It is graphically represented by a Block object.

    .. attribute:: sources

       Unordered list of outgoing connections (:py:class:`Source` objects)

    .. attribute:: sinks

        Unordered list of incomming connections. (:py:class:`Sink` objects)

    .. attribute:: block

        :py:class:`Block` object for this Vertex. 
        It is created when the vertex is instantiated, and cannot be reassigned. 

    .. method:: release()

        Removes this vertex from the topology. 
        This additionally removes all its associated :py:class:`Connection` 
        and :py:class:`Block` objects from the topology.
        
.. class:: Edge

    A directional multiple-input multiGple-output edge in the graph. Inputs
    (sources) and outputs (sinks) are linked to vertices. An edge is represented 
    graphically by either 1 or 2 Band objects. 

    .. attribute:: sources

    .. attribute:: sinks

    .. attribute:: posBand

    .. attribute:: negBand

    .. method:: release()

.. class:: Connection

    A base class for connecting a vertex to an edge, but without specifing 
    the nature of the connection (input or output). Rather then using this 
    class directly, Source or Sink objects should be used.

    .. attribute:: snap

    .. attribute:: edge

    .. attribute:: vertex

    .. attribute:: block

    .. method:: release()

.. class:: Source(Connection)

    A logical connection from a Vertex to an Edge. Graphically represented 
    by a Snap object.

    .. method:: release() 

.. class:: Sink(Connection)
    
    A logical connection from an Edge to a Vertex. Graphically represented
    by a Snap object. 

    .. method:: release() 

.. class:: Block

    Visual Representation of a Vertex
    Visual Parameters
    Index - Unique int value to determine order in which to draw blocks. 
            Lower values to the left, higher to the right. Indices do not 
            necessarily need to be consecutive.

    .. attribute:: index

        Defines the order in which blocks are arranged.
        This value is initially unset (defaults to None).
        For the block to be displayed as part of the graph, this value must be 
        changed to a positive integer that is unique among blocks.

    .. attribute:: vertex

        Returns the logical component (Vertex) for this relative object.
        The vertex is bound to this block, and cannot be changed.

    .. attribute:: emitter

        Dictionary of Snaps that represent source connections for this block.
        Only snaps which have been assigned an order value are represented, since
        the order is used as the dictionary key. If hide_disconnected_snaps is 
        set in the topology, only return snaps where isLinked() is true. 


    .. attribute:: collector

        Dictionary of :py:class:`Snap` objects that represent sink connections for this block.
        Only snaps which have been assigned an order value are represented, since
        the order is used as the dictionary key. If hide_disconnected_snaps is 
        set in the topology, only return snaps where isLinked() is true. 

    .. attribute:: leftBlock

        returns the block to the left, determined by block which has the next
        lowest index value.

    .. attribute:: rightBlock

        returns the block to the right, determined by block which has the next
        highest index value.
    
.. class:: Band

    Visual Representation of an Edge.
    An Edge can have up to two Bands - one with positive altitude and one negative.
    Visual Parameters
    Rank - the Z drawing order (higher values closer to user)
    Altitude - the distance above or below the Block ribbon

    .. attribute:: altitude

    .. attribute:: rank

    .. attribute:: edge

    .. attribute:: emitters

    .. attribute:: collectors

    .. attribute:: isPositive

    .. attribute:: topBand

    .. attribute:: bottomBand

    .. method:: isUsed()

----------------

.. automodule:: diarc.topology
  :members:
  :inherited-members:
