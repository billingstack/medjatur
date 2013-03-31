from medjatur.plugin import DestinationPlugin


def get_destination(*args, **kw):
    return DestinationPlugin.get_plugin(*args, **kw)
