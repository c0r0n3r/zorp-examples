############################################################################
## -*- coding: UTF-8 -*-
##
## Copyright (c) 2000-2001 BalaBit IT Ltd, Budapest, Hungary
## Copyright (c) 2011 Szilárd Pfeiffer <szilard.pfeiffer@balabit.com>

## Authors: Szilárd Pfeiffer <szilard.pfeiffer@balabit.com>
##
## Permission is granted to copy, distribute and/or modify this document
## under the terms of the GNU Free Documentation License, Version 1.3
## or any later version published by the Free Software Foundation;
## with no Invariant Sections, no Front-Cover Texts, and no Back-Cover Texts.
## A copy of the license is included in the section entitled "GNU
## Free Documentation License".
##
############################################################################

from Zorp.Core import *
from Zorp.Http import *
from Zorp.Proxy import *

from zones import *

class CloudEncryptionHttpsKeyBrigeProxy(HttpProxy):
    def config(self):
        HttpProxy.config(self)

        self.transparent_mode=TRUE

        self.ssl.handshake_seq=SSL_HSO_SERVER_CLIENT
	self.ssl.key_generator=X509KeyBridge(
		key_file="/etc/zorp/keybridge/key.pem",
		key_passphrase="passphrase",
		cache_directory="/var/lib/zorp/keybridge-cache",
		trusted_ca_files=(
			"/etc/zorp/keybridge/ZorpGPL_TrustedCA.cert.pem",
			"/etc/zorp/keybridge/ZorpGPL_TrustedCA.key.pem",
			"passphrase"
		),
		untrusted_ca_files=(
			"/etc/zorp/keybridge/ZorpGPL_UnTrustedCA.cert.pem",
			"/etc/zorp/keybridge/ZorpGPL_UnTrustedCA.key.pem",
			"passphrase"
		)
	)

        self.ssl.client_connection_security=SSL_FORCE_SSL
        self.ssl.client_keypair_generate=TRUE
        self.ssl.client_ssl_method=SSL_METHOD_ALL
        self.ssl.client_disable_proto_sslv2=TRUE

        self.ssl.server_connection_security=SSL_FORCE_SSL
        self.ssl.server_verify_depth=5
        self.ssl.server_verify_type=SSL_VERIFY_NONE
        self.ssl.client_verify_type=SSL_VERIFY_NONE
        self.ssl.server_check_subject=FALSE


class CloudEncryptionHttpNonTransparentProxy(HttpProxyNonTransparent):
    def config(self):
        HttpProxyNonTransparent.config(self)
        self.connect_proxy=CloudEncryptionHttpsKeyBrigeProxy
        self.request["*"]=HTTP_REQ_ACCEPT


def cloud_encryption_instance():
	Service("cloud_encryption_service", CloudEncryptionHttpNonTransparentProxy, router=InbandRouter())
	Listener(SockAddrInet("172.16.30.2", 8080), "cloud_encryption_service")
