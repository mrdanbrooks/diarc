#!/usr/bin/python
# Usage:
# ./test.py topology_plot data/v5.xml

import sys
import inspect

def ros_plot(args):
    """ Test drawing a ROS xml specification """
    import ros_parser
    import asciiplot
    ros = ros_parser.parseFile(args[0])
    asciiplot.draw(ros)

def asciidraw(args):
    import parser
    import asciidraw

    topology = parser.parseFile(args[0])
    print ""
    asciidraw.draw(topology)

def topology_plot(args):
    """ draw an xml topology in ascii art """
    import parser
    import asciiplot
    print "Opening file",args[0]

    topology = parser.parseFile(args[0])
    print ""
    asciiplot.draw(topology)


if __name__=="__main__":
    available_tests = dict(inspect.getmembers(sys.modules[__name__],inspect.isfunction))

    if len(sys.argv) < 2 or sys.argv[1] not in available_tests:
        print "Usage:\n ./test.py <test> [parameters]\n"
        print "Tests available:",available_tests.keys()
        exit(0)
    elif len(sys.argv)>2:
        available_tests[sys.argv[1]](sys.argv[2:])
    else:
        available_tests[sys.argv[1]]()

