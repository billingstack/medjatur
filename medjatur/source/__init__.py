from medjatur.plugin import SourcePlugin


def get_source(*args, **kw):
    return SourcePlugin.get_plugin(*args, **kw)
