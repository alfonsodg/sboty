#!/usr/bin/env python
#-*- coding: utf-8 -*-
"""
Common functions and constants for both bots.
"""
import os
from datetime import datetime

import aiml

from chatbotconfig import Config
from chatbotio import write_to_file


class ChatBot(object):
    """
    ChatBot object
    """
    def __init__(self):
        """
        Initialization
        """
        self.my_list = None
        self.use_brain = True

        self._config = Config()
        self._set_files()
        self._brain_conf()

    @property
    def brain(self):
        """
        Run getter
        """
        return self._kernel

    @propery
    def config(self):
        """
        config getter
        """
        return self._config

    def _set_files(self):
        """
        Create files and needed directories
        """
        # Create empty command cache file if doesn't exist
        if not os.path.exists('%s/mencache.txt' % config.common.cache):
            write_to_file('%s/mencache.txt' % config.common.cache, str({}))

        # Create directories (if missing)
        directories = ['%s' % config.common.cache,
                       '%s/msn' % config.common.log,
                       '%s/gtalk' % config.common.log]
        for directory in directories:
            os.mkdir(directory)


    def _brain_conf(self):
        """
        Configure Brain
        """
        self._kernel = aiml.Kernel()

        for option in self._config.common.ini_config.options:
            self._kernel(
                option, getattr(self._config.common.ini_config, option))

        configure(self._config.common.ini_config, self._kernel)
        self._kernel.verbose(False)

        # Load Brain
        if self._use_brain and os.path.isfile(self._config.common.brain):
            self._kernel.bootstrap(brainFile=self._config.common.brain)
        else:
            self._kernel.bootstrap(
                learnFiles='ia_start.xml', commands='load aiml b')
            self._kernel.saveBrain(self._config.common.brain)


def connection_log(message, bot):
    """
    Log msn/gtalk connection events.
    """
    if bot == 'msn':
        filename = LOGDIR + '/msn_events'

    elif bot == 'gtalk':
        filename = LOGDIR + '/gtalk_events'

    # TODO: embed into an exception block
    logfile = open(filename, 'a')
    logfile.write(now() + ' ' + message)
    logfile.close()


def configure(configfile, brainer):
    """
    Bot properties configuration.
    """
    # Setup bot properties such name, birthplace, etc.

    fil = open(configfile)
    opt = fil.readlines()
    fil.close()

    for elem in opt:
        par = elem.split('=')

        if len(par) == 2:
            brainer.setBotPredicate(par[0].strip(), par[1].strip())


def remove_cache(senderemail):
    """
    Remove the cache file.
    """
    try:
        os.remove(CACHEDIR + str(senderemail) + '.txt')

    except OSError:
        pass


def action_process(message, senderemail, **kwargs):
    """
    Perform the particular action for the given command.
    """
    remove_cache(senderemail)

    if CHATBOT.getPredicate('name', senderemail) == '':
        dispname = senderemail.split('@')

        if len(dispname) == 2:
            CHATBOT.setPredicate('name', dispname[0], senderemail)

    remsg = CHATBOT.respond(message, senderemail)
    remsg = getheader() + remsg + getfooter()

    if not remsg:
        remsg = u"Sorry, can't understand.".encode('utf-8')

    return remsg


def getheader():
    """
    Returns the header.
    """
    return ''


def getfooter():
    """
    Returns the footer.
    """
    return ''
