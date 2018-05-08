#!/usr/bin/env python
# -*- encoding=utf8 -*-

'''
FileName:   system.py
Author:     Fasion Chan
@contact:   fasionchan@gmail.com
@version:   $Id$

Description:

Changelog:

'''

import os
import platform

from libase.decorator.helper import (
    eval_now,
)


class System(object):

    OS_TYPE_LINUX = 'linux'
    OS_TYPE_WINDOWS = 'windows'

    LSB_RELEASE_PATH = '/etc/lsb-release'
    DEBIAN_VERSION_PATH = '/etc/debian_version'
    REHAT_RELEASE_PATH = '/etc/redhat-release'

    @eval_now
    def os_type():
        os = platform.system().lower()
        return os

    distro = None
    distro_release = None
    kernel_version = None

    def __init__(self):
        self._init(os_type=self.os_type)

        self.fetch_distro()

    def fetch_distro(self):
        (
            self.fetch_lsb_release() or
            self.fetch_debian_release() or
            self.fetch_rehat_release() or
            None
        )

    def fetch_lsb_release(self):
        if not os.path.exists(self.LSB_RELEASE_PATH):
            return False

        data = {}
        with open(self.LSB_RELEASE_PATH) as f:
            for line in f:
                field, value = line.split('=')
                field, value = field.strip(), value.strip()

                if field == 'DISTRIB_ID':
                    self.distro = value

                if field == 'DISTRIB_RELEASE':
                    self.distro_release = value

        return bool(self.distro) and bool(self.distro_release)

    def fetch_debian_release(self):
        if not os.path.exists(self.DEBIAN_VERSION_PATH):
            return False

        with open(self.DEBIAN_VERSION_PATH) as f:
            self.distro_release = f.read().strip()
            self.distro = 'Debian'

        return bool(self.distro_release)

    def fetch_rehat_release(self):
        if not os.path.exists(self.REHAT_RELEASE_PATH):
            return False

        with open(self.REHAT_RELEASE_PATH) as f:
            fields = f.read().strip().split()

            self.distro = fields[0]
            self.distro_release = fields[2]

        return bool(self.distro) and bool(self.distro_release)

    @property
    def is_linux(self):
        return self.os_type == self.OS_TYPE_LINUX

    @property
    def is_windows(self):
        return self.os_type == self.OS_TYPE_WINDOWS

    def _init_uname(self):
        uname = os.uname()

        self.kernel_version = uname[2]

    def _init(self, os_type):
        init_handler_name = '_init_{os_type}'.format(os_type=os_type)
        getattr(self, init_handler_name, self._init_fake)()

    def _init_linux(self):
        self._init_uname()

    def _init_darwin(self):
        self._init_uname()

    def _init_windows(self):
        from wmi import WMI

        wmi = WMI()
        os, = wmi.Win32_OperatingSystem()

        self.distro = os.Caption
        self.distro_release = os.BuildNumber
        self.kernel_version = os.Version

    def _init_fake(self):
        self
