import salt.fileserver.roots

class RootsSFSB(salt.fileserver.roots.RootsFSB):
    serves = 'states'

def __init__():
    global __load__
    __load__ = salt.fileserver.singleton_class_function_export(RootsSFSB, __opts__)
