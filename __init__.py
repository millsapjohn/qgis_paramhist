from .paramhist import ParamHistPlugin

def classFactory(iface):
    return ParamHistPlugin(iface)
