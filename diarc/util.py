# Copyright 2014 Open Source Robotics Foundation, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import types

class TypedDict(dict):
    def __init__(self,_keyType,_objType):
        super(TypedDict,self).__init__()
        typecheck(_keyType,type,"_keyType")
        typecheck(_objType,type,"_objType")
        self._keyType = _keyType
        self._objType = _objType

    def __setitem__(self,key,val):
        typecheck(key,self._keyType,"key")
        typecheck(val,self._objType,"val")
        super(TypedDict,self).__setitem__(key,val)

    def __getitem__(self, key):
        typecheck(key, self._keyType, "key")
        return super(TypedDict,self).__getitem__(key)

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
    return obj



   
