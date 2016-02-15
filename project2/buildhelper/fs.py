#!/usr/bin/env python

import os
import itertools


def ls(dir_path):
    """
    Return ([dir path], [file path]) in given dir_path excluding '.' and '..' non-recursively.
    """
    def entry_bucket((dirs, files), entry):
        entry_path = os.path.join(dir_path, entry)
        if os.path.isdir(entry_path):
            dirs.append(entry_path)
        else:
            files.append(entry_path)

        return (dirs, files)

    return reduce(entry_bucket, os.listdir(dir_path), ([], []))


def is_c_cpp_source(file_path):
    """
    Check if the given file_path is a C/C++ source file.
    """
    exts = ('.c', '.cc', '.cpp')
    return any(itertools.imap(
        lambda ext: file_path.endswith(ext), exts))


def c_cpp_sources(dir_path):
    """
    Return [file path] in given dir_path.
    Valid source extensions are .c / .cc / .cpp
    """
    _, files = ls(dir_path)
    return filter(is_c_cpp_source, files)


def dirs_c_cpp_sources(dir_path):
    """
    Return dirs and C/C++ sources under dir_path with recursive.
    """
    dirs, files = ls(dir_path)
    return (dirs, filter(is_c_cpp_source, files))


def replace_top_dir(old_path, new_top):
    """
    Replace the top dir of path.
    E.g.
    '/a/b/', 'new_top' -> 'new_top/a/b/'
    'a/b', 'new_top' -> 'new_top/b'
    'a', 'new_top' -> 'new_top/a'
    """
    return os.path.join(new_top, old_path[old_path.find(os.sep) + 1:])
