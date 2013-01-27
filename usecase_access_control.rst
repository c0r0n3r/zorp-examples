--------------
Access Control
--------------

anchor:usecase_access_control[Use case access control]
.. index:: single: protocol;FTP

Use case
========

It is a general use case that we want to grant access for a user to an *FTP* server on the Internet to allow downloading anything, but at the same time we want to prevent them from uploadin anything.

Solution
========

The application level solution of the problem is to accept the read-only commands of the *FTP* protocol, but drop the commands used to write to the server (for example: ``PUT``). As it is a general issue, *Zorp* provides a predefined proxy to perform that, so the system administrator does not have to do anything to implement a read-only *FTP* access, only use that proxy.

.. literalinclude:: sources/ftp_proxy_readonly.py
  :language: python
  :emphasize-lines: 3,7

1. Creates a *rule* that matches the *FTP* traffic, as the destination port in the *rule* is the standard port of the *FTP* servers (``21``). 
2. The service uses the predefined ``FtpProxyRO``, which analyzes the traffic and when we issue a read-only command, it will be sent successfully to the server. When we issue a write command an error message will be sent to the client, but nothing will be sent to the server, as *Zorp* rejects them.

Result
======

Any kind of read-only operation works successfully, but error message is displayed on the client side when it tries to perform a write operation on the server.

.. only:: latex

  .. figure:: images/zorp_access_ro_ftp.png
    :scale: 75

    Read-only FTP proxy

.. only:: html

  .. raw:: html

    <iframe width="853" height="480" src="http://www.youtube.com/embed/EriNAY0hhXU?list=SPE040858BE2F7D34C" frameborder="0" allowfullscreen></iframe>

The configuration file sniplet above grants read-only access to the servers in the zone ``servers`` for the users who come from the zone ``clients``. Without the ``src_zone`` and ``dst_zone`` filters the *rule* would grant access to any server for any user.
