#! /usr/bin/env python26
#-*- coding: utf-8 -*-
"""
CHATBOT en Google Talk
"""
import sys
import xmpp
import sqlite3

from primary import chatbotini
from primary.chatbotio import write_to_file


def present_controller(conn, presence):
    """
    Handler for automatically adding users to jabber servers (gtalk).
    """
    if presence:
        try:
            if presence.getFrom().getStripped() != chatbotini.LOGINGTALK:
                print "-" * 100
                print "%s,%s,%s,%s,%s" % (
                    presence.getFrom().getStripped(),
                    presence.getFrom().getResource(),
                    presence.getType(),
                    presence.getStatus(),
                    presence.getShow())
                print "~" * 100

        except UnicodeEncodeError:
            print "-" * 100
            print "%s,%s,%s,Cannot show nick,%s" % (
                presence.getFrom().getStripped(),
                presence.getFrom().getResource(),
                presence.getType(),
                presence.getShow())
            print "~" * 100

        if presence.getType() == "subscribe":
            jid = presence.getFrom().getStripped()
            chatbotini.MY_LIST.Authorize(jid)


def chatregistry(message, email):
    """
    Logs the chat.
    """
    filename = "%s/gtalk/%s" % (config.common.log, email)
    write_to_file(filename, message)


def step_on(conn):
    """
    Keeps the connection alive.
    """
    try:
        conn.Process(1)
    except KeyboardInterrupt:
        chatbotini.connection_log(
            "Keyboard Interrupt (Ctrl+C)\n", "gtalk")
        disconnect_bot()
    return 1


def loop_start(conn):
    """
    Starts the loop.
    """
    while step_on(conn):
        show.setShow("ax")
        conn.send(show)


def disconnect_bot():
    """
    Quit and disconnect the bot.
    """
    print "Exiting."
    chatbotini.connection_log("Session terminated\n\n\n", "gtalk")
    sys.exit(0)


def cache_read_rpta(email):
    """
    Reads the cache
    """
    ans = 0

    frace = read_file("%s/%s_1.txt" % (config.gtalk.cache, str(email)))

    if frace.count("How old are you") > 0 or \
            frace.count("What's your age"):
        ans = 1

    return ans


def cache_write_ans(message, email):
    """
    Writes to the cache
    """
    write_to_file("%s/%s_1.txt" % (config.gtalk.cache, str(email)), message)


def gtalk_ans(conn, mess):
    """
    Respond to messages from gtalk contacts.
    """
    logtime = config.now()
    text = mess.getBody()
    #so you can convert to lower case

    substitutions = [
        (u"\xe1", u"a"),
        (u"\xe9", u"e"),
        (u"\xed", u"i"),
        (u"\xf3", u"o"),
        (u"\xfa", u"u"),
        ("+", " mas ")]
    for search, replacement in substitutions:
        text = text.replace(search, replacement)

    #text = text.replace(u"\xbf",u"") ##u"\xbf" = ¿
    user = mess.getFrom()
    user.lang = "en"   # dup
    senderemail = user.getStripped()

    try:
        message = text.lower().replace("\n", " ").encode("utf-8")
    except AttributeError:
        message = ""

    # Log query message
    chatregistry(("%s <<< %s\n" % (logtime, message)), senderemail)

    remsg = chatbotini.action_process(
        message, senderemail, conn=conn, mess=mess)

    #stores the questions that have no answers
    record_questions_unanswered(
        message, remsg, senderemail, logtime[1:11], logtime[12:20])

    if remsg:
        extramsg = u""

        if cache_read_rpta(senderemail) == 1:
            # try except really needed?
            try:
                age = int(text)

            # TODO: find exception type
            except:
                pass

            else:
                if age < 5:
                    extramsg = u"So young and you know how to write?"
                if age > 95:
                    extramsg = u"Wow! You are the oldest person i've meet"

        message = xmpp.Message(
            to=mess.getFrom(), body=extramsg.encode("utf-8") + remsg,
            typ="chat")
        conn.send(unicode(message).encode("utf-8").replace(r"\n", "\n"))

    # Log response message
    # TODO: move unneded code out of the try block
    try:
        message = message.getBody()
    except AttributeError:
        pass
    else:
        chatregistry(
            ("%s >>> %s\n" % (logtime, message.encode("utf-8"))), senderemail)

    cache_write_ans(remsg, senderemail)


def record_questions_unanswered(message, answer, email, date, time):
    """
    Records Unanswered Questions
    """
    unanswered = read_file_lines("unanswered.txt")
    answer_random = [elem.split("\n") for elem in unanswered]

    for data in answer_random:
        if data in unanswered:
            data = (email, date, time, unicode(message, "UTF-8"), 0)
            #print data
            conn = sqlite3.connect("show_unanswered.bd")
            conn_cursor = conn.cursor()
            conn_cursor.execute(
                """insert into preguntas values(?,?,?,?,?)""", data)
            conn.commit()
            conn_cursor.close()
            conn.close()


if __name__ == "__main__":
    print "\n\n* ChatBot Gtalk Client *\n"
    config = Config()

    conn = xmpp.Client(config.gtalk.server, debug=[])
    show = xmpp.Presence()

    # Show: dnd, away, ax
    show.setShow("ax")
    conres = conn.connect(server=("talk.google.com", 5223))

    chatbotini.connection_log("Initializing session\n", "gtalk")
    chatbotini.connection_log(
        "Connecting to server (talk.google.com)\n", "gtalk")

    if not conres:
        print "Cannot connect to server %s!" % config.gtalk.server

        chatbotini.connection_log(
            "Unable to connect to jabber server (%s)\n" % (
                config.gtalk.server), "gtalk")
        chatbotini.connection_log("Ending\n\n\n", "gtalk")

        sys.exit(1)

    if conres != "tls":
        print (
            "Warning: Cannot establish secure connection - TLS failed")

    authres = conn.auth(config.gtalk.login.split("@")[0],
                        config.gtalk.password,
                        config.gtalk.name)

    chatbotini.connection_log("Authenticating\n", "gtalk")

    if not authres:
        print "Cannot authenticate to %s - check username and password." % (
            config.gtalk.server)

        chatbotini.connection_log("Login/Password incorrect\n", "gtalk")
        chatbotini.connection_log("Terminating\n\n\n", "gtalk")

        sys.exit(1)

    if authres != "sasl":
        # FIXME
        print """Warning: SASL authentication cannot you %s.
        Old method of authentication used!""" % config.gtalk.server

    conn.RegisterHandler("message", gtalk_ans)
    conn.RegisterHandler("presence", present_controller)
    conn.sendInitPresence()
    conn.send(show)

    chatbotini.MY_LIST = conn.getRoster()

    print "Gtalk Login OK"
    chatbotini.connection_log("Session initialized\n", "gtalk")

    # Starts Application
    loop_start(conn)
