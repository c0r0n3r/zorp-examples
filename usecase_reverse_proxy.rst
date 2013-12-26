-------------
Reverse Proxy
-------------

Use case
========

.. index:: DMZ
.. index:: reverse proxy
.. index:: single: protocol;SMTP

A common requirement is the following case: Client connects to a proxy server, that appears to the client as an ordinary server, but it forwards the request to the origin server, which handles it. Thus, we communicate with the origin server through a proxy server. For example we reach a mail server in *DMZ*, we connect to a firewall, but in reality, we communicate with the *SMTP* server in the *DMZ*.

Solution
========

.. index:: single: protocol;FTP
.. index:: single: protocol;HTTP

The communication can be inspected on the protocol level, since the *SMTP* proxy is available in *Zorp*. Based on the abovementioned example, we connect to the firewall, and indirectly communicate with another server through the firewall.

.. literalinclude:: sources/smtp_proxy_transparent_directed.py
  :language: python
  :emphasize-lines: 4,6,8

1. This case is similar than it was at the *HTTP* forward proxy code sniplet, the clients connect to the firewall directly, so the destination IP address is the firewall's address (``172.16.40.1``) and the port is the standard port of *SMTP* (``25``).
2. The service uses the predefined ``SmtpProxy`` proxyclass to enforce the *SMTP* protocol.
3. As the clients target the firewall, the traffic must be routed to the origin server (``172.16.20.254``) directly. As its name shows, this function can be solved by the ``DirectedRouter`` class, where the ``dest_addr`` parameter contains the address and the port value of the origin server.

There is another relevant question in case of a *forward proxy*. As the firewall connects to the origin server, in the log of the *SMTP* server on the origin server it would always show the IP address of the firewall, if we did not extend the router with following parameter:

.. code-block:: python

  router=DirectedRouter(dest_addr=SockAddrInet('172.16.20.254', 25),
                        forge_addr=TRUE
                       )

The ``forge_addr`` and ``forg_port`` options of the *router* can be used to forge the client address and port to the traffic instead of the firewall's ones.

Result
======

.. index:: forward proxy

The client connection is forwarded to the origin server by the firewall to handle it. Replies are forwarded back to the client in a transparent way (at the application level). The client is not aware of the forwarding, so additional settings are not required -- like proxy in the *forward proxy* use case -- on the client side.
