Basic Concepts
==============

Zone
----

What Zone is good for?
^^^^^^^^^^^^^^^^^^^^^^

.. index:: IP
.. index:: subnetwork
.. index:: Zone
.. index:: OSI model
.. index:: access control

Usually access to the services controlled by the attributes of lower layers of the *ISO*/*OSI* model, like IP addresses or ports. *Zorp* has an extra feature compared with other firewall suites. There is a possibility to define sets of IP subnetworks, called *Zone*.

Administrative Hierarchy
""""""""""""""""""""""""

*Zones* group IP subnetworks that administratively belong together. What is it good for? In this way an administrative hierarchy can be created that is independent from the network topology, reflecting only the network policy. Imagine the situation when all those who are permitted to access an *FTP* servers for upload not belongs to the same IP subnet. In this case we would have to add at least two IP based rules to our network policy. If we use *Zorp* we only have to add necessary IP subnetworks to the necessary *zone*.

Inheritable Rights
""""""""""""""""""
.. index:: single: protocol;FTP

Other notable feature of zones, that they can be linked to a tree hierarchy. Access control rights are inherited between the levels of the *zone* tree. A top-level access is in effect in the lower levels as long as it is not blocked. For instance a top-level access can be the right to download from *FTP* servers. When a group of users should have special rights. These special rights can be granted in the lower levels of the *zone* tree.

How Zone can be configured?
^^^^^^^^^^^^^^^^^^^^^^^^^^^

The simplest way to define a *Zone* to write the followings to the configuration file ``policy.py``. It defines an empty *Zone*, which has not contain any subnetwork, but can be referred from the firewall rules by its name ``zone``. Obviously it is not so useful, but it is simple as we promised.

.. code-block:: python

  Zone('zone')

As it has already mentioned a *Zone* groups the administratively belonging IP subnetworks together, so we have to define these subnetworks somehow to give meaning to the *Zone*. It can be done by creating the ``Zone`` class with additional ``addrs`` parameter, which value must be an iterable object, which contains IP subnetworks in CIDR notation.

.. code-block:: python

  Zone(name='intra.devel', addrs=['10.1.0.0/16', 'fec0:1::/24'])
  Zone(name='intra.it',    addrs=['10.2.0.0/16', 'fec0:2::/24'])

How Zone works?
^^^^^^^^^^^^^^^

Inheritance
"""""""""""

As it has also mentioned a *Zone* can refer another *Zone* as its parent, which makes possible to create a tree from the *Zone* s. This tree represents the administrative hierarchy of our network. When a *Rule* refers to a parent *Zone* in the hierarchy it implicitly refers to the whole subtree. It practically means that we accept a special kind of traffic in a parent *Zone* it will be accepted all of its child *Zone* s also.

.. code-block:: python

  Zone(name='intra',
       addrs=['10.0.0.0/8', 'fec0::/16'])
  
  Zone(name='intra.devel', admin_parent='intra',
       addrs=['10.1.0.0/16', 'fec0:1::/24'])
  Zone(name='intra.it',    admin_parent='intra',
       addrs=['10.2.0.0/16', 'fec0:2::/24'])

If the *Zone* hierarchy above is defined and we create a *Rule* which accepts for example the *HTTP* traffic from the *Zone* ``intra`` it also accepts the *HTTP* traffic from ``intra.devel`` and ``intra.it`` and any other *Zone* will be crated in the future which defined as the child of ``intra`` independently from the fact that subnetworks of parent and child *Zone* s contains each other or not.

Rule
----

.. index:: access control

What Rule is good for?
^^^^^^^^^^^^^^^^^^^^^^

There is no firewall without access control and *Zorp* is no exception to this rule. When an access control policy is being created, we first have to find answers to the "who", "what" and "how" - questions. Resources should be accessible only for a specific group of users under the defined conditions.

How Zone works?
^^^^^^^^^^^^^^^

The *Rule* answers to the "who", "what" and indirectly the "how" questions.

Who and What?
"""""""""""""

The "who" and the "what" questions can be answered by a set of traffic properties. A specific *Rule* matches to a certain traffic when the parameters what were given to the *Rule* match to the traffic.

.. code-block:: python

  Rule(service='service_dns',
       dst_port=53)

In the example above the *Rule* matches to any kind of traffic which target the port destination 53. In other words it grants access to any name server on the internet. It works only when protocol is *TCP* or *UDP*, because port is not defined in case of other protocols (for example *IGRP*), but we can add another conditions to the *Rule* to make the rule definite.

.. _complex rule example:
.. code-block:: python

  Rule(service='service_dns',
       proto=(socket.IPPROTO_TCP, socket.IPPROTO_UDP),
       dst_subnet='8.8.8.8/32',
       dst_port=53)

As it can be seen multiple conditions can be defined, so the "who" and the "what" can be answered at the same time. The questions are what kind of conditions can be set, what is the relation between the different type of conditions, what is the relation between the items of a certain condition.

Conditions
""""""""""

First of all list the possible conditions parameters of a *Rule*. As you can see there are 8 different type of conditions, which can be set independently from each other. If more the one condition is given the rule matches only if the logical conjunction of the conditions matches. If there is more than one value in a specific condition there is logical disjunction between them.

.. _condition list:

#. VPN id (``reqid``)
#. source interface (``iface`` or ``src_iface``)
#. protocol (``proto``)
#. protocol type (``proto_type``)
#. protocol subtype (``proto_subtype`` or ``icmp_type``)
#. source port (``src_port`` or ``icmp_code``)
#. destination port (``dst_port``)
#. source subnetwork (``src_subnet`` and ``src_subnet6``)
#. source *zone* (``src_zone``)
#. destination subnetwork (``dst_subnet`` and ``dst_subnet6``)
#. destination interface (``dst_iface``)
#. destination *zone* (``dst_zone``)

In the `complex rule example`_ above the *Rule* matches when the protocol of the traffic is ``TCP`` or ``UDP`` and the destination address is ``8.8.8.8`` and the destination port is ``53``. In general we can say if we want a more restrictive *Rule* we have to add a new condition, if want a more permissive rule we have to add a new value to an existing condition.

Best match
""""""""""
.. index:: best match
.. index:: Netfilter

In contrast to the *Netfilter* where the first matching rule takes effect, in case of *Zorp* the best matching rule takes effect. It entails that the order of the rules is irrelevant. When a new connection is occurred the evaluation will check each rule against the parameters of the traffic to find the best one.

The word best in the expression *best match* means that the more accurate rule will take affect. The accuracy of a *Rule* depends on two thing, the evaluation order of the conditions and the accuracy of the specific condition in the *Rule*.

Evaluation order
  There is a precedence between the different condition types, which determines the order of the evaluation. It means if a rule has a condition with higher precedence it considers better that the other one. The `condition list`_ enumerates over the conditions in top to bottom in descending precedence. It practically means that a rule with a destination subnetwork condition is always better than a rule with destination *zone* condition and both of them are worse than a rule with a source *zone* condition and so on ...
Condition scope
  If two rule are considered to be identical -- in other words they have conditions with the same precedence -- the value of the conditions determines which one considered to be better. In general a narrower is always better than a wide scope, which means an IP subnetwork with greater prefix value, a port number instead of a port range, a child *zone* instead of a parent is more specific, so the rule with it is considered better.

How Rule can be configured?
^^^^^^^^^^^^^^^^^^^^^^^^^^^

Lets imagine the situation when we want to grant access to any kind of *FTP* server on the internet in read-only mode for everyone in our local network (``10.0.0.0/8``), but we have to grant read-write access to a specific server (``1.2.3.4``) and for a certain department (``10.10.0.0/16``) of our organization. How can we use the *best match* to fulfill the requirements?

First of all solve the general requirement, which is the read-only access to any *FTP* server for everyone from our subnet. It can be done by a *rule* which contains two explicit and an implicit condition and an action. The explicit conditions are about the destination port, namely ``21``, the standard *FTP* port, and the source subnetwork, namely ``10.0.0.0/8`` which is our private network in the example. The implicit condition is about the destination subnetwork that does not appear in the rule, which means it matches independently from the destination of the traffic. The action can be set by the ``service`` parameter of the rule which is ``service_ftp_read_only`` in this case.

.. code-block:: python

  Rule(service='service_ftp_read_only',
       dst_port=21)
  
  Rule(service='service_ftp_read_write',
       dst_subnet='1.2.3.4/32',
       dst_port=21)
  
  Rule(service='service_ftp_read_write',
       src_subnet='10.10.0.0/16',
       dst_port=21)

The second requirement was to grant read-write access to a specific server (``1.2.3.4``). It can be done by a *rule* matches "better" to the traffic than the previous one. As the second rule has a condition to the destination subnetwork (``dst_subnet``), while the first one has not, it considered to more specific, so it is a "better" match.

The third requirement was to grant read-write access for a department (``10.10.0.0/16``) of our organization to any *FTP* server. It is also possible by adding a new *rule* with a condition to the source subnetwork (``src_subnet``) with the necessary value (``10.10.0.0/16``).

The question arises, what is the *best match* to a traffic which comes from the subnetwork ``10.10.0.0/16`` and its destination is the address ``1.2.3.4``, as in this case each *rule* matches. As we have already mentioned the second and the third one more specific than the first, so the first one cannot be the bast match. Inasmuch source subnetwork condition has higher precedence than the destination subnetwork the second *rule* will be the *best match*.

Service
-------

What service is good for?
^^^^^^^^^^^^^^^^^^^^^^^^^

The *service* answers the earlier mentioned "how" question, as it determines what exactly happen with the traffic, whether it is analyzed in the application layer of the *ISO*/*OSI* model or not, rejected or accepted. After the best matching *rule* has found, an instance of a *service* set in the *rule* starts to handle the new connection.

How service works?
^^^^^^^^^^^^^^^^^^

There are three different service types in *Zorp* with completely different functionality and configuration.

``PFService``
  Transfers packet-filter level services, so if you want to transfer connections on the packet-filter level only and you don't want analyze application level traffic making decisions based on it use ``PFService``. It gives you better performance as the decision about the traffic can be made in kernel space by *KZorp* without the assistance of the user space firewall (*Zorp*) itself.

``Service``
  Transfers application-level (*proxy*) services, so if you want to transfer connections on the application-level to make possible the audit, analysis, restriction or modification use ``Service``. It gives you worse performance than ``PFService`` as the decision about the traffic cannot be made only in kernel space (*KZorp*) it needs the assistance of the *Zorp*, runs in the user space, which makes deeper and also more resource hungry operations.

``DenyService``
  Rejects the connections in a predefined way. In general it can be used to handle the exceptions in your policy. If you have a general rule which grant access to any *FTP* servers from any subnetwork, but you want to make an exception (for example there is a prohibited server) you can create a more specific *rule* (with the server address in ``dst_subnet`` condition) which rejects the traffic as it is set in the ``DenyService``.

How service can be configured?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Minimal configuration of a *service* depends on its type, but at least must contain a name. The ``name`` parameter is used to refer the *service* from other object (for example from a *rule*).

``PFService``
  With the defaults of the additional parameters of ``PFService`` transfers the traffic through the firewall in packet-filter level without passing it to the user space (just like in *Netfilter*).
``Service``
  In case of ``Service`` ``proxy_class`` parameter also mandatory. This is the most important parameter in the point of view of a proxy firewall, while its value determines what will happen with the traffic in the application layer.
``DenyService``
  With the defaults of the additional parameters of ``DenyService`` drops the traffic silently (just like ``DROP`` target in *Netfilter*).

.. code-block:: python

  PFService(name='PFService')
  Service(name='Service', proxy_class=HttpProxy)
  DenyService(name='DenyService')

Proxy
-----

As it has already been mentioned earlier the network traffic analysis can take place at the application level. To perform that, *Zorp* implements application level protocol analyzers. These analyzers are called proxies in the terminology of *Zorp*. Proxies are written in *C*, and they are extendable and configurable in *Python*.

What proxy is good for?
^^^^^^^^^^^^^^^^^^^^^^^

Any kind of application level protocol analysis, restriction, modification can be done by *proxy*.

How proxy works?
^^^^^^^^^^^^^^^^

Predefined proxies
""""""""""""""""""

*Zorp* contains several proxies which can be used without any improvement or modification to work on the application level traffic.

``HTTP``, ``FTP``, ``SMTP``
  Proxies to analyze widely used protocols

``Finger``, ``Telnet``, ``Whois``
  Proxies to analyze rarely used protocols.

.. index:: single: proxy;Plug

``Plug``
  As its name shows it does nothing else, but to plug the client and server connection. It has all the benefits that other proxies have, except the protocol analysis.

.. index:: single: proxy;AnyPy

``AnyPy``
  It is a simple proxy like the *Plug* proxy with a *Python* interface. It makes it possible to do anything with the application level network traffic which can be done by the help of the *Python* language, while the lower layers of the connection is handled by *Zorp*. For instance if the proxy to our favorite protocol is not implemented yet in *Zorp* we have the possibility to perform application level analysis manually.

Proxy Inheritance
"""""""""""""""""

As it is mentioned each proxy is configurabe and extendable in *Python*. It means each proxy represented as a class in *Python* and the system administrator can inherit his own *Python* class from that to override the behavior of the parent class. A derived class inherits everything from the base class, which is necessary for the protocol analysis, so the system administrator has to care about his specific problem. For instance to change a value of a header in the *HTTP* protocol needs only an extra line of code over the lines related to the *Python* inheritance mechanism.

General SSL Handling
""""""""""""""""""""

General *SSL* handling follows from the fact, that transport layer security is an independent subsystem in *Zorp*. It means, that *SSL*/*TLS* parameters can be set independently from the fact, that we perform protocol analysis or not. Consequently not only *HTTP*, *FTP*, *SMTP* and *POP3* proxies are *SSL* capable, but also the *Plug* and the *AnyPy* proxies. Server and client side *SSL* parameters can also be set independently. So it is possible to encrypt on the client side, but not on the server side and vice versa. Of course both of the sides can be encrypted.

Program stacking
""""""""""""""""

.. index:: program stacking

*Zorp* is a proxy firewall, neither more nor less, but can be used to do tasks other than protocol analysis, such as virus scanning or spam filtering by integrating it with external applications. For instance in case of the *HTTP* protocol *Zorp* can forward responses to a virus scanner software. After that depending on the result of the scan *Zorp* can accept or reject the original request.

How proxy can be configured?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

*Zorp* *proxy* classes can be implemented or customized in *Python* language. As the following example show the only thing we have to do is deriving a new class from the necessary base class (``HttpProxy``) and customizing its behaviour.

.. code-block:: python

  from Zorp.Http import *
  
  class HttpProxyHeaderReplace(HttpProxy):
      def config(self):
          HttpProxy.config(self)
          self.request_header["User-Agent"] = (HTTP_HDR_CHANGE_VALUE,
                                               "Forged Browser 1.0")

The example above only a demonstration of a customization, it is uncommented now, we will back to later.
