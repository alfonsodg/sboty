#!/usr/bin/env python
#-*- coding: utf-8 -*-
"""
Common functions and constants for both bots.
"""
import os
from datetime import datetime

import aiml
import xmlfunctions

ELEMENT = xmlfunctions.xml_to_dict('chatbot_settings.xml')

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
    command_cache_file = open(CACHEDIR + 'mencache.txt', 'w')
    command_cache_file.write(str({}))
    command_cache_file.close()

# Create directories (if missing)
os.system('mkdir -p %s' % CACHEDIR)
os.system('mkdir -p %s/msn' % LOGDIR)
os.system('mkdir -p %s/gtalk' % LOGDIR)

USE_BRAIN = True


def now():
    """
    ChatBot object
    """
    today = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
    ret = '[%s]' % today
    return ret


def connection_log(message, bot):
    """
    Log msn/gtalk connection events.
    """
    filename = ''
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
        display_name = senderemail.split('@')
        if len(display_name) == 2:
            CHATBOT.setPredicate('name', display_name[0], senderemail)
    re_msg = CHATBOT.respond(message, senderemail)
    re_msg = getheader() + re_msg + getfooter()
    if not re_msg:
        re_msg = u"Sorry, can't understand.".encode('utf-8')
    return re_msg


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
