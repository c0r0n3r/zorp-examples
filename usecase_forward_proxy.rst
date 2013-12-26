-------------
Forward Proxy
-------------

Use case
========

.. index:: Squid
.. index:: single: proxy;forward proxy

We intend to use the firewall as a proxy server, like a *Squid* web cache.

Solution
========

The solution is very simple, since there is a proxy class that we can use to control the traffic on the proxy level. In this case, the clients connect to *Zorp* that acts as a proxy server, and allows traffic flow according to the rules, but communicates with the clients "in the proxy language".

.. literalinclude:: sources/http_proxy_nontransparent.py
  :language: python
  :emphasize-lines: 4,5,6,8

1. Creates a *rule* which matches only, when the traffic comes from the ``clients`` *zone* and targets the IP address ``172.16.10.254`` and the port ``3128``, which address is the address of the client side interface of the firewall.
2. Creates a service that works like a proxy server.
3. It uses the predefined ``HttpProxyNonTransparent``, because this *proxy* class -- against the ``HttpProxy`` in the code sniplet tarnsparent proxy use case -- handles the traffic as a proxy server.
4. In this case the address of the *HTTP* server, that the client wants to connect to, comes from the application layer traffic and not from the network layer, so the default ``DirectedRouter``. It routes the traffic where it was originally considered to be routed, but in this case (non-transparent service) the client targets the proxy server (here, the firewall) itself. Setting ``InbandRouter`` as ``router`` can handle the situation for both the *HTTP* and *FTP* protocol.

Result
======

Now the IP address ``172.16.10.254`` and port ``3128`` can be set as *HTTP* proxy in the internet browsers.
