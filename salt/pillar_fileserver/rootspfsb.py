import salt.fileserver.rootsfsb

__virtualname__ = 'roots'

def __virtual__():
    return True

class RootsPFSB(salt.fileserver.rootsfsb.RootsFSB):
    serves = 'pillar'

def __init__(opts):
    global __load__
    __load__ = salt.fileserver.singleton_class_function_export(RootsPFSB, opts)

