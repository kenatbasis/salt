# -*- coding: utf-8 -*-
'''
Manage information about files on the minion, set/read user, group
data

:depends:   - win32api
            - win32con
            - win32security
            - ntsecuritycon
'''

# Import python libs
import os
import stat
import os.path
import logging
import contextlib
import difflib
import tempfile  # do not remove. Used in salt.modules.file.__clean_tmp
import itertools  # same as above, do not remove, it's used in __clean_tmp

# Import third party libs
try:
    import win32security
    from pywintypes import error as pywinerror
    import ntsecuritycon as con
    HAS_WINDOWS_MODULES = True
except ImportError:
    HAS_WINDOWS_MODULES = False

# Import salt libs
import salt.utils
from salt.modules.file import (check_hash,  # pylint: disable=W0611
        directory_exists, get_managed, mkdir, makedirs, makedirs_perms,
        check_managed, check_perms, patch, remove, source_list, sed_contains,
        touch, append, contains, contains_regex, contains_regex_multiline,
        contains_glob, patch, uncomment, sed, find, psed, get_sum, check_hash,
        get_hash, comment, manage_file, file_exists, get_diff, get_managed,
        __clean_tmp, check_managed, check_file_meta, _binary_replace,
        contains_regex)

from salt.utils import namespaced_function as _namespaced_function

log = logging.getLogger(__name__)

# Define the module's virtual name
__virtualname__ = 'file'


def __virtual__():
    '''
    Only works on Windows systems
    '''
    if salt.utils.is_windows():
        if HAS_WINDOWS_MODULES:
            global check_perms, get_managed, makedirs_perms, manage_file
            global source_list, mkdir, __clean_tmp, makedirs, file_exists

            check_perms = _namespaced_function(check_perms, globals())
            get_managed = _namespaced_function(get_managed, globals())
            makedirs_perms = _namespaced_function(makedirs_perms, globals())
            makedirs = _namespaced_function(makedirs, globals())
            manage_file = _namespaced_function(manage_file, globals())
            source_list = _namespaced_function(source_list, globals())
            mkdir = _namespaced_function(mkdir, globals())
            file_exists = _namespaced_function(file_exists, globals())
            __clean_tmp = _namespaced_function(__clean_tmp, globals())

            return __virtualname__
        log.warn(salt.utils.required_modules_error(__file__, __doc__))
    return False


__outputter__ = {
    'touch': 'txt',
    'append': 'txt',
}


def gid_to_group(gid):
    '''
    Convert the group id to the group name on this system

    CLI Example:

    .. code-block:: bash

        salt '*' file.gid_to_group S-1-5-21-626487655-2533044672-482107328-1010
    '''
    if not gid:
        return False
    sid = win32security.GetBinarySid(gid)
    name, domain, account_type = win32security.LookupAccountSid(None, sid)
    return name


def group_to_gid(group):
    '''
    Convert the group to the gid on this system

    CLI Example:

    .. code-block:: bash

        salt '*' file.group_to_gid administrators
    '''
    sid, domain, account_type = win32security.LookupAccountName(None, group)
    return win32security.ConvertSidToStringSid(sid)


def get_gid(path):
    '''
    Return the id of the group that owns a given file

    CLI Example:

    .. code-block:: bash

        salt '*' file.get_gid c:\\temp\\test.txt
    '''
    if not os.path.exists(path):
        return False
    secdesc = win32security.GetFileSecurity(
        path, win32security.OWNER_SECURITY_INFORMATION
    )
    owner_sid = secdesc.GetSecurityDescriptorOwner()
    return win32security.ConvertSidToStringSid(owner_sid)


def get_group(path):
    '''
    Return the group that owns a given file

    CLI Example:

    .. code-block:: bash

        salt '*' file.get_group c:\\temp\\test.txt
    '''
    if not os.path.exists(path):
        return False
    secdesc = win32security.GetFileSecurity(
        path, win32security.OWNER_SECURITY_INFORMATION
    )
    owner_sid = secdesc.GetSecurityDescriptorOwner()
    name, domain, account_type = win32security.LookupAccountSid(None, owner_sid)
    return name


def uid_to_user(uid):
    '''
    Convert a uid to a user name

    CLI Example:

    .. code-block:: bash

        salt '*' file.uid_to_user S-1-5-21-626487655-2533044672-482107328-1010
    '''
    sid = win32security.GetBinarySid(uid)
    name, domain, account_type = win32security.LookupAccountSid(None, sid)
    return name


def user_to_uid(user):
    '''
    Convert user name to a uid

    CLI Example:

    .. code-block:: bash

        salt '*' file.user_to_uid myusername
    '''
    sid, domain, account_type = win32security.LookupAccountName(None, user)
    return win32security.ConvertSidToStringSid(sid)


def get_uid(path):
    '''
    Return the id of the user that owns a given file

    CLI Example:

    .. code-block:: bash

        salt '*' file.get_uid c:\\temp\\test.txt
    '''
    if not os.path.exists(path):
        return False
    secdesc = win32security.GetFileSecurity(
        path, win32security.OWNER_SECURITY_INFORMATION
    )
    owner_sid = secdesc.GetSecurityDescriptorOwner()
    return win32security.ConvertSidToStringSid(owner_sid)


def get_mode(path):
    '''
    Return the mode of a file

    Right now we're just returning 777
    because Windows' doesn't have a mode
    like Linux

    CLI Example:

    .. code-block:: bash

        salt '*' file.get_mode /etc/passwd
    '''
    if not os.path.exists(path):
        return -1
    mode = 777
    return mode


def get_user(path):
    '''
    Return the user that owns a given file

    CLI Example:

    .. code-block:: bash

        salt '*' file.get_user c:\\temp\\test.txt
    '''
    secdesc = win32security.GetFileSecurity(
        path, win32security.OWNER_SECURITY_INFORMATION
    )
    owner_sid = secdesc.GetSecurityDescriptorOwner()
    name, domain, account_type = win32security.LookupAccountSid(None, owner_sid)
    return name


def chown(path, user, group):
    '''
    Chown a file, pass the file the desired user and group

    CLI Example:

    .. code-block:: bash

        salt '*' file.chown c:\\temp\\test.txt myusername administrators
    '''
    err = ''
    # get SID object for user
    try:
        userSID, domainName, objectType = win32security.LookupAccountName(None, user)
    except pywinerror:
        err += 'User does not exist\n'

    # get SID object for group
    try:
        groupSID, domainName, objectType = win32security.LookupAccountName(None, group)
    except pywinerror:
        err += 'Group does not exist\n'

    if not os.path.exists(path):
        err += 'File not found\n'
    if err:
        return err

    # set owner and group
    securityInfo = win32security.OWNER_SECURITY_INFORMATION + win32security.GROUP_SECURITY_INFORMATION
    win32security.SetNamedSecurityInfo(path, win32security.SE_FILE_OBJECT, securityInfo, userSID, groupSID, None, None)
    return None


def chgrp(path, group):
    '''
    Change the group of a file

    CLI Example:

    .. code-block:: bash

        salt '*' file.chgrp c:\\temp\\test.txt administrators
    '''
    err = ''
    # get SID object for group
    try:
        groupSID, domainName, objectType = win32security.LookupAccountName(None, group)
    except pywinerror:
        err += 'Group does not exist\n'

    if not os.path.exists(path):
        err += 'File not found\n'
    if err:
        return err

    # set group
    securityInfo = win32security.GROUP_SECURITY_INFORMATION
    win32security.SetNamedSecurityInfo(path, win32security.SE_FILE_OBJECT, securityInfo, None, groupSID, None, None)
    return None


def stats(path, hash_type='md5', follow_symlink=False):
    '''
    Return a dict containing the stats for a given file

    CLI Example:

    .. code-block:: bash

        salt '*' file.stats /etc/passwd
    '''
    ret = {}
    if not os.path.exists(path):
        return ret
    if follow_symlink:
        pstat = os.stat(path)
    else:
        pstat = os.lstat(path)
    ret['inode'] = pstat.st_ino
    ret['uid'] = pstat.st_uid
    ret['gid'] = pstat.st_gid
    ret['group'] = 0
    ret['user'] = 0
    ret['atime'] = pstat.st_atime
    ret['mtime'] = pstat.st_mtime
    ret['ctime'] = pstat.st_ctime
    ret['size'] = pstat.st_size
    ret['mode'] = str(oct(stat.S_IMODE(pstat.st_mode)))
    ret['sum'] = get_sum(path, hash_type)
    ret['type'] = 'file'
    if stat.S_ISDIR(pstat.st_mode):
        ret['type'] = 'dir'
    if stat.S_ISCHR(pstat.st_mode):
        ret['type'] = 'char'
    if stat.S_ISBLK(pstat.st_mode):
        ret['type'] = 'block'
    if stat.S_ISREG(pstat.st_mode):
        ret['type'] = 'file'
    if stat.S_ISLNK(pstat.st_mode):
        ret['type'] = 'link'
    if stat.S_ISFIFO(pstat.st_mode):
        ret['type'] = 'pipe'
    if stat.S_ISSOCK(pstat.st_mode):
        ret['type'] = 'socket'
    ret['target'] = os.path.realpath(path)
    return ret
