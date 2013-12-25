from Zorp.Http import *

def default_instance():
    Service(name="service_http_nontransparent_inband", # <2>
            proxy_class=HttpProxyNonTransparent, # <3>
            router=InbandRouter(forge_port=TRUE, forge_addr=TRUE) # <4>
    )
    Rule(service='service_http_nontransparent_inband', # <1>
         dst_port=3128,
         dst_subnet=('172.16.10.254', ),
         src_zone=('clients', )
    )
