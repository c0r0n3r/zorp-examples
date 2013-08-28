Configuration debugging
=======================

After a configuration change there are so many cases when the system does not function as expected. Typical problems can be explored with some check you can read in the following sections.

Obsolete configuration
----------------------

Problem
```````

It is common problem that an *instance* runs with an obsolete configuration, because we had modified the policy, but did not notify the *Zorp* about it.

Check
`````

The actual status of a *Zorp* instance can be displayed by ``zorpctl`` with ``status`` command. With ``instance_name`` argument only the status of the given *instance* will be printed, otherwise ``zorpctl`` prints state of each and every instance.

.. code:: bash

  zorpctl status [instance_name]

The output of the ``zorpctl status`` command is the following. In case of the first line instance is running with an obsolete configuration, which means the *policy* file is newer that the *instance* is run. In case of the second line instance is not running at all, which typically means there is a configuration problem why the instance could not be started.

::

  Process http#0: running, policy NOT reloaded, 5 threads active, pid 2180
  Process http#0: not running

Solution
````````

If the only problem is that we forget reloading the *instance* run ``zorpctl reload`` command with the name of the instance as argument. If the *instance* is not running it can be started with ``zorpctl start`` command.

.. code:: bash

  zorpctl reload instance_name
  zorpctl start instance_name

.. IMPORTANT:: Any changes in ``instances.conf`` needs *restart*.

.. CAUTION:: Instance *restart* aborts active connection.

.. WARNING:: Active connections are not affected by *reload*. The traffic which was accepted by the *policy* before the *reload*, but rejected by the actual *policy* is not aborted by the *reload*.

Result
``````

After *reload* or *start* we should see something similar than the following status report. The process identifier (pid) will be the same if an instance *reload* had been accomplished , but should be different after a *restart*

::

  Process http#0: running, 9 threads active, pid 19302

Configuration reload
--------------------

Problem
```````

In exceptional cases it might happen that the *policy* know by the user space (*Zorp*) and kernel space (*KZorp*) differs from each other.

Check
`````

Configuration actually stored in *KZorp* can be dumped by ``kzorp`` tool.

.. code:: bash

  kzorp --dispatchers
  kzorp --zones
  kzorp --services

The certain configuration items (dispatchers, zones, services) can be dumped separately or at the same time.

.. code:: bash

  kzorp -dzs

The dumped configuration should be the same that is stored in the configuration file assuming that the *instances* run the actual configuration.

Solution
````````

The solution is the same that it was in case of `obsolete configuration`_.

Result
``````

After the *reload* or *restart* the the *policy* know by the user space (*Zorp*) and kernel space (*KZorp*) must be the same.

Missing zone
------------

Problem
```````

Typical situation is when a *zone* in a newly created *rule* in the *policy* does not match the actual traffic.

Check
`````

If we know the parameters of the traffic cause the problem, it can be evaluated by *KZorp* to decide which *zone* matches in the policy by ``kzorp`` command line tool.

.. code:: bash

  kzorp -e tcp 10.10.0.1 1.2.3.4 eth1 --src-port 1234 --dst-port 21

The most commonly encountered problem is that there is no *zone* which matches to the traffic or an unexpected *zone* matches. In this case the result of the evaluation will be similar to the followings.

::

  evaluating tcp 10.10.0.1:1234 -> 1.2.3.4:21 on eth1
  Client zone: not found <1>
  Server zone: unexpected.zone <2>
  Service: ftp/ftp_readonly
  Dispatcher: ftp/dsp/dispatch:0

1. The *zone* contains the source address (2nd argument of ``evaluate`` option)
2. The *zone* contains the destination address (3rd argument of ``evaluate`` option)

.. NOTE:: If there is no *zone* in our *policy* the *Client zone* and *Server zone* will always be *not found*.

Solution
````````

If *zone* is not found add a new *zone* or extend an existing one with a pretty small subnetwork (for example ``10.10.0.0/16``) or add a *zone* (for example with name *internet*) with the largest possible subnetworks (``0.0.0.0/0`` and/or ``::0/0``) which means a fallback if there is no other matching *zone*.

If other *zone* found than it is expected there are two possibilities.

1. The subnetwork in the expected *zone* is too small and the IP address of the traffic is outside of the subnetwork and also the *zone*. In this case

  * increase the size of the subnetwork by decreasing its prefix to make it large enough to contain the IP address (for example ``10.10.0.0/16`` instead of ``10.10.10.0/24``) or
  * add another subnetwork to the *zone* which contains the IP address (for example ``10.10.20.0/24`` or ``10.10.20.30/32``) or
  * add another *zone* to the *rule* which already contains the IP address

2. The expected *zone* is too large and there is another *zone* with a more specific subnetwork. In this case

  * set the actually matching *zone* the child of the expected *zone*, but keep in mind any other *rule* with the parent*zone* will apply to this earlier independent *zone* from now on
  * add a more specific subnetwork to the expected *zone* that there is in the actually matching *zone*

Result
``````
After the fix of the subnetworks and hierarchy of *zone*s the result of the evaluation should contain the the expected *zone* s.

::

  evaluating tcp 10.10.0.1:1234 -> 1.2.3.4:21 on eth1
  Client zone: intranet.devel
  Server zone: internet
  Service: ftp/ftp_readwrite
  Dispatcher: ftp/dsp/dispatch:0

Missing dispatcher
------------------

Problem
```````

Despite of the fact that the *zone*s are the expected *zone*s or we do not have any *zone* in our *policy* it may happen that no *dispatcher* found cause of other conditions in the *rule* that are not match.

Check
`````

The check is the same that it was `last time <missing zone_>`_ in case if missing *zone*.

.. code:: bash

  kzorp -e tcp 10.10.0.1 1.2.3.4 eth1 --src-port 1234 --dst-port 21

In this case the *zone*s are what we expected, but neither *dispatcher* nor the *service* found.

::

  evaluating tcp 10.10.0.1:1234 -> 1.2.3.4:21 on eth1
  Client zone: expected.zone
  Server zone: expected.zone
  Service: not found <1>
  Dispatcher: not found <2>

1. The *service* started by the *rule* matches the given traffic.
2. The *dispatcher* that matches to the traffic.

Solution
````````

Consider other conditions of the *rule*. They are the following in the order of probability that the condition in question cause the problem.

1. Check source and destination subnetwork condition in the *rule* (``src_subnet``, ``dst_subnet``) in the same way that you did in case of missing *zone*.
2. Check source interface condition in the *rule* (``src_iface``) also check (for example with *tcpdump*) the traffic is actually on this interface.
3. Check source and destination port in the *rule* (``src_port``, ``dst_port``) especially port ranges.
4. Check protocol number.

Result
``````

After the fix *service* and *dispatcher* in the evaluation should contain the the expected ones.

::

  evaluating tcp 10.10.0.1:1234 -> 1.2.3.4:21 on eth1
  Client zone: not found
  Server zone: not found
  Service: ftp/ftp_readwrite
  Dispatcher: ftp/dsp/dispatch:0


Disappearing traffic
--------------------

Problem
```````

Everything seems fine, *policy* is up-to-date in *Zorp*, evaluation result is correct, but *service* does not start.

Check
`````

Add Netfilter rules to the ``raw`` table which makes possible to trace the route of desired traffic in IPTables. If  traffic in question is *TCP* where the destination is ``1.2.3.4:21`` use the following commands.

.. code:: bash

  iptables -A PREROUTING -t raw -p tcp -d --dport 21 -j TRACE
  iptables -A OUTPUT -t raw -p tcp -d --dport 21 -j TRACE

.. NOTE:: Do not forget to load ``ipt_LOG`` module with the command ``modprobe ipt_LOG``.

.. TIP:: You can prefix the generated log by appending ``--log-prefix "some prefix"`` which makes easy to find them in your log.

Solution
````````

Follow the route of the traffic and find the last Netfilter rule where it appears. Depending on the type of the rule you can modify your Netfilter policy (for example found rule jumps to *DROP* target) or continue debug in *KZorp* as you can read :ref:`kernel-debugging` section.

Result
``````

Hopefully after finding the problematic Netfilter rule the *service* work very well.
