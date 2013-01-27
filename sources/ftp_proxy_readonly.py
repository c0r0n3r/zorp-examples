from Zorp.Ftp import *

Service(name="service_ftp_transparent", # <1>
        proxy_class=FtpProxyRO
)

Rule(service='service_ftp_transparent', # <2>
     dst_port=21,
     src_zone=('clients', ),
     dst_zone=('servers', )
)
