import salt.fileserver.roots

class RootsPFSB(salt.fileserver.roots.RootsFSB):
    serves = 'pillar'

def __init__():
    global __load__
    __load__ = salt.fileserver.singleton_class_function_export(RootsPFSB, __opts__)
