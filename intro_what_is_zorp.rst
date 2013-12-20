What Is Zorp?
=============

Briefly *Zorp* is an open source proxy firewall with deep protocol analysis. It sounds very sophisticated at first, however, the explanation below will make it easy to understand.

Protocol analysis
-----------------
.. index:: Netfilter
.. index:: OSI model
.. index:: single: protocol;FTP

Resulting from their functionality firewalls can analyze the network traffic to a certain extent, since without it, it would not be possible for the administrators to control the traffic. This is not different with *Zorp*. The difference between the firewall applications result from the depth of the analysis. For instance when administrators use *Netfilter* traffic can only be controlled up until layer 4 (traffic) of the *ISO*/*OSI* model. In contrast to that *Zorp* allows analyzation of even the topmost (application) layer, and can make decisions based on data originating from that layer. Decisions can be applied a certain traffic type, for example full access can be set to an *FTP* server for a group of users, or only a subset of commands can be granted to implement a read-only access.

Proxy firewall
--------------
.. index:: single: proxy;forward proxy
.. index:: single: proxy;reverse proxy
.. index:: single: programming language;C
.. index:: single: programming language;Python

Almost anything that comes to your mind can be applied on *Zorp*. First of all the fact that a *proxy* server makes independent connections with the participants of the network communication and relays messages between them separating the clients and the servers from each other. In this regard *Zorp* is better than its competitors as the analysis can take place at the application level, either firewall is used as a *forward* or a *reverse proxy*. To perform that *Zorp* implements application level protocol analyzers. These analyzers, called *proxy* in *Zorp* terminology, are written in *C*, extendable and configurable in *Python*. Nine of twenty five *proxies* of the commercial version of *Zorp* are available in the open source edition.

Modularity
----------
.. index:: single: encryption;TLS
.. index:: single: encryption;SSL

One of the key features of the *Zorp* is customization. It would not be possible without the modular structure of the software. During everyday use it does not require any extra effort to get the benefits of the application level analysis of the network protocols, if we do not have any special requirements. To keep the application level traffic under control we do not have to care about neither the lower layers of the protocol, nor the details of the application level. We only have to concentrate on our goal (for example replacing the value of a specific *HTTP* header), everything else is done by the proxy. If the proxy to our favourite protocol is not given, *Zorp* can handle the connection in lower layers and we have the possibility to perform application level analysis manually.

.. index:: integration
.. index:: virus scanning
.. index:: spam filtering

Transport layer security is an independent subsystem in *Zorp* as far as it possible, so the *SSL*/*TLS* parameters can be set independently from the applied application level protocol (for example *HTTP*, *SMTP*, ...). Consequently each proxy can work within an *SSL* connection, including the case when we perform the protocol analysis. *Zorp*  is a proxy firewall, neither more nor less, but can be adapted to tasks other than protocol analysis, such as virus scanning or spam filtering by integrating it with external applications.

Open source
-----------
.. index:: single: licence;GPL
.. index:: single: licence;LGPL
.. index:: single: Zorp;Zorp GPL
.. index:: single: Zorp;Zorp Professional
.. index:: single: licence;dual-licensin

*Zorp* is not only an open source product, but also a free software as it is licensed under `GPL <http://www.gnu.org/licenses/gpl-2.0.html>`_ and `LGPL <http://www.gnu.org/licenses/lgpl-2.0.html>`_. The reason of the two licenses is the fact that *Zorp* is released in two parts. The application level proxy firewall itself (``zorp``), under the terms of *GPL* and a related library (``libzorpll``), under *LGPL*. Both of them are approved by the `Free Software Foundation <http://www.fsf.org/>`_ as `copyleft <http://www.gnu.org/copyleft/>`_ licences. It must be noted that the *Zorp* is `dual-licensed <http://en.wikipedia.org/wiki/Multi-licensing>`_, where *Zorp*/*Zorp GPL* is the open source version and *Zorp Professional* is the proprietary one with some extra features and proxies.
