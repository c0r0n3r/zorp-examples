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

class CloudEncryptionStackedProxy(AnyPyProxy):
    stream = __import__('Zorp.Stream')

    def __init__(self, data_handler, cypher)
        super(CloudEncryptionStackedProxy).__init__()
        self.data_handler = data_handler
        self.cypher = cypher

    def config(self):
        self.client_max_line_length = 16384

    def getData(self):
        data = ""
        while True:
            try:
                data += self.client_stream.read(1024)
            except stream.StreamException, (code, lastline):
                if code == stream.G_IO_STATUS_EOF:
                    break
                else:
                    raise

        return data

    def proxyThread(self):
        try:
            plain_raw_data = self.getData()
            plain_parsed_data = self.data_handler.parse(plain_raw_data)
            plain_sensitive_data = self.data_handler.getData(plain_parsed_data)
            cyphered_parsed_data = self.data_handler.setData(parsed_data, cyphered_sensitive_data)
            cyphered_raw_data = self.data_handler.compose(cyphered_parsed_data)
            self.server_stream.write(cyphered_raw_data)
            proxyLog(self, "cypher.info", 3, "Data successfully cyphered")
        except TypeError as e:
            proxyLog(self, "cypher.error", 3, "Data cypher failed; error='%s'", e)
            

import xml.etree.ElementTree as ET
class GoogleCalendarProxy(CloudEncryptionStackedProxy):
    def processEventFeed(self, data, cypher_func):
        proxyLog(self, "cypher.info", 3, "processEventFeed")
        event_feed = gcalendar.CalendarEventFeedFromString(data)
        if event_feed is None:
            raise SyntaxError("event feed cannot be parsed")

        for entry in event_feed.entry:
            entry.title.text = cypher_func(entry.title.text)
            for where in entry.where:
                where.value_string = cypher_func(where.value_string)
            entry.content.text = cypher_func(entry.content.text)

        return event_feed.ToString()

    def processEventEntry(self, data, cypher_func):
        proxyLog(self, "cypher.info", 3, "processEventEntry '%s'", data)
        event_entry = gcalendar.CalendarEventEntryFromString(data)
        if event_entry is None:
            raise ET.ParseError(data)

        event_entry.title.text = cypher_func(event_entry.title.text)
        for where in event_entry.where:
            where.value_string = cypher_func(where.value_string)
        event_entry.content.text = cypher_func(event_entry.content.text)

        return event_entry.ToString()

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


class EncryptionHttpsProxy(MyHttpsKeyBrigeProxy):
    def config(self):
        MyHttpsKeyBrigeProxy.config(self)

        self.request_header["Accept-Encoding"]=(HTTP_HDR_CHANGE_VALUE, "identity")
        self.rewrite_host_header = FALSE

        self.request["GET"] = (HTTP_REQ_POLICY, self.filterOutIrrelevanTraffic)
        self.request["POST"] = (HTTP_REQ_POLICY, self.filterOutIrrelevanTraffic)

    def filterOutIrrelevanTraffic(self, method, url, version):
        raise NotImplementedError


class EncryptionHttpsGoogleCalendarProxy(EncryptionHttpsProxy):
    def filterOutIrrelevanTraffic(self, method, url, version):
        if self.request_url_file.startswith("/calendar/feeds"):
            self.request_stack["*"] = (HTTP_STK_DATA, (Z_STACK_PROXY, GoogleCalendarRequestProxy))
            self.response_stack["*"] = (HTTP_STK_DATA, (Z_STACK_PROXY, GoogleCalendarResponseProxy))
        return HTTP_REQ_ACCEPT


class CloudEncryptionHttpNonTransparentProxy(HttpProxyNonTransparent):
    def config(self):
        HttpProxyNonTransparent.config(self)
        self.connect_proxy=CloudEncryptionHttpsKeyBrigeProxy
        self.request["*"]=HTTP_REQ_ACCEPT


def cloud_encryption_instance():
	Service("cloud_encryption_service", CloudEncryptionHttpNonTransparentProxy, router=InbandRouter())
	Listener(SockAddrInet("172.16.30.2", 8080), "cloud_encryption_service")
