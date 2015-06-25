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

""" Snapkeys are abbreviations that can be used to identify a snap. Snaps do
    not have a single unique attribute, which makes them difficult to identify.
    Snapkeys solve that problem.

    Snapkeys have 3 parts:
        block index (int)
        container indicator ('e' for emitter or 'c' for collector)
        snap order

    Example:
        snapkey 3e1 means the snap in block index 3's emitter with order 1
"""
import re
def parse_snapkey(snapkey):
    """ Parses a snapkey into a 3-tuple """
    m = re.findall("(^\d+)([ce])(\d+$)",snapkey)
    if len(m) == 0:
        raise Exception("Invalid snapkey %s"%snapkey)
    container_name = "emitter" if m[0][1] == 'e' else "collector" if m[0][1] == 'c' else None
    return (int(m[0][0]), container_name, int(m[0][2]))

def gen_snapkey(block_index, container, snap_order):
    """ generate a snapkey """
    assert(container in ["emitter","collector"])
    return "%d%s%d"%(block_index,container[0],snap_order)
