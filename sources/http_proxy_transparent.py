from Zorp.Http import * #1

def default_instance():
    Service(name='service_http_transparent', #2
            proxy_class=HttpProxy
    )
    Rule(service='service_http_transparent', dst_port=80, #3
         src_zone=('clients', ),
         dst_zone=('servers', )
    )
