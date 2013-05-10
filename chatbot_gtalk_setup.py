#! /usr/bin/env python
#-*- coding: utf-8 -*-
"""
CHATBOT en Google Talk
"""
import sys
import xmpp
import sqlite3

from primary import chatbotini
from primary.chatbotio import write_to_file


def presence_controller(conn, presence):
    """
    Handler for automatically adding users to jabber servers (gtalk).
    :rtype : Bool
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



def chat_registrar(message, email):
    """
    Logs the chat.
    :rtype : Bool
    """
    filename = "%s/gtalk/%s" % (config.common.log, email)
    write_to_file(filename, message)


def step_on(conn):
    """
    Keeps the connection alive.
    :rtype : Bool
    """
    try:
        conn.Process(1)
    except KeyboardInterrupt:
        chatbotini.connection_log(
            "Keyboard Interrupt (Ctrl+C)\n", "gtalk")
        disconnect_bot()
    return True


def loop_start(conn):
    """
    Starts the loop.
    :rtype : Bool
    """
    while step_on(conn):
        show.setShow("ax")
        conn.send(show)


def disconnect_bot():
    """
    Quit and disconnect the bot.
    :rtype : Bool
    """
    print "Exiting."
    chatbotini.connection_log("Session terminated\n\n\n", "gtalk")
    sys.exit(0)


def cache_read_reply(email):
    """
    Reads the cache
    :rtype : Bool
    """
    reply = False
    try:
        cache = open(
            "%s%s_1.txt" % (chatbotini.CACHEDIR, str(email)), "r")
        fraze = cache.read()
    except IOError:
        pass
    else:
        if fraze.count("cuantos años tienes") > 0 or\
           fraze.count("y cual es tu edad"):
            reply = True
        cache.close()
    return reply


def cache_write_reply(message, email):
    """
    Writes to the cache
    :rtype : object
    """
    cache = False
    try:
        cache = open(
            chatbotini.CACHEDIR + str(email) + "_1.txt", "w")
        cache.write(message)
    except IOError:
        cache = False
    finally:
        cache.close()


def reply_gtalk(conn, mess):
    """
    Respond to messages from gtalk contacts.
    """
    log_time = chatbotini.now()
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
    sender_email = user.getStripped()

    try:
        message = text.lower().replace("\n", " ").encode("utf-8")
    except AttributeError:
        message = ""

    # Log query message
    chat_registrar(("%s <<< %s\n" % (log_time, message)), sender_email)

    re_msg = chatbotini.action_process(
        message, sender_email, conn=CONN, mess=mess)

    #stores the questions that have no answers
    record_questions_unanswered(
        message, sender_email, log_time[1:11], log_time[12:20])
    if re_msg:
        extra_msg = u""
        if cache_read_reply(sender_email):
            # try except really needed?
            try:
                age = int(text)
            except Exception:
                pass
            else:
                if age < 5:
                    extra_msg = u"Tan joven y ya sabes escribir?"
                if age > 95:
                    extra_msg = (u"Vaya eres la persona más longeva que" +
                                u"estoy conociendo!")
        message = xmpp.Message(
            to=mess.getFrom(), body=extra_msg.encode("utf-8") + re_msg,
            typ="chat")
        conn.send(unicode(message).encode("utf-8").replace(r"\n", "\n"))

    # Log response message
    try:
        message = message.getBody()
        chat_registrar(
            ("%s >>> %s\n" % (log_time, message.encode("utf-8"))), sender_email)
    except AttributeError:
        pass
    else:
        chatregistry(
            ("%s >>> %s\n" % (logtime, message.encode("utf-8"))), senderemail)
    cache_write_reply(re_msg, sender_email)


def record_questions_unanswered(message, email, date, time):
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
    config = chatbotini.Config()
    conn = xmpp.Client(config.gtalk.server, debug=[])
    show = xmpp.Presence()

    # Show: dnd, away, ax
    SHOW.setShow("ax")
    CON_RES = CONN.connect(server=("talk.google.com", 5223))
    chatbotini.connection_log("Initializing session\n", "gtalk")
    chatbotini.connection_log(
        "Connecting to server (talk.google.com)\n", "gtalk")
    if not CON_RES:
        print "No se puede conectar al servidor %s!" % chatbotini.SERVER
        chatbotini.connection_log(
            "Unable to connect to jabber server (%s)\n" % (
                config.gtalk.server), "gtalk")
        chatbotini.connection_log("Ending\n\n\n", "gtalk")
        sys.exit(1)

    if CON_RES != "tls":
        print(
            "Advertencia: no se puede estabilizar conexion segura - TLS fallo")
    AUTHKEY = CONN.auth(chatbotini.LOGINGTALK.split("@")[0],
        chatbotini.LOGINPASSWORD,
        chatbotini.BOTNAME)
    chatbotini.connection_log("Authenticating\n", "gtalk")

    if not AUTHKEY:
        print("No se puede autorizar en %s - comprobar " +
              "nombre de usuario / contrasenia.") % chatbotini.SERVER
        chatbotini.connection_log("Login/Password incorrect\n", "gtalk")
        chatbotini.connection_log("Terminating\n\n\n", "gtalk")
        sys.exit(1)

    if AUTHKEY != "sasl":
        print """Warning: SASL authentication can not you% s.
        Old method of authentication used!""" % chatbotini.SERVER
    CONN.RegisterHandler("message", reply_gtalk)
    CONN.RegisterHandler("presence", presence_controller)
    CONN.sendInitPresence()
    CONN.send(SHOW)

    chatbotini.MY_LIST = conn.getRoster()

    print "Gtalk Login OK"
    chatbotini.connection_log("Session initialized\n", "gtalk")

    # Starts Application
    loop_start(conn)
