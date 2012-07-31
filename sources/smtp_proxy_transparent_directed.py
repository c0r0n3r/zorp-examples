from Zorp.Smtp import *

def default_instance():
    Service(name="service_smtp_transparent_directed", # <3>
            proxy_class=SmtpProxy,
            router=DirectedRouter(dest_addr=SockAddrInet('172.16.20.254', 25)) # <2>
    )
    Rule(service='service_smtp_transparent_directed', # <1>
         dst_port=25,
         src_zone=('dmz', ),
         dst_subnet=('172.16.40.1', )
    )

