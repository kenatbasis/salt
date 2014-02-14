# -*- coding: utf-8 -*-
'''
Extends fileserver
'''

# Import salt libs
import salt.fileserver

class PillarFileserver(salt.fileserver.Fileserver):
    '''
    Instantiates a fileserver using the pillar_fileserver_backend config
    '''

    def __init__(self, opts):
        super(PillarFileserver, self).__init__(opts, 'pillar')

