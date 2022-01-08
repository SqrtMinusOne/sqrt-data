# [[file:../../org/core.org::*Hostname][Hostname:1]]
import os
import socket

__all__ = ['get_hostname', 'is_android']

def is_android():
    return os.environ.get('ANDROID_PHONE') is not None

def get_hostname():
    return os.environ.get('ANDROID_PHONE', socket.gethostname())
# Hostname:1 ends here
