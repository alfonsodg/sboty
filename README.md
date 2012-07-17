Sboty Project
=============

Messaging Multiprotocol Application (bot) with automated responses
using the AIML standard libraries.


Requirements
------------

* xmpp
* msn_lib (included and modified to fix deprecated methods)

You can install xmpp, using:

    pip install xmpppy


Usage
-----

* Rename **chatbot_settings.xml.EDITME** to **chatbot_settings.xml**.
* Edit chatbot_settings.xml filling the data required by each tag.
* Run **chatbot_gtalk_setup.py** or **chatbot_msn_setup.py** according
  to what service you will be using.
* To debug the AI, you can use/modify the scripts: all_questions.py
  (to show all questions being asked) or show_unanswered.py (to show
  only the unanswered ones).
* If you need to change the logic or the content of the replies, change
  the corresponding files in the *intelligence* drawer.

Demo
----

Try adding this contact to gmail / google apps / live / hotmail :

    demo@ictec.biz


AIML Reference
--------------

http://www.alicebot.org/aiml.html


Notes
-----

You can copy or modify the chatbot_gtalk_setup.py to accommodate to any service.
Nowadays most messaging services use the xmpp protocol, so it should
be simple to accommodate other providers.


Author
------

ICTEC SAC

Alfonso de la Guarda Reyes <alfonsodg@gmail.com>


Thanks
------

César Bustios

Giancarlo Reyes



License
-------

Under GPL / v3

Proprietary on demand when OSI / FSF licenses are not compatible with
your desires
