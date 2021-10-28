# [[file:../../org/index.org::*Hostname][Hostname:1]]
import os
import socket

__all__ = ['get_hostname']


def get_hostname():
    return os.environ.get('ANDROID_PHONE', socket.gethostname())
# Hostname:1 ends here
