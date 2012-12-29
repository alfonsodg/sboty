#! /usr/bin/env python26
#-*- coding: utf-8 -*-
"""
CHATBOT en Google Talk
"""
import sys
import xmpp
from primary import chatbotini
import sqlite3


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
            print "%s,%s,%s,No se puede mostrar nick,%s" % (
                presence.getFrom().getStripped(),
                presence.getFrom().getResource(),
                presence.getType(),
                presence.getShow())
            print "~" * 100

        if presence.getType() == "subscribe":
            jid = presence.getFrom().getStripped()
            chatbotini.MY_LIST.Authorize(jid)


def registrochat(message, email):
    """
    Logs the chat.
    """
    filename = chatbotini.LOGDIR + "/gtalk/" + email
    logfile = open(filename, "a")
    logfile.write(message)
    logfile.close()


def step_on(conn):
    """
    Keeps the connection alive.
    """
    try:
        conn.Process(1)
    except KeyboardInterrupt:
        chatbotini.connection_log(
            "Interrupcion de teclado (Ctrl+C)\n", "gtalk")
        disconnect_bot()
    return 1


def loop_start(conn):
    """
    Starts the loop.
    """
    while step_on(conn):
        SHOW.setShow("ax")
        CONN.send(SHOW)


def disconnect_bot():
    """
    Quit and disconnect the bot.
    """
    print "Exiting."
    chatbotini.connection_log("Sesion terminada\n\n\n", "gtalk")
    sys.exit(0)


def cache_read_rpta(email):
    """
    Reads the cache
    """
    rpta = 0
    try:
        cache = open(
            "%s%s_1.txt" % (chatbotini.CACHEDIR, str(email)), "r")
        frace = cache.read()
    except IOError:
        pass
    else:
        if frace.count("cuantos años tienes") > 0 or \
                frace.count("y cual es tu edad"):
            rpta = 1
        cache.close()
    return rpta


def cache_write_rpta(message, email):
    """
    Writes to the cache
    """
    try:
        cache = open(
            chatbotini.CACHEDIR + str(email) + "_1.txt", "w")
        cache.write(message)

    except IOError:
        pass

    finally:
        cache.close()


def rpta_gtalk(conn, mess):
    """
    Respond to messages from gtalk contacts.
    """
    logtime = chatbotini.now()
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
    registrochat(("%s <<< %s\n" % (logtime, message)), senderemail)

    remsg = chatbotini.action_process(
        message, senderemail, conn=CONN, mess=mess)

    #stores the questions that have no answers
    record_questions_unanswered(
        message, remsg, senderemail, logtime[1:11], logtime[12:20])

    if remsg:
        extramsg = u""

        if cache_read_rpta(senderemail) == 1:
            # try except really needed?
            try:
                anios = int(text)

            # TODO: find exception type
            except:
                pass

            else:
                if anios < 5:
                    extramsg = u"Tan joven y ya sabes escribir?"
                if anios > 95:
                    extramsg = (u"Vaya eres la persona más longeva que" +
                                u"estoy conociendo!")

        message = xmpp.Message(
            to=mess.getFrom(), body=extramsg.encode("utf-8") + remsg,
            typ="chat")
        CONN.send(unicode(message).encode("utf-8").replace(r"\n", "\n"))

    # Log response message
    # TODO: move unneded code out of the try block
    try:
        message = message.getBody()
        registrochat(
            ("%s >>> %s\n" % (logtime, message.encode("utf-8"))), senderemail)

    except AttributeError:
        pass

    cache_write_rpta(remsg, senderemail)


def record_questions_unanswered(message, answer, email, date, time):
    """
    Records Unanswered Questions
    """
    answer = open("unanswered.txt", "r")
    unanswered = answer.readlines()
    answer.close()
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
    CONN = xmpp.Client(chatbotini.SERVER, debug=[])
    SHOW = xmpp.Presence()

    # Show: dnd, away, ax
    SHOW.setShow("ax")
    CONRES = CONN.connect(server=("talk.google.com", 5223))

    chatbotini.connection_log("Iniciando sesion\n", "gtalk")
    chatbotini.connection_log(
        "Conectando al servidor (talk.google.com)\n", "gtalk")

    if not CONRES:
        print "No se puede conectar al servidor %s!" % chatbotini.SERVER

        chatbotini.connection_log(
            "No ha sido posible conectar al servidor jabber (%s)\n" % (
                chatbotini.SERVER), "gtalk")
        chatbotini.connection_log("Terminando\n\n\n", "gtalk")

        sys.exit(1)

    if CONRES != "tls":
        print(
            "Advertencia: no se puede estabilizar conexion segura - TLS fallo")

    AUTHRES = CONN.auth(chatbotini.LOGINGTALK.split("@")[0],
                        chatbotini.LOGINPASSWORD,
                        chatbotini.BOTNAME)

    chatbotini.connection_log("Autenticando\n", "gtalk")

    if not AUTHRES:
        print("No se puede autorizar en %s - comprobar " +
              "nombre de usuario / contrasenia.") % chatbotini.SERVER

        chatbotini.connection_log("Login/Password incorrectos\n", "gtalk")
        chatbotini.connection_log("Terminando\n\n\n", "gtalk")

        sys.exit(1)

    if AUTHRES != "sasl":
        print """Warning: SASL authentication can not you% s.
        Old method of authentication used!""" % chatbotini.SERVER

    CONN.RegisterHandler("message", rpta_gtalk)
    CONN.RegisterHandler("presence", present_controller)
    CONN.sendInitPresence()
    CONN.send(SHOW)

    chatbotini.MY_LIST = CONN.getRoster()

    print "Gtalk Login OK"
    chatbotini.connection_log("Sesion iniciada\n", "gtalk")

    # Starts Application
    loop_start(CONN)
