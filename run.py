#!/usr/bin/env python
# Usage:
# ./run.py topology_plot data/v5.xml

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

def asciiplot(args):
    """ draw an xml topology in ascii art """
    import parser
    import asciiplot
    print "Opening file",args[0]

    topology = parser.parseFile(args[0])
    print ""
    asciiplot.draw(topology)

def qtplot(args):
    import PyQt4.QtGui
    import parser
    import qtview
    topology = parser.parseFile(args[0])
    app = PyQt4.QtGui.QApplication(sys.argv)
    graphView = qtview.GraphView(topology)
    # Create Visual Objects
    for altitude,band in topology.bands.items():
        print "adding band",altitude
        visualBand = qtview.BandItem(graphView.topologyWidget,band)
    for index,block in topology.blocks.items():
        print "adding block",index
        vertexBlock = qtview.BlockItem(graphView.topologyWidget,block)
        for snap in block.emitter.values()+block.collector.values():
            print "adding snap",snap.order
            mySnap = qtview.SnapItem(graphView.topologyWidget,snap)
    graphView.topologyWidget.link()

    graphView.activateWindow()
    graphView.raise_()
    sys.exit(app.exec_())

def rostest():
    import PyQt4.QtGui
    import ros_diarc
    app = PyQt4.QtGui.QApplication([])
    graphView = ros_diarc.RosDiarcWidget()
    graphView.activateWindow()
    graphView.raise_()
    sys.exit(app.exec_())

def rostest2():
    import PyQt4.QtGui
    import qt_view
    import ros_adapter
    app = PyQt4.QtGui.QApplication([])
    view = qt_view.QtView()
    adapter = ros_adapter.RosAdapter(view)
    adapter.update_model()
    view.activateWindow()
    view.raise_()
    sys.exit(app.exec_())

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

