from topology import *


class AsciiBlock(object):
    def __init__(self,block):
        self.block = typecheck(block,Block,"block")

class AsciiBand(object):
    def __init__(self,band):
        self._band = typecheck(band,Band,"band")
    
class AsciiSnap(object):
    def __init__(self,snap):
        self._snap = typecheck(snap,Snap,"snap")
   
