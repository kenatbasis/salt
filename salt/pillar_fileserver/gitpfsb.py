import salt.fileserver.gitfsb

__virtualname__ = 'git'

class GitPFSB(salt.fileserver.gitfsb.GitFSB):
    serves = 'pillar'

def __virtual__():
    return salt.fileserver.gitfsb.virtual(__virtualname__, __opts__, GitPFSB.serves)

def __init__(opts):
    globals().update(salt.fileserver.singleton_class_function_export(GitPFSB, opts))
