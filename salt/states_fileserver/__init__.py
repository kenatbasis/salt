# -*- coding: utf-8 -*-
'''
Extends fileserver
'''

# Import salt libs
import salt.fileserver

class StatesFileserver(salt.fileserver.Fileserver):
    '''
    Instantiates a fileserver using the states_fileserver_backend config
    '''

    def __init__(self, opts):
        super(StatesFileserver, self).__init__(opts, 'states')

