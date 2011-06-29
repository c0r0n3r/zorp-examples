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

class FtpProxyNonTransparent(FtpProxy):
	def config(self):
		FtpProxy.config(self)
		self.transparent_mode=FALSE

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
	Service(name="service_http_nontransparent_inband",
		proxy_class=HttpProxyNonTransparent,
		router=InbandRouter(forge_port=TRUE
		)
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
			 'dst_port' : 8080,
			 'src_zone' : ('clients', ),
			 'service'  : 'service_http_transparent_directed'
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
