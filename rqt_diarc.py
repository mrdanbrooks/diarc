import os
import rospy

from qt_gui.plugin import Plugin
from python_qt_bindings import loadUi
from python_qt_bindings.QtGui import QWidget

class DiarcPlugin(Plugin):
    def __init__(self,context):
        super(DiarcPlugin,self).__init__(context)
        self.setObjectName('DiarcPlugin')

        from argparse import ArgumentParser
        parser = ArgumentPraser()
        parser.add_argument("-q", "--quiet", action="store_true", dest="quiet", help="put plugin in silent mode")
        args, unknowns = parser.parse_known_args(context.argv())
        if not args.quiet:
            pass

        import rosgraph_hooks
        topology = rosgraph_hooks.rsg_generator()
        # Create widget
        self._widget = GraphView()
        self._widget.autoLayout(topology)
        context.add_widget(self._widget)
    
    def shutdown_plugin(self):
        # Unregister ROS connections here
        pass

    def save_settings(self,plugin_settings, instance_settings):
        pass

    def restore_settings(self,plugin_settings, instance_settings):
        pass

