#!/usr/bin/env python
#-*- coding: utf-8 -*-
"""
Common functions and constants for both bots.
Author: Nicolas Valcarcel <nvalcarcel@gmail.com>
"""

from ConfigParser import SafeConfigParser
import os


class Config(object):
    """
    Configuration class. Reads chatbot.cfg.
    Returns and object with properties:
        - common
        - ACCOUNT_NAME
    """
    def __init__(self):
        """
        Initialize config object
        """
        config = SafeConfigParser()
        config.read('chatbot.cfg')

        self._common = Section(config, 'common')

        root = os.getcwd()
        if hasattr(self._common, 'log'):
            self._common.log = '%s/%s' % (root, self._common.log)
        else:
            self._common.log = '%s/log' % root

        if hasattr(self._common, 'cache'):
            self._common.cache = '%s/%s' % (root, self._common.cache)
        else:
            self._common.cache = '%s/cache' % root

        ini_config = SafeConfigParser()
        ini_config.read(self._common.msn_ini)

        self._common.msn_ini = Section(ini_config, 'DEFAULT')

        self._gtalk = Section(config, 'gtalk')
        self._msn = Section(config, 'msn')


    class Section(object):
        """
        Section class. Read seccions from chatbot.cnf
        Returns an object with:
            object.option = value
        """
        def __init__(self, config, name):
            self._options = []
            for option in config.options(name)
                setattr(self, option, config.get(name, option))
                self._options.append(option)

        @property
        def options(self):
            return self._options

    @staticmethod
    def now():
        """
        Returns the current date and time.
        """
        now = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        ret = '[%s]' % (now)

        return ret

    @property
    def common(self):
        return self._common

    @property
    def gtalk(self):
        return self._gtalk

    @property
    def msn(self):
        return self._msn
