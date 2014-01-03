class HttpProxyHeaderReplace(HttpProxy):
    def config(self):
        HttpProxy.config(self)
        self.request_header["User-Agent"] = (HTTP_HDR_CHANGE_VALUE, "Forged Browser 1.0")
