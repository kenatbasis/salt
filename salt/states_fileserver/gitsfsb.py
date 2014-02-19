import salt.fileserver.gitfsb

__virtualname__ = 'git'

class GitSFSB(salt.fileserver.gitfsb.GitFSB):
    serves = 'states'

def __virtual__():
    return salt.fileserver.gitfsb.virtual(__virtualname__, __opts__, GitSFSB.serves)

def __init__(opts):
    globals().update(salt.fileserver.singleton_class_function_export(GitSFSB, opts))
