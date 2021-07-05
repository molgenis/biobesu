#!/user/bin/env python3

from shutil import which
from os.path import isfile
from os.path import isdir
from os import access
from os import R_OK
from os import W_OK
from os import X_OK
from biobesu.helper.generic import create_dir


def program(cmd):
    """
    Checks whether the command line (which should contain an application name) refers to a valid path. If it is an
    existing application, does nothing. If the path is not valid, raises an OSError.
    :param cmd: the name of the application as how it would be called using the command line
    """

    if not which(cmd):
        raise OSError(f'Error: {cmd} is not available on this system.')


def file(file_string, expected_extension='', executable=False):
    """
    Checks whether given path goes to a valid file. If not, raises an OSError.
    :param file_string: path to check whether it is a readable file
    :param expected_extension: the expected file extension (default: '', which skips this check)
    :param executable: whether file_string should be checked if it is executable (default: False)
    """

    file_name = file_string.split('/')[-1]
    if not isfile(file_string):
        raise OSError(f'"{file_name}" is not a file')
    if expected_extension != '' and not file_string.endswith(expected_extension):
        raise OSError(f'"{file_name}" is not a {expected_extension} file')
    if not access(file_string, R_OK):
        raise OSError(f'"{file_name}" is not a readable file')
    if executable and not access(file_string, X_OK):
        raise OSError(f'"{file_name}" is not an executable file')


def directory(dir_string, writable=True, create_if_not_exist=False):
    """
    Checks whether given path goes to an existing directory. If not, raises an OSError.
    :param dir_string: directory path to check
    :param writable: check whether a directory is writable (default: True)
    :param create_if_not_exist: creates directory before validating if true (default: False)
    """

    # Strips slash on the end and re-adds it so input directories are always coherent.
    dir_string = dir_string.rstrip('/') + '/'
    dir_name = dir_string.split('/')[-2]

    # Creates directory if allowed before validating.
    if create_if_not_exist:
        create_dir(dir_string, exist_allowed=True)

    if not isdir(dir_string):
        raise OSError(f'"{dir_name}" is not a directory')
    if not access(dir_string, R_OK):
        raise OSError(f'"{dir_name}" is not a readable directory')
    if writable and not access(dir_string, W_OK):
        raise OSError(f'"{dir_name}" is not a writable directory')

    # Return coherent dir string.
    return dir_string
