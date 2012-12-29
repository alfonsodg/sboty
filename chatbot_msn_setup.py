#!/usr/bin/env python26
#-*- coding: utf-8 -*-
"""
CHATBOT MSN Client
"""

import sys
import os
import socket
import select
import urllib
import time

from msn_lib import msnlib
from msn_lib import msncb

from primary import chatbotini

# Basic classes
MSN = msnlib.msnd()
MSN.cb = msncb.cb()


class Use_Function():
    """
    Useful functions
    """
    def __init__(self):
        """Start"""
        pass

    def do_login(self, email, log_type, msg):
        """
        Performs the chat log.
        """
        if CONFIG["log history"]:
            logfile = "%s/%s" % (CONFIG["history directory"], email)
            lines = '\n'
            if log_type == "in":
                lines = "%s <<< %s\n" % (chatbotini.now(), str(msg))
            elif log_type == "out":
                lines = "%s >>> %s\n" % (chatbotini.now(), str(msg))

            file_dict = open(logfile, "a")
            file_dict.write(lines)
            file_dict.close()

    def null(self, sample):
        """
        Null function, useful to void debug ones.
        """
        pass

    def email_to_nick(self, email):
        """
        Returns a nick using the given email, or None if nobody matches.
        """
        if email in MSN.users.keys():
            return MSN.users[email].nick
        else:
            return None

    def get_configure(self):
        """
        Parses the configuration, returns a var:value dict.
        """
        config = {"email": chatbotini.LOGINEMAILMSN,
                  "password": chatbotini.LOGINPASSWORDMSN}
        return config

    def quit(self, code=0):
        """
        Signs out from MSN.
        """
        print "Closing"
        chatbotini.connection_log("Sesion terminada\n\n\n", "msn")

        try:
            MSN.disconnect()

        # TODO: Add exception type
        except:
            pass

        sys.exit(code)


class Server_Disconnect():
    """
    Server disconnect
    """
    def __init__(self):
        """Start"""
        pass

    def cb_errors(self, md1, err_no, params):
        """
        Handles server errors.
        """
        if not err_no in msncb.error_table:
            desc = "Unknown"
        else:
            desc = msncb.error_table[err_no]

        desc = "\rServer sent error %d: %s\n" % (err_no, desc)
        print desc

        msncb.cb_err(md1, err_no, params)

    def cb_adding(self, md1, data_type, tid, params):
        """
        Handler for adding users.
        """
        plist = params.split(" ")
        if not data_type:
            data_type = plist[0]
        email = ''
        nick = ''

        if data_type == "RL" or data_type == "FL":
            email = plist[2]
            nick = urllib.unquote(plist[3])

        if data_type == "RL":
            out = "\r%s (%s) has added you to his contact list" % (email, nick)
            print out

            email = params.split(" ")[2]
            MSN.useradd(email)  # Automatically adds the user

            try:
                MSN.userunblock(email.strip())

            except KeyError:
                pass

        elif data_type == "FL":
            out = "\r%s (%s) has been added to your contact list" % (
                email, nick)
            print out

        msncb.cb_add(md1, data_type, tid, params)

    def cb_messages(self, md1, data_type, tid, params, sbd):
        """
        Handles MSN messages.
        """
        global LAST_RECEIVED
        plist = tid.split(" ")
        email = plist[0]
        if not data_type:
            data_type = False
        # Parse
        lines = params.split("\n")
        headers = {}
        eoh = 0

        for line in lines:
            # End of headers
            if line == "\r":
                break

            tvv = line.split(":", 1)
            data_type = tvv[0]
            value = tvv[1].strip()
            headers[data_type] = value
            eoh += 1

        eoh += 1

        # Handle special hotmail messages
        if email == "Hotmail":
            if not "Content-Type" in headers:
                return

            hotmail_info = {}

            # Parse the body
            for line in lines:
                line = line.strip()

                if not line:
                    continue

                tvv = line.split(":", 1)
                data_type = tvv[0]
                value = tvv[1].strip()
                hotmail_info[data_type] = value

            msnlib.debug(params)

            if headers["Content-Type"] == ("text/x-msmsgsinitialemail" +
                                           "notification; charset=UTF-8"):
                new_messages = int(hotmail_info["Inbox-Unread"])

                if not new_messages:
                    return

                print("\rYou have %s unread email(s)" +
                      " in your Hotmail account") % str(new_messages)

            elif headers["Content-Type"] == ("text/" +
                                             "x-msmsgsemailnotification;" +
                                             " charset=UTF-8"):
                from_name = hotmail_info["From"]
                from_address = hotmail_info["From-Addr"]
                subject = hotmail_info["Subject"]

                print("\rYou have just received an email in your" +
                      " Hotmail account:")
                print "\r\tFrom: %s (%s)" % (from_name, from_address)
                print "\r\tSubject: %s" % subject
            return

        if "Content-Type" in headers and \
                headers["Content-Type"] == "text/x-msmsgscontrol":
            nick = USE_FUNCTION.email_to_nick(email)
            #if not nick:
            #    nick = email

            if not "typing" in MSN.users[email].priv:
                MSN.users[email].priv["typing"] = 0

            if not MSN.users[email].priv["typing"] and email not in IGNORED:
                # When typing
                pass

            MSN.users[email].priv["typing"] = time.time()

        elif "Content-Type" in headers and \
                headers["Content-Type"] == "text/x-clientcaps":
            pass

        elif "Content-Type" in headers and \
                headers["Content-Type"] == "text/x-keepalive":
            pass

        else:
            # Messages
            MSN.users[email].priv["typing"] = 0
            display_message(email, lines, eoh)

            if len(HISTORY_BUFFER) > CONFIG["history size"]:
                del(HISTORY_BUFFER[0])

            HISTORY_BUFFER.append((time.time(), email, lines[eoh:]))

        LAST_RECEIVED = email
        msncb.cb_msg(md1, type, tid, params, sbd)

    def cb_disconnect(self, md1, type, tid, params):
        """
        When the server disconnect us from MSN.
        """
        print("\rServer sent disconnect" +
              " (probably you logged in somewhere else)")

        USE_FUNCTION.quit()
        msncb.cb_out(md1, type, tid, params)

    def cb_join(self, md1, type, tid, params, sbd):
        """
        Join a conversation and send pending messages.
        """
        email = tid
        nick = USE_FUNCTION.email_to_nick(email)

        if not nick:
            nick = email

        if sbd.emails and email != sbd.emails[0]:
            first_nick = USE_FUNCTION.email_to_nick(sbd.emails[0])

            if not first_nick:
                first_nick = sbd.emails[0]

            print "\rUser %s has joined the chat with %s" % (nick, first_nick)

        elif len(sbd.msgqueue) > 0:
            print "\rFlushing messages for %s:" % nick

            for msg in sbd.msgqueue:
                print nick, msg

        msncb.cb_joi(md1, type, tid, params, sbd)


def display_message(email, lines, eoh=0):
    """
    Prints an incoming message and an optional pointer at the
    end of your header.
    :rtype : Bool
    """
    message = ""

    substitutions = [
        ("\xc3\xb1", "n"),
        ("\xc3\xa1", "a"),
        ("\xc3\xa9", "e"),
        ("\xc3\xad", "i"),
        ("\xc3\xb3", "o"),
        ("\xc3\xba", "u")]

    for line in lines[-1:]:
        for search, replacement in substitutions:
            line = line.replace(search, replacement)

        message += line.strip() + " "

    message = message.strip().decode("utf-8", "ignore")

    # Log query message
    USE_FUNCTION.do_login(email, "in", message.encode("utf-8"))
    message_to_send = chatbotini.action_process(message, email, msn=MSN)

    # We really need to add empty string??
    extra_message = u""
    message_to_send += extra_message.encode("utf-8")

    MSN.sendmsg(email, message_to_send.replace(r"\n", "\n"))

    # Log response message
    USE_FUNCTION.do_login(email, "out", message_to_send)


if __name__ == "__main__":
    # TODO: split into functions
    # classes start
    USE_FUNCTION = Use_Function()
    SERVER_DISCONNECT = Server_Disconnect()

    MSN.cb.out = SERVER_DISCONNECT.cb_disconnect
    MSN.cb.msg = SERVER_DISCONNECT.cb_messages
    MSN.cb.joi = SERVER_DISCONNECT.cb_join
    MSN.cb.err = SERVER_DISCONNECT.cb_errors
    MSN.cb.add = SERVER_DISCONNECT.cb_adding

    print "\n\n* ChatBot MSN Client *\n"
    chatbotini.connection_log("Iniciando sesion\n", "msn")

    # First, the configuration
    print "Loading config... "

    CONFIG = USE_FUNCTION.get_configure()
    CONFIG["profile"] = None

    # Set the mandatory values
    MSN.email = CONFIG["email"]
    MSN.pwd = CONFIG["password"]

    if not "history size" in CONFIG:
        CONFIG["history size"] = 10

    else:
        try:
            CONFIG["history size"] = int(CONFIG["history size"])

        except:
            print "history size must be integer, using default"
            CONFIG["history size"] = 10

    # Input history size
    if not "input history size" in CONFIG:
        CONFIG["input history size"] = 10

    else:
        try:
            CONFIG["history size"] = int(CONFIG["history size"])

        except:
            print "input history size must be integer, using default"
            CONFIG["input history size"] = 10

    # Initial status
    CONFIG["initial status"] = "online"

    # Debug
    CONFIG["debug"] = 0

    # Log history
    CONFIG["log history"] = 1

    # History directory
    CONFIG["history directory"] = chatbotini.LOGDIR + "/msn"

    # Show realnick changes
    if not "show realnick changes" in CONFIG:
        CONFIG["show realnick changes"] = 0

    elif CONFIG["show realnick changes"] != "yes":
        CONFIG["show realnick changes"] = 0

    # Encoding
    if not "encoding" in CONFIG:
        if "LC_ALL" in os.environ and os.environ["LC_ALL"]:
            CONFIG["encoding"] = os.environ["LC_ALL"]

        elif "LANG" in os.environ and os.environ["LANG"]:
            CONFIG["encoding"] = os.environ["LANG"]

        else:
            CONFIG["encoding"] = "iso-8859-1"

    MSN.encoding = CONFIG["encoding"]

    print "Done!"

    # Set or void the debug
    if not CONFIG["debug"]:
        msnlib.debug = USE_FUNCTION.null
        msncb.debug = USE_FUNCTION.null

    # Login to msn
    print "Logging in... "
    chatbotini.connection_log("Autenticando\n", "msn")
    try:
        MSN.login()
        print "Done!"

    except KeyboardInterrupt:
        chatbotini.connection_log(
            "Interrupcion de teclado (Ctrl + C)\n", "msn")
        USE_FUNCTION.quit()

    except socket.error, info:
        print "Network error: %s" % str(info)
        print "Closing"

        chatbotini.connection_log("Error de red (%s)\n" % str(info), "msn")
        chatbotini.connection_log("Terminando\n\n\n", "msn")
        sys.exit(1)

    except Exception, info:
        print "Exception logging in"
        print "Error: %s" % str(info)
        print "Closing"

        chatbotini.connection_log(str(info) + "\n", "msn")
        chatbotini.connection_log("Terminando\n\n\n", "msn")

        sys.exit(1)

    # Call sync to get the lists and refresh
    print "Sending user list request... "
    if MSN.sync():
        print "Done!"
        LIST_COMPLETE = 0

    else:
        print "Error syncing users"

    # Global variables
    HISTORY_BUFFER = []    # History buffer
    LAST_RECEIVED = ""   # Email of the last person we received a message from
    IGNORED = []         # People being locally ignored

    # Loop
    while 1:
        FDS = MSN.pollable()
        INFD = FDS[0]
        OUTFD = FDS[1]
        INFD.append(sys.stdin)

        try:
            FDS = select.select(INFD, OUTFD, [], 5)

        except KeyboardInterrupt:
            chatbotini.connection_log(
                "Interrupcion de teclado (Ctrl + C)\n", "msn")
            USE_FUNCTION.quit()

        for comp in FDS[0] + FDS[1]: # see msnlib.msnd.pollable.__doc__
            try:
                MSN.read(comp)

                # See if we got all the user list, so we can
                # change our initial status
                if not LIST_COMPLETE and MSN.lst_total == MSN.syn_total:
                    LIST_COMPLETE = 1

                    if MSN.change_status(CONFIG["initial status"]):
                        print "\rStatus set to %s" % CONFIG["initial status"]
                        chatbotini.connection_log("Sesion iniciada\n", "msn")

                    else:
                        print "\rError setting status: unknown status %s" % (
                            CONFIG["initial status"])

                    # Re-adding and Unblocking users just in case
                    contacts = MSN.users
                    for e_mail in contacts:
                        MSN.useradd(e_mail)
                        try:
                            MSN.userunblock(e_mail)

                        except KeyError:
                            pass

                # If not online then change the status
                if MSN.status != "NLN":
                    MSN.change_status("online")

            except socket.error, err:
                chatbotini.connection_log("Error en los sockets\n", "msn")

                if comp != MSN:
                    if comp.msgqueue:
                        nick = USE_FUNCTION.email_to_nick(comp.emails[0])
                        print("\rConnection with %s closed - the following" +
                              "messages couldn't be sent:") % nick

                        for message in comp.msgqueue:
                            print "\t>>> %s" % message

                    MSN.close(comp)

                else:
                    print "\nMain socket closed (%s)" % str(err)

                    chatbotini.connection_log(
                        "Se cerro el socket principal\n", "msn")

                    USE_FUNCTION.quit(1)
