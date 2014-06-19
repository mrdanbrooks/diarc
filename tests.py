import unittest
import types



class Test_v5_a(unittest.TestCase):
    def setUp(self):
        import parser
        self.t = parser.parseFile('data/v5_a.xml')
 
    def test_band_emitters_collectors(self):
        t = self.t
        # There should be exactly 1 edge with two bands
        assert(len(t.edges) == 1)
        assert(len(t.edges[0].bands) == 2)

        # Each band should have one emitter and one collector
        assert(len(t.edges[0].bands[0].emitters) == 1)
        assert(len(t.edges[0].bands[0].collectors) == 1)
        assert(len(t.edges[0].bands[1].emitters) == 1)
        assert(len(t.edges[0].bands[1].collectors) == 1)

        # The posBand emitter block should be index 0 and negBand block should be index 2
        assert(t.edges[0].posBand.emitters[0].block.index == 0)
        assert(t.edges[0].negBand.emitters[0].block.index == 2)
        
        # Both posBand and negBand collector block should be index 1, should be same snap object
        assert(t.edges[0].posBand.collectors[0].block.index == 1)
        assert(t.edges[0].negBand.collectors[0].block.index == 1)
        assert(t.edges[0].posBand.collectors[0] == t.edges[0].negBand.collectors[0])

    def test_block(self):
        t = self.t
        # Make sure the matching is correct
        for index in t.blocks:
            assert(t.blocks[index].index == index)

        # Count the number of emitters and collectors of each block
        # {blockIndex: (#collectors,#emitters), ...}
        vals = { 0: (0,1),  1: (1,0),  2: (0,1)}
        for index in t.blocks:
            assert(len(t.blocks[index].collector) == vals[index][0])
            assert(len(t.blocks[index].emitter) == vals[index][1])

    def test_snaps_to_bands_connectivity(self):
        """ Test to make sure that snaps are connected to the correct bands """
        t = self.t
        assert(t.blocks[0].emitter[0].posBand.altitude == 1)
        assert(t.blocks[0].emitter[0].negBand is None)
        assert(t.blocks[1].collector[0].posBand.altitude == 1)
        assert(t.blocks[1].collector[0].negBand.altitude == -1)
        assert(t.blocks[2].emitter[0].posBand is None)
        assert(t.blocks[2].emitter[0].negBand.altitude == -1)



class Test_v5_b(unittest.TestCase):
    def setUp(self):
        import parser
        self.t = parser.parseFile('data/v5_b.xml')
 
    def test_band_emitters_collectors(self):
        t = self.t
        # There should be exactly 1 edge with two bands
        assert(len(t.edges) == 1)
        assert(len(t.edges[0].bands) == 2)

        # Each band should have one emitter and one collector
        assert(len(t.edges[0].bands[0].emitters) == 1)
        assert(len(t.edges[0].bands[0].collectors) == 1)
        assert(len(t.edges[0].bands[1].emitters) == 1)
        assert(len(t.edges[0].bands[1].collectors) == 1)

        # The posBand collector block should be index 0 and negBand block should be index 2
        assert(t.edges[0].posBand.collectors[0].block.index == 2)
        assert(t.edges[0].negBand.collectors[0].block.index == 0)
        
        # Both posBand and negBand emitter block should both be index 1, should be same snap object
        assert(t.edges[0].posBand.emitters[0].block.index == 1)
        assert(t.edges[0].negBand.emitters[0].block.index == 1)
        assert(t.edges[0].posBand.emitters[0] == t.edges[0].negBand.emitters[0])

    def test_block(self):
        t = self.t
        # Make sure the matching is correct
        for index in t.blocks:
            assert(t.blocks[index].index == index)

        # Count the number of emitters and collectors of each block
        # {blockIndex: (#collectors,#emitters), ...}
        vals = { 0: (1,0),  1: (0,1),  2: (1,0)}
        for index in t.blocks:
            assert(len(t.blocks[index].collector) == vals[index][0])
            assert(len(t.blocks[index].emitter) == vals[index][1])

    def test_snaps_to_bands_connectivity(self):
        """ Test to make sure that snaps are connected to the correct bands """
        t = self.t
        assert(t.blocks[0].collector[0].posBand is None)
        assert(t.blocks[0].collector[0].negBand.altitude == -1)
        assert(t.blocks[1].emitter[0].posBand.altitude == 1)
        assert(t.blocks[1].emitter[0].negBand.altitude == -1)
        assert(t.blocks[2].collector[0].posBand.altitude == 1)
        assert(t.blocks[2].collector[0].negBand is None)



class Test_v5_c(unittest.TestCase):
    def setUp(self):
        import parser
        self.t = parser.parseFile('data/v5_c.xml')
 
    def test_band_emitters_collectors(self):
        t = self.t
        # There should be exactly 1 edge with two bands
        assert(len(t.edges) == 1)
        assert(len(t.edges[0].bands) == 1)

        # The top band should have one emitter and two collectors
        assert(len(t.edges[0].posBand.emitters) == 1)
        assert(len(t.edges[0].posBand.collectors) == 2)
        # The bottom band should have nothing
        assert(len(t.edges[0].negBand.emitters) == 0)
        assert(len(t.edges[0].negBand.collectors) == 0)

    def test_block(self):
        t = self.t
        # Make sure the matching is correct
        for index in t.blocks:
            assert(t.blocks[index].index == index)

        # Count the number of emitters and collectors of each block
        # {blockIndex: (#collectors,#emitters), ...}
        vals = { 0: (0,1),  1: (1,0),  2: (1,0)}
        for index in t.blocks:
            assert(len(t.blocks[index].collector) == vals[index][0])
            assert(len(t.blocks[index].emitter) == vals[index][1])

    def test_snaps_to_bands_connectivity(self):
        """ Test to make sure that snaps are connected to the correct bands """
        t = self.t
        assert(t.blocks[0].emitter[0].posBand.altitude == 1)
        assert(t.blocks[0].emitter[0].negBand is None)
        assert(t.blocks[1].collector[0].posBand.altitude == 1)
        assert(t.blocks[1].collector[0].negBand is None)
        assert(t.blocks[2].collector[0].posBand.altitude == 1)
        assert(t.blocks[2].collector[0].negBand is None)

class Test_v5_d(unittest.TestCase):
    def setUp(self):
        import parser
        self.t = parser.parseFile('data/v5_d.xml')
 
    def test_band_emitters_collectors(self):
        t = self.t
        # There should be exactly 1 edge with two bands
        assert(len(t.edges) == 1)
        assert(len(t.edges[0].bands) == 1)

        # The top band should have nothing
        assert(len(t.edges[0].posBand.emitters) == 0)
        assert(len(t.edges[0].posBand.collectors) == 0)
        # The bottom band should have one emitter and two collectors
        assert(len(t.edges[0].negBand.emitters) == 2)
        assert(len(t.edges[0].negBand.collectors) == 1)

    def test_block_index(self):
        """ checks that topology block indexing follows block index values """
        t = self.t
        # Make sure the matching is correct
        for index in t.blocks:
            assert(t.blocks[index].index == index)

    def test_emitter_collector_count(self):
        """ Counts the number of emitters and collectors in each block """
        # {blockIndex: (#collectors,#emitters), ...}
        vals = { 0: (1,0),  1: (0,1),  2: (0,1)}
        t = self.t
        for index in t.blocks:
            assert(len(t.blocks[index].collector) == vals[index][0])
            assert(len(t.blocks[index].emitter) == vals[index][1])

    def test_snaps_connectivity(self):
        """ Test to make sure that snaps are connected to the correct bands """
        t = self.t
        assert(t.blocks[0].collector[0].posBand is None)
        assert(t.blocks[0].collector[0].negBand.altitude == -1)
        assert(t.blocks[1].emitter[0].posBand is None)
        assert(t.blocks[1].emitter[0].negBand.altitude == -1)
        assert(t.blocks[2].emitter[0].posBand is None)
        assert(t.blocks[2].emitter[0].negBand.altitude == -1)

class Test_v5_e(unittest.TestCase):
    def setUp(self):
        import parser
        self.t = parser.parseFile('data/v5_e.xml')
 
    def test_band_emitters_collectors(self):
        t = self.t
        # There should be exactly 1 edge with two bands
        assert(len(t.edges) == 1)
        assert(len(t.edges[0].bands) == 2)

        # Check locations
        assert([snap.block.index for snap in t.edges[0].posBand.emitters] == [0,2])
        assert([snap.block.index for snap in t.edges[0].posBand.collectors] == [1,3])
        assert([snap.block.index for snap in t.edges[0].negBand.emitters] == [2])
        assert([snap.block.index for snap in t.edges[0].negBand.collectors] == [1])

    def test_block_index(self):
        """ checks that topology block indexing follows block index values """
        t = self.t
        # Make sure the matching is correct
        for index in t.blocks:
            assert(t.blocks[index].index == index)

    def test_emitter_collector_count(self):
        """ Counts the number of emitters and collectors in each block """
        # {blockIndex: (#collectors,#emitters), ...}
        vals = { 0: (0,1),  1: (1,0),  2: (0,1), 3: (1,0)}
        t = self.t
        for index in t.blocks:
            assert(len(t.blocks[index].collector) == vals[index][0])
            assert(len(t.blocks[index].emitter) == vals[index][1])

    def test_snaps_connectivity(self):
        """ Test to make sure that snaps are connected to the correct bands """
        t = self.t
        assert(t.blocks[0].emitter[0].posBand.altitude == 1)
        assert(t.blocks[0].emitter[0].negBand is None)
        assert(t.blocks[1].collector[0].posBand.altitude == 1)
        assert(t.blocks[1].collector[0].negBand.altitude == -1)
        assert(t.blocks[2].emitter[0].posBand.altitude == 1)
        assert(t.blocks[2].emitter[0].negBand.altitude == -1)
        assert(t.blocks[3].collector[0].posBand.altitude == 1)
        assert(t.blocks[3].collector[0].negBand is None)


class Test_v5_f(unittest.TestCase):
    def setUp(self):
        import parser
        self.t = parser.parseFile('data/v5_f.xml')
 
    def test_band_emitters_collectors(self):
        t = self.t
       
        # Check locations
        assert([snap.block.index for snap in t.edges[0].posBand.emitters] == [1])
        assert([snap.block.index for snap in t.edges[0].posBand.collectors] == [2])
        assert([snap.block.index for snap in t.edges[0].negBand.emitters] == [1,3])
        assert([snap.block.index for snap in t.edges[0].negBand.collectors] == [0,2])

    def test_block_index(self):
        """ checks that topology block indexing follows block index values """
        t = self.t
        # Make sure the matching is correct
        for index in t.blocks:
            assert(t.blocks[index].index == index)

    def test_emitter_collector_count(self):
        """ Counts the number of emitters and collectors in each block """
        # {blockIndex: (#collectors,#emitters), ...}
        vals = { 0: (1,0),  1: (0,1),  2: (1,0), 3: (0,1)}
        t = self.t
        for index in t.blocks:
            assert(len(t.blocks[index].collector) == vals[index][0])
            assert(len(t.blocks[index].emitter) == vals[index][1])

    def test_snaps_connectivity(self):
        """ Test to make sure that snaps are connected to the correct bands """
        t = self.t
        assert(t.blocks[0].collector[0].negBand.altitude == -1)
        assert(t.blocks[0].collector[0].posBand is None)
        assert(t.blocks[1].emitter[0].negBand.altitude == -1)
        assert(t.blocks[1].emitter[0].posBand.altitude == 1)
        assert(t.blocks[2].collector[0].negBand.altitude == -1)
        assert(t.blocks[2].collector[0].posBand.altitude == 1)
        assert(t.blocks[3].emitter[0].negBand.altitude == -1)
        assert(t.blocks[3].emitter[0].posBand is None)




if __name__ == "__main__":
    unittest.main()




