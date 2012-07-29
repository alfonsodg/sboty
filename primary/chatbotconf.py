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
        config = SafeConfigParser
        config.read('chatbot.cfg')

        self._common = Section('common')

        self._accounts = self._get_accounts(config)

        for account in self._accounts:
            aconfig = Section(config, account)
            setattr(self, account, aconfig)


    class Section(object):
        """
        Section class. Read seccions from chatbot.cnf
        Returns an object with:
            object.option = value
        """
        def __init__(self, config, name):
            for section in config.options(name)
                setattr(self, section, config.get(name, section))


    @staticmethod
    def _get_accounts(config):
        accounts = config.sections()
        accounts.remove('common')
        return accounts

    @staticmethod
    def now():
        """
        Returns the current date and time.
        """
        now = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        ret = '[%s]' % (now)

        return ret

    @property
    def accounts(self):
        return self._accounts

