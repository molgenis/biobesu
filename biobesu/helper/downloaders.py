#!/user/bin/env python3

import requests
import tarfile
from os import remove


def bytes_file_downloader(file_url, download_path):
    """
    Downloads a file to local storage.

    :param file_url: URL of file to download
    :type file_url:
    :param download_path: directory to download file to
    :type download_path:
    :return: path to downloaded file
    :rtype:
    """
    file_path = download_path + file_url.split('/')[-1]

    with requests.get(file_url, allow_redirects=True) as r:
        with open(file_path, 'xb') as file_writer:
            file_writer.write(r.content)
    return file_path


def archive_downloader(file_url, download_path):
    """
    Downloads an archive to local storage and extracts it. Supported extensions:
    - .tar.gz

    Note: Archive file will be removed during/after extraction.

    :param file_url: URL of file to download
    :type file_url:
    :param download_path: directory to download file to
    :type download_path:
    :return: path to downloaded file
    :rtype:
    """
    file_path = bytes_file_downloader(file_url, download_path)

    if file_path.endswith('.tar.gz'):
        with tarfile.open(file_path, "r:gz") as archive:
            
            import os
            
            def is_within_directory(directory, target):
                
                abs_directory = os.path.abspath(directory)
                abs_target = os.path.abspath(target)
            
                prefix = os.path.commonprefix([abs_directory, abs_target])
                
                return prefix == abs_directory
            
            def safe_extract(tar, path=".", members=None, *, numeric_owner=False):
            
                for member in tar.getmembers():
                    member_path = os.path.join(path, member.name)
                    if not is_within_directory(path, member_path):
                        raise Exception("Attempted Path Traversal in Tar File")
            
                tar.extractall(path, members, numeric_owner=numeric_owner) 
                
            
            safe_extract(archive, path=download_path)
    else:
        raise ValueError('Unsupported archive format.')

    remove(file_path)

