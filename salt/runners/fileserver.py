# -*- coding: utf-8 -*-
'''
Directly manage the salt fileserver plugins
'''

# Import salt libs
import salt.states_fileserver
import salt.pillar_fileserver


def update():
    '''
    Execute an update for all of the configured fileserver backends

    CLI Example:

    .. code-block:: bash

        salt-run fileserver.update
    '''
    fileservers = [
            salt.states_fileserver.StatesFileserver(__opts__),
            salt.pillar_fileserver.PillarFileserver(__opts__),
            ]
    for fileserver in fileservers:
        fileserver.update()
