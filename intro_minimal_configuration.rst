---------------------
Minimal Configuration
---------------------

Zorp Kernel Module
==================

*KZorp* is the kernel module of the *Zorp* application level firewall. The module makes possible to make kernel space decisions about the traffic according to the configured *Zorp* policy. It also provides some extensions to *IPTables* so that you can build your own packet filter ruleset that uses *Zorp* concepts and policy objects.

Rule evaluation
---------------

*Zorp* communicates the policy to *KZorp* when starting up, so inital policy decisions can be applied to certain traffic in kernel space. As the result of the decision, packets are either dropped or put back to the chain of *IPTables* where the *KZORP* target has been called.

IPTables relation
-----------------

The *KZorp* kernel and *IPTables* modules allow using certain *Zorp* concepts in packet filter rulesets.

It adds support for the following *IPTables* modules:

* ``zone`` match: you can match on *Zorp* zones (defined in the *Zorp* policy) in your *IPTables* ruleset.

* ``service`` match: matches on either the name or the type of the service that has been selected for the packet based on your *Zorp* policy.

* ``KZORP`` target: handles DAC checks, transparent proxy redirections and generic processing of packets for PFService services (that is, *Zorp* services that process packets on the packet filter level, not in a user-space proxy).

Configuration
=============

The main problem of transparent proxy firewalls is the fact that the traffic does not target the firewall itself, but a host behind the network security device. In a usual case the traffic is forwarded to the originally targeted server, but in case of a firewall the traffic must be delivered locally to the proxy, which will connect to the originally targeted server, or another according to the policy. The divertable packets should be identified somehow in the packet filter rulesets. It can be performed by the means of transparent proxy (`TProxy <http://www.balabit.com/support/community/products/tproxy>`_) kernel module of the kernel.

  The idea is to identify packets with the destination address matching a local socket on your box, set the packet mark to a certain value, and then match on that value using policy routing to have those packets delivered locally.

  -- TProxy Kernel Module Documentation

The following sections will describe the *IPTables* and policy routing rules  that are essential to make *Zorp* operable.

IPTables
--------

At least the following *IPTables* ruleset is required for *Zorp*. Note that this ruleset is fair enough for *Zorp*, but it is inadequate for even the simplest firewall. The ruleset submits a working example of *Zorp*, so it must be extended with some other rules that are ordinary in case of a proxy firewall (for example: grant *SSH* access, handle *ICMP* messages). 

.. literalinclude:: configs/firewall.rules
  :language: none
  :emphasize-lines: 5-6,21,24,32,36

[*KZorp* related *IPTables* rules]

1. The ``socket`` matcher inspects the traffic by performing a socket lookup on the packet (non-transparent sockets are not counted) and checks if an open socket can be found. It practically means that *Zorp* (or any other application) has a socket for the traffic, it is already handled by *Zorp* in the userspace, no kernel-level intervention is required. In this case it is marked with the *TProxy mark* value (``0x80000000``), meaning that it should be handled by *Zorp*.
2. There are some chains of table ``mangle`` where *KZorp* must be hooked for certain purposes (rule evaluation, NAT handling, ...). In these cases we are jumping to a user-defined chain (``DIVERT``) where the corresponding rules can placed to pass the traffic to *KZorp* or even bypass it.
3. This is the place where we can put rules which match to certain traffic should be hidden from *KZorp* and accept it.
4. If no rule has been matched in this chain earlier, this rule jumps to *KZorp* and also marks the packet. This mark can be used in policy routing rules to divert traffic locally to *Zorp* instead of forwarding it to its original address. Note that this mark is the same that we use in case of the first rule of the ``PREROUTING`` chain.
5. If the traffic has already been marked in table ``mangle`` with the corresponding value (``0x80000000``), we should accept it. For example the data channel connection of active mode FTP matches the first rule of ``mangle`` table ``PREROUTING`` chain, so it has been marked, but should be accepted in the ``INPUT`` chain of ``filter`` table as it is an incoming connection.
6. The ``service`` matcher looks up services specified within *KZorp*. Services can be identified by name or by type. Type ``forward`` means a forwarded session (or *PFService*). These kind of sessions should be forwarded in the ``FORWARD`` chain of the ``filter`` table.

.. caution::
  The ruleset above contains those and only those rules which are essential to make *KZorp* and *Zorp* operable. The ruleset must be extended with other rules that make the firewall operable (for example: accepting incoming *SSH* connection or particular typed *ICMP* packets).

.. note::
  The ruleset above is IP version-independent, so it can be used both in case of ``iptables`` and ``ip6tables``.

Advanced Routing
----------------

Packets have been marked to a certain value in *IPTables*. Now match on that value using policy routing to have those packets delivered locally to *Zorp* instead of forwarding it to the original address, and *Zorp* will connect to a server depending on the policy.

.. literalinclude:: configs/rc.local
  :language: none

[*Zorp* related policy routing rules]

1. Rule instructs the system to lookup route for the traffic from table ``tproxy`` if the traffic has been marked with the required value (``0x80000000``) in the ``DIVERT`` chain of the ``mangle`` table in *IPTables*.
2. Table ``tproxy`` has only one route that diverts the traffic locally to *Zorp*, so it is not forwarded as it would have been done by default.

Table name ``tproxy`` can be used only if the following line is added to ``rt_tables`` file.

.. literalinclude:: configs/rt_tables
  :language: none

[*Zorp* related policy routing table names]

.. note::
  The policy routing rules above must be repeated with options ``-6`` instead of ``-4`` to make IPv6 operable.
