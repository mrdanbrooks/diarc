import unittest


class TestBandEmittersCollectors(unittest.TestCase):
    """ A Band object's emitters and collectors should only consist of the 
    subset of snaps which will actually be drawn touching the band. Some snaps
    have links to a band they will not touch because the snap corresponds to a
    connection with an edge the follows the alternative band. 
    """
    def test_v5_a(self):
        import parser
        # TestFile v5_a.xml
        t = parser.parseFile('data/v5_a.xml')
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

    def test_v5_b(self):
        import parser
        t = parser.parseFile('data/v5_b.xml')
        
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

    def test_v5_c(self):
        import parser
        t = parser.parseFile('data/v5_c.xml')
        
        # There should be exactly 1 edge with two bands
        assert(len(t.edges) == 1)
        assert(len(t.edges[0].bands) == 2)

        # The top band should have one emitter and two collectors
        assert(len(t.edges[0].posBand.emitters) == 1)
        assert(len(t.edges[0].posBand.collectors) == 2)
        # The bottom band should have nothing
        assert(len(t.edges[0].negBand.emitters) == 0)
        assert(len(t.edges[0].negBand.collectors) == 0)

    def test_v5_d(self):
        import parser
        t = parser.parseFile('data/v5_d.xml')
        
        # There should be exactly 1 edge with two bands
        assert(len(t.edges) == 1)
        assert(len(t.edges[0].bands) == 2)

        # The top band should have nothing
        assert(len(t.edges[0].posBand.emitters) == 0)
        assert(len(t.edges[0].posBand.collectors) == 0)
        # The bottom band should have one emitter and two collectors
        assert(len(t.edges[0].negBand.emitters) == 2)
        assert(len(t.edges[0].negBand.collectors) == 1)


    def test_v5_e(self):
        import parser
        t = parser.parseFile('data/v5_e.xml')
        
        # There should be exactly 1 edge with two bands
        assert(len(t.edges) == 1)
        assert(len(t.edges[0].bands) == 2)

        # The top band should have two sources and two sinks
        assert(len(t.edges[0].posBand.emitters) == 2)
        assert(len(t.edges[0].posBand.collectors) == 2)
        # The bottom band should have one source and one sink
        assert(len(t.edges[0].negBand.emitters) == 1)
        assert(len(t.edges[0].negBand.collectors) == 1)

        # Check locations
        assert([snap.block.index for snap in t.edges[0].posBand.emitters] == [0,2])
        assert([snap.block.index for snap in t.edges[0].posBand.collectors] == [1,3])
        assert([snap.block.index for snap in t.edges[0].negBand.emitters] == [2])
        assert([snap.block.index for snap in t.edges[0].negBand.collectors] == [1])

    def test_v5_f(self):
        import parser
        t = parser.parseFile('data/v5_f.xml')
        
        # There should be exactly 1 edge with two bands
        assert(len(t.edges) == 1)
        assert(len(t.edges[0].bands) == 2)

        # The bottom band should have two sources and two sinks
        assert(len(t.edges[0].negBand.emitters) == 2)
        assert(len(t.edges[0].negBand.collectors) == 2)
        # The top band should have one source and one sink
        assert(len(t.edges[0].posBand.emitters) == 1)
        assert(len(t.edges[0].posBand.collectors) == 1)

        # Check locations
        assert([snap.block.index for snap in t.edges[0].posBand.emitters] == [1])
        assert([snap.block.index for snap in t.edges[0].posBand.collectors] == [2])
        assert([snap.block.index for snap in t.edges[0].negBand.emitters] == [1,3])
        assert([snap.block.index for snap in t.edges[0].negBand.collectors] == [0,2])

if __name__ == "__main__":
    unittest.main()




