====================
Protocol Enforcement
====================

Use case
========

.. index:: single: protocol;HTTP

The most common use case of a proxy firewall -- including *Zorp* -- nowadays is to rule the Internet, means take control over the *HTTP* traffic. This is a simple, but good example to show the advantage of a proxy firewall technology. When the system administrator has to grant access to the World Wide Web, usually only one rule is created, which opens port 80 to the Internet. It solves the original problem, but generates another one. With the help of this rule anybody can access any kind of service of any server on the port 80 independently from the fact, that it is a *web* service or not.

Solution
========

The application level solution of the problem is enforcing the *HTTP* protocol on the traffic on the destination port 80. It is easy with *Zorp*, because there is a predefined proxy (``HttpProxy``) to enforce the *HTTP* protocol. We only have to start a *service* which sets this *proxy* as ``proxy_class`` parameter, when the traffic meets the mentioned requirements.

.. literalinclude:: sources/http_proxy_transparent.py
  :language: python
  :emphasize-lines: 1,4,7

1. Imports anything from the \texttt{Zorp.Http} module, which makes it possible to use *HttpProxy*-related names without any prefix.
2. Creates a simple *service* with the name ``service_http_transparent``, which uses the predefined ``HttpProxy`` of *Zorp*.
3. Creates a *rule* with the necessary conditions, traffic from *zone* ``clients`` to *Zone* ``servers`` targets the port 80 and starts a *service* named ``service_http_transparent``.

Result
======

The result is as simple as possible. The traffic goes through a transparent service without the client or the server being aware of that, while the *HTTP* protocol is enforced by the ``HttpProxy`` of *Zorp*.

.. only:: latex

  .. figure:: images/zorp_audit_http_middle.png
    :scale: 75

    Transparent HTTP proxy

.. only:: html

  .. raw:: html

    <iframe width="853" height="480" src="http://www.youtube.com/embed/ohkpUAgt05k?list=SPE040858BE2F7D34C" frameborder="0" allowfullscreen></iframe>
