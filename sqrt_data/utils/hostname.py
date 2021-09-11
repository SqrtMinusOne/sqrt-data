import os
import socket

__all__ = ['get_hostname']


def get_hostname():
    return os.environ.get('ANDROID_PHONE', socket.gethostname())
