#!/usr/bin/env python
#-*- coding: utf-8 -*-
"""
Common functions and constants for both bots.
"""
import os
from datetime import datetime

import aiml

from chatbotconfig import Config

# TODO: use __name__ trick if possible

#ELEMENT = xmlfunctions.xmltodict('chatbot_settings.xml')

# Main settings
LOGINGTALK = ELEMENT['setup']['loginusergtalk']
LOGINEMAILMSN = ELEMENT['setup']['loginusermsn']
LOGINPASSWORD = ELEMENT['setup']['loginpasswordgtalk']
LOGINPASSWORDMSN = ELEMENT['setup']['loginpasswordmsn']
EMAIL_SENDER = ELEMENT['setup']['emailsender']
SERVER = ELEMENT['setup']['jabberserver']
BOTNAME = ELEMENT['setup']['botname']
BRAIN = ELEMENT['setup']['botconf']['brain']
MSNINI = ELEMENT['setup']['botconf']['msnini']
LOGPATH = ELEMENT['setup']['path']['logpath']
CACHEPATH = ELEMENT['setup']['path']['cachepath']
MY_LIST = None

# Initializes basic configurations for bot sessions
ROOTDIR = os.getcwd()
CONFIGFILE = '%s/%s' % (ROOTDIR, MSNINI)
LOGDIR = '%s/%s' % (ROOTDIR, LOGPATH)
CACHEDIR = '%s/%s/' % (ROOTDIR, CACHEPATH)


# Create empty command cache file if doesn't exist
if not os.path.exists(CACHEDIR + 'mencache.txt'):
    command_cachefile = open(CACHEDIR + 'mencache.txt', 'w')
    command_cachefile.write(str({}))
    command_cachefile.close()

# Create directories (if missing)
os.system('mkdir -p %s' % CACHEDIR)
os.system('mkdir -p %s/msn' % LOGDIR)
os.system('mkdir -p %s/gtalk' % LOGDIR)

USE_BRAIN = True


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


# Initialization
CHATBOT = aiml.Kernel()
configure(CONFIGFILE, CHATBOT)
CHATBOT.verbose(False)

# Load brain
if USE_BRAIN and os.path.isfile(BRAIN):
    CHATBOT.bootstrap(brainFile=BRAIN)

else:
    CHATBOT.bootstrap(learnFiles='ia_start.xml', commands='load aiml b')
    CHATBOT.saveBrain(BRAIN)
