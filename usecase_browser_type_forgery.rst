--------------------
Browser Type Forgery
--------------------

Use case
========
.. index:: single: protocol;HTTP;user-agent

However *Zorp* is not a *Data Loss Prevention* system, it can help the system administrator to avoid leaking some kind of sensitive information, which are usually not filtered or blocked by the firewalls, because they are absolutely compliant with the related protocol standards.

Best known example is the ``User-Agent`` field in the *HTTP* header, which contains the name and the version of the browser connected to the server. In this case information about the software being run on the client machine is received by the visited web server without the knowledge or the permission of the user.

Some interoperability related issues can also be solved by *Zorp* follows the fact that a *proxy* firewall makes independent connections with the participants of the network communication and relays messages between them separating the clients and the servers from each other. Client thinks that it talks to the server and server thinks that it talks to the client. In real each of them talks with the proxy, which send their messages to the other part, while reinterprets it, so changes can be made on each side without the knowledge of the participants.

Solution
========

Modification of certain protocol items and their values can be done. It can solve the problem of the interoperability for example when a web server constraints the type or the version of the connecting browser despite of the fact that it has no good or valuable reason. Such a situation can be solved easily by changing the value of the ``User-Agent`` header in the request sent by the browser to a value which is acceptable to the server.

.. literalinclude:: sources/http_proxy_header_replace.py
  :language: python

Result
======

.. only:: latex

  .. figure:: images/zorp_ilp_http_header_replace_end.png
    :scale: 75

    HTTP header replace

.. only:: html

  .. raw:: html

    <iframe width="853" height="480" src="http://www.youtube.com/embed/ohkpUAgt05k?list=SPE040858BE2F7D34C" frameborder="0" allowfullscreen></iframe>
