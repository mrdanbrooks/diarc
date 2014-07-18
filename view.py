
class View(object):
    """ Interface definations provided by the View for use by the Adapter.  
    
    NOTE: There should be no Qt specific code here!
    """
    def __init__(self):
        self.adapter = None

    def register_adapter(self,adapter):
        """ Saves a pointer to the adapter object."""
        self.adapter = adapter

    def update_view(self):
        raise NotImplementedError()


    def add_block_item(self, index):
        """ Create new a drawable object to correspond to a Block with this index. """
        raise NotImplementedError()

    def remove_block_item(self, index):
        """ Remove the drawable object that corresponds with block index """
        raise NotImplementedError()

    def get_block_item(self, index):
        """ Return a pointer to the single drawable object that corresponds to 
        the block with the given index.
        Raise an exception if no such item exists, or if multiple items match.
        """
        raise NotImplementedError()

    def add_band_item(self, altitude, rank):
        """ Create a new drawable object to correspond to a Band. """
        raise NotImplementedError()

    def remove_band_item(self, altitude):
        """ Remove the drawable object to correspond to a band """ 
        raise NotImplementedError()

    def get_band_item(self, altitude):
        """ Returns the BandItem with the given altitude """
        raise NotImplementedError()

    def add_snap_item(self, block_index, container, order):
        raise NotImplementedError()

    def remove_snap_item(self, block_index, container, order):
        raise NotImplementedError()

    def get_snap_item(self, block_index, container, order):
        raise NotImplementedError()

