import types

class IndexedList(dict):
    def __init__(self,_type,sortFunc=None):
        typecheck(_type,type,"_type")
        self._valFunc = valFunc or (lambda x,y: x if x >= y else y)
        typecheck(valFunc,types.FunctionType,"valFunc")
        self._type = _type
        super(IndexedList,self).__init__()

    def insert(self,obj):
        typecheck(obj,self._type,"obj")
        key = self._valFunc(obj)
        if key in self.keys():
            raise Exception("Object with  value %r already exists"%key)
        super(IndexedList,self).__setitem__(key,obj)

    def keys(self):
        return self._order

    def values(self):
        return [self[key] for key in self._order]
    
    def __iter__(self):
        for key in self._order:
            yield key

    def iteritems(self):
        for key in self._order:
            yield (key,self[key])

    def iterkeys(self):
        for key in self._order:
            yield key

    def itervalues(self):
        for key in self._order:
            yield self[key]
            
    def __repr__(self):
        out = "{"
        if len(self) > 0:
            for x in self.iteritems():
                out+=repr(x[0])+": "+repr(x[1])+", "
            out = out[:-2]
        out+="}"
        return out

    def __str__(self):
        return self.__repr__()


    def __setitem__(self,key,val):
        raise Exception("Cannot assign directly to list")



class TypedList(list):
    def __init__(self,_type):
        super(TypedList,self).__init__()
        typecheck(_type,type,"_type")
        self._type = _type

    def insert(self,index,val):
        typecheck(self._type,val,"val")
        super(TypedList,self).insert(val)

    def append(self,val):
        typecheck(val,self._type,"val")
        super(TypedList,self).append(val)

    def __setitem__(self,key,val):
        typecheck(val,self._type,"val")
        super(TypedList,self).__setitem__(key,val)

 
def typecheck(obj,objtype,varname=None):
    """ Checks the type of obj against class objtype, optionally pass in a varname for debug purposes.  """
    var = varname or ""
    if not isinstance(obj,objtype):
        raise Exception("%s must be of type '%s', got %r"%(var, objtype.__name__, obj.__class__.__name__))



   
