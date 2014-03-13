class ProxyDataHandlerBase(object):
    STATE_INIT = 0
    STATE_PARSED = 1
    STATE_CYPHERED = 2

    def __init__(self):
        self._state = ProxyDataHandlerBase.STATE_INIT

    def parse(self, plain_raw_data):
        self._state = ProxyDataHandlerBase.STATE_PARSED

        self._parse(plain_raw_data)

    def cypher(self, cypher, is_request):
        if self._state < ProxyDataHandlerBase.STATE_PARSED:
            raise TypeError('no plain data to cypher')

        #for item in vars(self):
        #    setattr(self, cypher.encrypt(getattr(self, item)) \
        #                  if is_request \
        #                  else cypher.decrypt(getattr(self, item)))

        self._state = ProxyDataHandlerBase.STATE_CYPHERED

    def compose(self):
        if self._state < ProxyDataHandlerBase.STATE_CYPHERED:
            raise TypeError('no chypered data to compose')

        return self._compose()

    def log(self, logger):
        pass

    def __dict__(self):
        if self._state < ProxyDataHandlerBase.STATE_PARSED:
            raise TypeError('no chypered data')

        return {}


import xml.etree.ElementTree as ET
class XMLProxyDataHandler(ProxyDataHandlerBase):

    def _parse(self, plain_raw_data):
        try:
            self._parsed_data = ET.fromstring(plain_raw_data)
        except ET.ParseError as e:
            raise e

    def _compose(self):
        try:
            cyphered_raw_data = ET.tostring(self._parsed_data)
            return cyphered_raw_data
        except AttributeError as e:
            raise TypeError(e)
