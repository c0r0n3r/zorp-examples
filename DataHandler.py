class ProxyDataHandlerBase(object):
    STATE_INIT = 0
    STATE_PARSED = 1
    STATE_CYPHERED = 2

    def __init__(self)
        self._state = STATE_INIT

    def parse(self, raw_data)
        self.state = STATE_PARSED

        self._parse(raw_data)

    def cypher(self, cypher, is_request):
        if self._state < STATE_PARSED:
            raise TypeError('no chypered data')

        for item in self._items:
            self.item = cypher.encrypt(self.item)
                        if is_request
                        else cypher.decrypt(self.item)

    def compose(self):
        if self._state < STATE_CYPHERED:
            raise TypeError('no chypered data')

    def log(self, logger):
        pass


class XMLProxyDataHandler(object):
    ET = __import__('xml.etree.ElementTree')

    def parse(plain_raw_data):
        super(XMLProxyDataHandler, self).parse()

        try:
            self._plain_parsed_data = ET.fromstring(plain_raw_data)
        except xml.etree.ElementTree.ParseError as e:
            raise TypeError(e.what())

    def compose(self)
        super(XMLProxyDataHandler, self).compose()

        try:
            cyphered_raw_data = self._cyphered_parsed_data.tostring()
            return cyphered_raw_data
        except AttributeError as e:
            raise TypeError(e.what())

