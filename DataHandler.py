from syslog import syslog

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

        syslog('%s %s' % (str(is_request), 'alma'))

        cypher_func = cypher.encrypt if is_request else cypher.decrypt
        self._cypher(cypher_func)

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
        syslog("%s" % plain_raw_data)
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

import json
class GoogleCalendarProxyDataHandler(ProxyDataHandlerBase):

    def _parse(self, plain_raw_data):
        syslog('parse \'%s\'' % plain_raw_data)
        try:
            self.data = json.loads(plain_raw_data)
            if self.data == None:
                raise JSONDecodeError("No JSON object could be decoded")
            syslog('parsed as json %s' % str(self.data))
            return
        except ValueError:
            pass
        self.data = None
        syslog('unknown %s' % plain_raw_data)

    def _cypher(self, cypher_func):
        if 'kind' in self.data and self.data['kind'] == 'calendar#events':
            for event in self.data['items']:
                event['summary'] = cypher_func(event['summary'])
        else:
            self.data['summary'] = cypher_func(self.data['summary'])

    def _compose(self):
        return json.dumps(self.data)
