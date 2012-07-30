
#!/usr/bin/env python
#-*- coding: utf-8 -*-
"""
Common I/O functions
Author: Nicolas Valcarcel <nvalcarcel@gmail.com>
"""


def write_to_file(filename, message):
    """
    Writes message to filename
    """
    try:
        f = open(filename, "a")
    except IOError:
        print "Cannot open %s" % filename
    else:
        f.write(message)
    finally:
        f.close()


def read_file(filename):
    """
    Reads filename. Returns file content or None if failed.
    """
    try:
        f = open(filename, "r")
    except IOError:
        ret = ""
    else:
        ret = f.read()
    finally:
        f.close()

    return ret


def read_file_lines(filename):
    """
    Reads filename. Returns file lines or None if failed.
    """
    try:
        f = open(filename, "r")
    except IOError:
        ret = [] 
    else:
        ret = f.readlines()
    finally:
        f.close()

    return ret
