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
from Zorp.AnyPy import *
from Zorp.Proxy import *

import Zorp
import Zorp.Stream

from zones import *

import DataHandler
import Cypher

config.options.kzorp_enabled=FALSE

class CloudEncryptionStackedProxy(AnyPyProxy):
    def config(self):
        self.client_max_line_length = 16384

        self.data_handler = DataHandler.GoogleCalendarProxyDataHandler()
        self.cypher = Cypher.NoCypher('magic')

    def readData(self):
        data = ""
        while True:
            try:
                data += self.client_stream.read(1024)
            except BaseException:
                break
            #except Zorp.Stream.StreamException, (code, lastline):
            #    if code == Zorp.Stream.G_IO_STATUS_EOF:
            #        break
            #    else:
            #        raise

        return data

    def proxyThread(self):
        try:
            plain_raw_data = self.readData()
            self.data_handler.parse(plain_raw_data)
            self.data_handler.cypher(self.cypher, self.is_request)
            cyphered_raw_data = self.data_handler.compose()
            self.server_stream.write(cyphered_raw_data)
            #proxyLog(self, "cypher.info", 3, "Data successfully cyphered")
        except KeyError as e:
            proxyLog(self, "cypher.error", 3, "Data cypher failed; error='%s'", str(e))


class CloudEncryptionStackedProxyRequest(CloudEncryptionStackedProxy):
    def config(self):
        super(self.__class__, self).config()

        self.is_request = True


class CloudEncryptionStackedProxyResponse(CloudEncryptionStackedProxy):
    def config(self):
        super(self.__class__, self).config()

        self.is_request = True


class CloudEncryptionSSLProxy(HttpProxy):
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


class CloudEncryptionHttpsProxy(CloudEncryptionSSLProxy):
    def config(self):
        CloudEncryptionSSLProxy.config(self)

        self.request_header["Accept-Encoding"]=(HTTP_HDR_CHANGE_VALUE, "identity")
        self.rewrite_host_header = FALSE

        self.request["GET"] = (HTTP_REQ_POLICY, self.filterOutIrrelevanTraffic)
        self.request["POST"] = (HTTP_REQ_POLICY, self.filterOutIrrelevanTraffic)

    def filterOutIrrelevanTraffic(self, method, url, version):
        raise NotImplementedError


class CloudEncryptionHttpsGoogleCalendarProxy(CloudEncryptionHttpsProxy):
    def filterOutIrrelevanTraffic(self, method, url, version):
        proxyLog(self, "", 3, "Data cypher failed; uri='%s'", self.request_url_file)
        if self.request_url_file.startswith("/calendar/feeds"):
            self.request_stack["*"] = (HTTP_STK_DATA, (Z_STACK_PROXY, CloudEncryptionStackedProxyRequest))
            self.response_stack["*"] = (HTTP_STK_DATA, (Z_STACK_PROXY, CloudEncryptionStackedProxyResponse))
        return HTTP_REQ_ACCEPT


class CloudEncryptionHttpNonTransparentProxy(HttpProxyNonTransparent):
    def config(self):
        HttpProxyNonTransparent.config(self)
        self.connect_proxy=CloudEncryptionHttpsGoogleCalendarProxy
        self.request["*"]=HTTP_REQ_ACCEPT


def cloud_encryption_instance():
    Service("cloud_encryption_service", CloudEncryptionHttpNonTransparentProxy, router=InbandRouter())
    Listener(SockAddrInet("172.16.30.2", 8080), "cloud_encryption_service")
