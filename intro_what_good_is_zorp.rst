What Good Is Zorp?
==================

A marketing specialist would claim that it is "good for everything". Not being one of them, we would rather say that *Zorp* is not the philosopher's stone, however, it can solve almost any issue that can be expected from a deep protocol analyzer proxy firewall. The most important cases are the following:

Access control
--------------
.. index:: IP
.. index:: subnetwork
.. index:: Zone
.. index:: OSI model

Access control is a basic functionality of proxy firewalls, but *Zorp* has an extra feature compared with other firewall suites. Access to the services can be controlled by the attributes of lower layers of the *ISO*/*OSI* model, like IP addresses or ports, but in case of *Zorp* there is a possibility to define sets of IP subnetworks, called *zones*. *Zones* are IP subnetwork groups that administratively belong together (for example all those who are permitted to access *FTP* servers for upload) and can be linked to a tree hierarchy. Access control rights are inherited between the levels of the *Zone* tree. A top-level access (for example a right to download from *FTP* servers) is in effect in the lower levels as long as it is not blocked. In this way an administrative hierarchy can be created that is independent from the network topology and the location of the devices, while reflecting only the network policy.

When an access control policy is being created, we first have to find answers to the "who", "what" and "how" - questions. Resources should be accessible only for a specific group of users under the defined conditions. It may mean that each request and response must be recorded to the system log when a given server is accessed. Some features of the protocol (for example: ``STARTTLS`` in case of *SMTP*) causing incompatibility between the client and the server may have to be filtered out. Some items of the protocol (for example ``PUT`` in case of *FTP*) may be rejected. Some protocol items (for example ``user-agent`` in case of *HTTP*) may be changed to avoid information leak. Secure connection may be decrypted on one side and encrypted again on the other side. The following sections will describe this in detail.

Information Leak Prevention
---------------------------
.. index:: single: protocol;HTTP
.. index:: single: protocol;SMTP
.. index:: single: protocol;HTTP;user-agent

Several protocols leak information about the running softwares, the networking options of the clients, which is usually not filtered or not blocked by the firewalls, because they are absolutely compliant with the related standards. An example of this is the ``user-agent`` header in the *HTTP* protocol, which contains the name and the version of the web browser connected to the server. In this case an information about the software being run on the client machine is received by the visited web server without the knowledge or the permission of the user.

The proxy settings of the web browser, the *IP* address of the machine, the *URL* of the previously visited web page (referrer of the currently visited one) are leaked in the same way. Similar methods exist in case of several protocols, besides *HTTP*. System administrators have to be aware of these type of information leaks and have the means to forbid them. *Zorp* is an easy-to-use and flexible tool for that.

Interoperability
----------------
.. index:: single: protocol;HTTP;user-agent

Continuing the example above, not only forbidding of complete protocol items is possible, but also the modification of their values. It can solve the problem of the interoperability for example when a web server constraints the type or the version of the connecting browser despite of the fact that it has no good or valuable reason. Such a situation can be solved easily by changing the value of the ``user-agent`` header in the request sent by the browser to a value which is acceptable to the server.

.. index:: single: encryption;SSL
.. index:: single: encryption;TLS

The lack of encryption support may cause interoperability mainly in case of old-fashioned software especially when the traffic should pass through an untrusted network. There are several solutions to this problem, but if we want to proxy the traffic and use different methods of encryption (*STARTTLS*, *SSL*) to the client and the server, *Zorp* is still one of the best solutions. It is possible to establish an encrypted connection through the untrusted network and a plain connection through the trusted one. It is also possible the use different versions of encryption (*TLS* 1.0, *TLS* 2.0) to the client and server.

.. index:: single: protocol;SMTP

To do that, capability of establishing encrypted connections separately to the client and the server is necessary, but not sufficient. The reason is the way to upgrade a plain text connection to an encrypted (*TLS* or *SSL*) one instead of using a separate port for encrypted communication (*STARTTLS*), where understanding the protocol is a must. If we want to hide this functionality from the client and the server even if both of them support it, to solve an incompatibility problem, *Zorp* can help us. We can conceal features of the clients or the servers (for example *STARTTLS* in *SMTP*, or compression in *HTTP*) from each other.

To continue the encrypting example, *Zorp* can hide the *STARTTLS* feature of the *SMTP* server from the client, which prevents to initiate encrypted communication in this way. Certain combinations of client and server side *SSL* settings (for example when *SSL* is forced in server side) *Zorp* does it automatically.

Content Filtering
-----------------
.. index:: content filtering
.. index:: single: content filtering;virus scanning
.. index:: single: content filtering;spam filtering
.. index:: single: content filtering;URL filtering

Content filtering is a key feature of firewalls. *Zorp* is not an exception to this rule, even if without extensions there are only limited opportunities to do that work. However, each of spam filtering, virus scanning, *URL* filtering is possible by means of external software components. Let the cobbler stick to his last. *Zorp* does nothing else, but analyzes the protocol to find the particularly interesting parts of the traffic (*URL*, downloaded data, e-mail attachment, ...) and passes it to the necessary application. As the result of the content filtering and possibly other conditions, *Zorp* may accept, reject or only log the request, or even quarantine the response. We have nothing to do, but establish connection between the *Zorp* and the chosen content filtering software (for example: ClamAV, SpamAssassin, ...) with a simple adapter application, which makes the location of the data known to the content filtering tool and forwards the result to *Zorp*.

Audit
-----
.. index:: audit

Establishing an access control system is only the first step on the way to achieve a well-controlled and secure network. Operating and administrating this network is more difficult. Above all, we need to know what is happening in our network, because only this information can create the possibility to improve the access control system. On the one hand we have to answer what kind of events have violated the current network policy. On the other hand we are in need of the information whether a permitted action has happened or not and if so, than how. *Zorp* is able to log the necessary information in both cases.

.. index:: logging

The benefit of *Zorp* is the fact that we can retrieve information from the proxies in application level so events of the network can be handled in the application level also. Even requests and responses of a protocol can be recorded to the system log, which can be very useful in case of an audit. After the necessary configuration of the proxy from the log messages it can be proved whether an event has happened or not in a specific time interval and also statistics can be created based on them.

Flexibility
-----------
.. index:: single: programming language;C
.. index:: single: programming language;Python
.. index:: single: proxy;AnyPy

*Zorp* is able to solve the general uses mentioned above as it is, but the strength of the *Zorp* lies in the fact that it is easily extendable and customizable to solve specific problems. We do not need to reimplement any kind of functionality, especially the protocol analyzers, we can reuse and extend them to meet our requirements. Nevertheless the proxies are mainly written in *C*, they can also be scripted in *Python* with all of the benefits of the language. Existing ones (*HTTP*, *FTP*, ...) can be specialized, or a new one can be implemented if we want to analyze the protocol at application level only. It is possible with a special kind of proxy (*AnyPy*) which does anything, but the application level analysis, so we can focus on that job.
