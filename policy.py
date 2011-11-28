#############################################################################
## -*- coding: UTF-8 -*-
##
## Copyright (c) 2011 BalaBit IT Ltd, Budapest, Hungary
## Copyright (c) 2011 Szilárd Pfeiffer <szilard.pfeiffer@balabit.com>
## Copyright (c) 2011 Tibor Balázs <tibor.balazs@balabit.com>
##
## Authors: Szilárd Pfeiffer <szilard.pfeiffer@balabit.com>
##          Tibor Balázs <tibor.balazs@balabit.com>
##
## Permission is granted to copy, distribute and/or modify this document
## under the terms of the GNU Free Documentation License, Version 1.3
## or any later version published by the Free Software Foundation;
## with no Invariant Sections, no Front-Cover Texts, and no Back-Cover Texts.
## A copy of the license is included in the section entitled "GNU
## Free Documentation License".
##
#############################################################################

from Zorp.Core import *
from Zorp.Proxy import *

from Zorp.Ftp import *
from Zorp.Http import *
from Zorp.Pop3 import *
from Zorp.Smtp import *

InetZone(name="clients",
	 addr=["172.16.10.0/23", ], 
	 inbound_services=["*"],
	 outbound_services=["*"]
	)

InetZone(name="servers",
	 addr=["172.16.20.0/23", ],
	 inbound_services=["*"],
	 outbound_services=["*"]
	)

InetZone(name="servers.audit",
	 addr=["172.16.21.1/32", ],
	 inbound_services=["*"],
	 outbound_services=["*"],
	 admin_parent="servers"
	)

InetZone(name="servers.stack_clamav",
	 addr=["172.16.21.5/32", ],
	 inbound_services=["*"],
	 outbound_services=["*"],
	 admin_parent="servers"
	)

InetZone(name="servers.smtp_starttls",
	 addr=["172.16.21.9/32", ],
	 inbound_services=["*"],
	 outbound_services=["*"],
	 admin_parent="servers"
	)

InetZone(name="servers.smtp_one_sided_ssl",
	 addr=["172.16.21.13/32", ],
	 inbound_services=["*"],
	 outbound_services=["*"],
	 admin_parent="servers"
	)

InetZone(name="servers.http_stack_cat",
	 addr=["172.16.21.17/32", ],
	 inbound_services=["*"],
	 outbound_services=["*"],
	 admin_parent="servers"
	)

InetZone(name="servers.http_stack_tr",
	 addr=["172.16.21.21/32", ],
	 inbound_services=["*"],
	 outbound_services=["*"],
	 admin_parent="servers"
	)

InetZone(name="servers.http_header_replace",
	 addr=["172.16.21.25/32", ],
	 inbound_services=["*"],
	 outbound_services=["*"],
	 admin_parent="servers"
	)

InetZone(name="servers.http_url_filter",
	 addr=["172.16.21.29/32", ],
	 inbound_services=["*"],
	 outbound_services=["*"],
	 admin_parent="servers"
	)

InetZone(name="servers.plug",
	 addr=["172.16.21.33/32", ],
	 inbound_services=["*"],
	 outbound_services=["*"],
	 admin_parent="servers"
	)
	
class HttpProxyHeaderReplace(HttpProxy):
	def config(self):
		HttpProxy.config(self)
		self.request_header["User-Agent"] = (HTTP_HDR_CHANGE_VALUE, "Forged Browser 1.0")

class HttpProxyUrlFilter(HttpProxy):
        def config(self):
                HttpProxy.config(self)
                self.request["GET"] = (HTTP_REQ_POLICY, self.filterURL)

        def filterURL(self, method, url, version):
                if (url == "http://server_disallowed.zorp/"):
                        self.error_info = 'Access of this content is denied by the local policy.'
                        return HTTP_REQ_REJECT
                return HTTP_REQ_ACCEPT

class FtpProxyNonTransparent(FtpProxy):
	def config(self):
		FtpProxy.config(self)
		self.transparent_mode=FALSE

class SmtpProxyStartTls(SmtpProxy):
	def config(self):
		SmtpProxy.config(self)
		self.relay_zones=("*",)
		self.ssl.client_connection_security = SSL_ACCEPT_STARTTLS
		self.ssl.client_verify_type = SSL_VERIFY_OPTIONAL_UNTRUSTED
		self.ssl.client_keypair_files=(
					       "/etc/ssl/certs/ssl-cert-snakeoil.pem",
					       "/etc/ssl/private/ssl-cert-snakeoil.key"
                                              )
		self.ssl.server_verify_type = SSL_VERIFY_OPTIONAL_UNTRUSTED

class SmtpProxyOneSideSsl(SmtpProxy):
	def config(self):
		SmtpProxy.config(self)
		self.relay_zones=("*",)
		self.ssl.server_connection_security=SSL_FORCE_SSL
		self.ssl.server_verify_type=SSL_VERIFY_OPTIONAL_UNTRUSTED

class HttpsProxyKeybridge(HttpProxy):
	key_generator=X509KeyBridge(
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

	def config(self):
		HttpProxy.config(self)
		self.require_host_header=FALSE
		self.ssl.handshake_seq=SSL_HSO_SERVER_CLIENT
		self.ssl.key_generator = self.key_generator
		self.ssl.client_keypair_generate=TRUE
		self.ssl.client_connection_security=SSL_FORCE_SSL
		self.ssl.client_verify_type=SSL_VERIFY_OPTIONAL_UNTRUSTED
		self.ssl.server_connection_security=SSL_FORCE_SSL
		self.ssl.server_verify_type=SSL_VERIFY_REQUIRED_UNTRUSTED
		self.ssl.server_ca_directory="/etc/ssl/certs"
		self.ssl.server_trusted_certs_directory="/etc/zorp/certs"

def zorp_instance():
	#http services
	Service(name="service_http_transparent",
		proxy_class=HttpProxy,
		router=TransparentRouter()
	)
	Service(name="service_http_transparent_directed",
		proxy_class=HttpProxy,
		router=DirectedRouter(dest_addr=SockAddrInet('172.16.20.254', 80)
		)
	)
	Service(name="service_http_transparent_header_replace",
		proxy_class=HttpProxyHeaderReplace,
		router=TransparentRouter()
	)
	Service(name="service_http_transparent_url_filter",
		proxy_class=HttpProxyUrlFilter,
		router=TransparentRouter()
	)
	Service(name="service_http_nontransparent_inband",
		proxy_class=HttpProxyNonTransparent,
		router=InbandRouter(forge_port=TRUE
		)
	)

	#plug service
	Service(name="service_plug",
		proxy_class=PlugProxy,
		router=TransparentRouter()
	)

	#https services
	Service(name="service_https_transparent",
		proxy_class=HttpsProxyKeybridge,
		router=TransparentRouter()
	)

	#ftp services
	Service(name="service_ftp_transparent",
		proxy_class=FtpProxyRO,
		router=TransparentRouter()
	)
	Service(name="service_ftp_nontransparent_inband",
		proxy_class=FtpProxyNonTransparent,
		router=InbandRouter(forge_port=TRUE
		)
	)

	#smtp services
	Service(name="service_smtp_transparent",
		proxy_class=SmtpProxy,
		router=TransparentRouter()
	)
	Service(name="service_smtp_transparent_starttls",
		proxy_class=SmtpProxyStartTls,
		router=TransparentRouter()
	)
	Service(name="service_smtp_transparent_one_sided_ssl",
		proxy_class=SmtpProxyOneSideSsl,
		router=DirectedRouter(dest_addr=(SockAddrInet('172.16.20.254', 465),))
	)

	#transparent tcp dispatcher
	NDimensionDispatcher(bindto=DBSockAddr(SockAddrInet('172.16.10.254', 50000),
					       ZD_PROTO_TCP),
			     transparent=TRUE,
		rules=(
            		{
			 'dst_port' : 21,
			 'src_zone' : ('clients', ),
			 'dst_zone' : ('servers', ),
			 'service'  : 'service_ftp_transparent'
			},
            		{
			 'dst_port' : 80,
			 'src_zone' : ('clients', ),
			 'dst_zone' : ('servers', ),
			 'service'  : 'service_http_transparent'
			},
            		{
			 'dst_port' : 80,
			 'src_zone' : ('clients', ),
			 'dst_zone' : ('servers.http_header_replace', ),
			 'service'  : 'service_http_transparent_header_replace'
			},
            		{
			 'dst_port' : 80,
			 'src_zone' : ('clients', ),
			 'dst_zone' : ('servers.http_url_filter', ),
			 'service'  : 'service_http_transparent_url_filter'
			},
            		{
			 'dst_port' : 8080,
			 'src_zone' : ('clients', ),
			 'service'  : 'service_http_transparent_directed'
			},
            		{
			 'dst_port' : 443,
			 'src_zone' : ('clients', ),
			 'dst_zone' : ('servers.plug', ),
			 'service'  : 'service_plug'
			},
            		{
			 'dst_port' : 443,
			 'src_zone' : ('clients', ),
			 'dst_zone' : ('servers', ),
			 'service'  : 'service_https_transparent'
			},
			{
			 'dst_port': 25,
			 'src_zone': ('clients'),
			 'dst_zone': ('servers'),
			 'service': 'service_smtp_transparent'
			},
			{
			 'dst_port': 25,
			 'src_zone': ('clients'),
			 'dst_zone': ('servers.smtp_starttls'),
			 'service': 'service_smtp_transparent_starttls'
			},
			{
			 'dst_port': 25,
			 'src_zone': ('clients'),
			 'dst_zone': ('servers.smtp_one_sided_ssl'),
			 'service': 'service_smtp_transparent_one_sided_ssl'
			},
		)
	)

	#non-transparent tcp dispatcher
	NDimensionDispatcher(bindto=DBSockAddr(SockAddrInet('172.16.10.254', 50021),
					       ZD_PROTO_TCP),
			     transparent=FALSE,
		rules=(
            		{
			 'dst_port'   : 50021,
			 'dst_subnet' : ('172.16.10.254', ),
			 'src_zone'   : ('clients', ),
			 'service'    : 'service_ftp_nontransparent_inband'
			},
		)
	)

	NDimensionDispatcher(bindto=DBSockAddr(SockAddrInet('172.16.10.254', 50080),
					       ZD_PROTO_TCP),
			     transparent=FALSE,
		rules=(
            		{
			 'dst_port'   : 50080,
			 'dst_subnet' : ('172.16.10.254', ),
			 'src_zone'   : ('clients', ),
			 'service'    : 'service_http_nontransparent_inband'
			},
		)
	)

	#udp dispatcher
	NDimensionDispatcher(bindto=DBSockAddr(SockAddrInet('172.16.10.254', 60000),
					       ZD_PROTO_UDP),
		rules=(
		)
	)

def audit_instance():
	Service(name="service_ftp_transparent_audit",
		proxy_class=FtpProxy,
		router=TransparentRouter()
	)
	Service(name="service_http_transparent_audit",
		proxy_class=HttpProxy,
		router=TransparentRouter()
	)
	Service(name="service_pop3_transparent_audit",
		proxy_class=Pop3Proxy,
		router=TransparentRouter()
	)
	Service(name="service_smtp_transparent_audit",
		proxy_class=SmtpProxy,
		router=TransparentRouter()
	)

	#transparent tcp dispatcher
	NDimensionDispatcher(bindto=DBSockAddr(SockAddrInet('172.16.10.254', 70000),
					       ZD_PROTO_TCP),
			     transparent=TRUE,
		rules=(
            		{
			 'dst_port' : 21,
			 'src_zone' : ('clients', ),
			 'dst_zone' : ('servers.audit', ),
			 'service'  : 'service_ftp_transparent_audit'
			},
            		{
			 'dst_port' : 80,
			 'src_zone' : ('clients', ),
			 'dst_zone' : ('servers.audit', ),
			 'service'  : 'service_http_transparent_audit'
			},
            		{
			 'dst_port' : 110,
			 'src_zone' : ('clients', ),
			 'dst_zone' : ('servers.audit', ),
			 'service'  : 'service_pop3_transparent_audit'
			},
            		{
			 'dst_port' : 25,
			 'src_zone' : ('clients', ),
			 'dst_zone' : ('servers.audit', ),
			 'service'  : 'service_smtp_transparent_audit'
			},
		)
	)

class HttpProxyStackCat(HttpProxy):
	def config(self):
		HttpProxy.config(self)
		self.response_stack["GET"] = (HTTP_STK_DATA, (Z_STACK_PROGRAM, '/bin/cat'))

class HttpProxyStackTr(HttpProxy):
	def config(self):
		HttpProxy.config(self)
		self.request_header["Accept-Encoding"] = (HTTP_HDR_POLICY, self.processAcceptEncoding)
		self.response_stack["GET"] = (HTTP_STK_DATA, (Z_STACK_PROGRAM, '/usr/bin/tr \'[a-z]\' \'[A-Z]\''))

	def processAcceptEncoding(self, name, value):
		lst_value = value.split(',')
		if 'gzip' in lst_value:
			lst_value.remove('gzip')
		if 'bzip' in lst_value:
			lst_value.remove('bzip')
		if 'bzip2' in lst_value:
			lst_value.remove('bzip2')
		if 'compress' in lst_value:
			lst_value.remove('compress')
		self.current_header_value = ','.join(lst_value)
        
		return HTTP_HDR_ACCEPT

class HttpProxyStackClamav(HttpProxy):
    def config(self):
        HttpProxy.config(self)
        self.keep_persistent = TRUE
        self.response_stack["GET"] = (HTTP_STK_DATA, (Z_STACK_PROGRAM, '/etc/zorp/scripts/clamav_stack.py'))

class FtpProxyStackClamav(FtpProxy):
    def config(self):
        FtpProxy.config(self)
        self.request_stack["RETR"]=(FTP_STK_DATA, (Z_STACK_PROGRAM, '/etc/zorp/scripts/clamav_stack.py'))

def stack_instance():
	Service(name="service_http_transparent_stack_cat",
		proxy_class=HttpProxyStackCat,
		router=TransparentRouter()
	)
	Service(name="service_http_transparent_stack_tr",
		proxy_class=HttpProxyStackTr,
		router=TransparentRouter()
	)
	Service(name="service_http_transparent_stack_clamav",
		proxy_class=HttpProxyStackClamav,
		router=TransparentRouter()
	)
	Service(name="service_ftp_transparent_stack_clamav",
		proxy_class=FtpProxyStackClamav,
		router=TransparentRouter()
	)

	#transparent tcp dispatcher
	NDimensionDispatcher(bindto=DBSockAddr(SockAddrInet('172.16.10.254', 80000),
					       ZD_PROTO_TCP),
			     transparent=TRUE,
		rules=(
            		{
			 'dst_port' : 80,
			 'src_zone' : ('clients', ),
			 'dst_zone' : ('servers.http_stack_cat', ),
			 'service'  : 'service_http_transparent_stack_cat'
			},
            		{
			 'dst_port' : 80,
			 'src_zone' : ('clients', ),
			 'dst_zone' : ('servers.http_stack_tr', ),
			 'service'  : 'service_http_transparent_stack_tr'
			},
            		{
			 'dst_port' : 80,
			 'src_zone' : ('clients', ),
			 'dst_zone' : ('servers.stack_clamav', ),
			 'service'  : 'service_http_transparent_stack_clamav'
			},
            		{
			 'dst_port' : 21,
			 'src_zone' : ('clients', ),
			 'dst_zone' : ('servers.stack_clamav', ),
			 'service'  : 'service_ftp_transparent_stack_clamav'
			},
		)
	)

