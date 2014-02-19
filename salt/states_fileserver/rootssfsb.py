import salt.fileserver.rootsfsb

__virtualname__ = 'roots'

def __virtual__():
    return True

class RootsSFSB(salt.fileserver.rootsfsb.RootsFSB):
    serves = 'states'

def __init__(opts):
    global __load__
    __load__ = salt.fileserver.singleton_class_function_export(RootsSFSB, opts)
