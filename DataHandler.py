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
from syslog import syslog
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

import gdata
import syslog
import xml.etree.ElementTree as ET
import xml.etree.cElementTree as cET
class GoogleCalendarProxyDataHandler(ProxyDataHandlerBase):
    namespaces = { ''           : 'http://www.w3.org/2005/Atom',
                   'gCal'       : 'http://schemas.google.com/gCal/2005',
                   'gd'         : 'http://schemas.google.com/g/2005',
                   'openSearch' : 'http://a9.com/-/spec/opensearchrss/1.0/',
                 }
    namespaces_registered = False

    def __init__(self):
        if not GoogleCalendarProxyDataHandler.namespaces_registered:
            for (prefix, uri) in GoogleCalendarProxyDataHandler.namespaces.iteritems():
                ET.register_namespace(prefix, uri)
            GoogleCalendarProxyDataHandler.namespaces_registered = True
        
    def _parse(self, plain_raw_data):
        syslog.syslog('parse \'%s\'' % plain_raw_data)
        try:
            self.gdata = gdata.GDataEntryFromString(plain_raw_data)
            syslog.syslog('parsed as gdataentry %s' % str(type(self.gdata)))
            return
        except cET.ParseError:
            pass
        try:
            self.gdata = gdata.GDataFeedFromString(plain_raw_data)
            syslog.syslog('parsed as gdata %s' % str(type(self.gdata)))
            return
        except cET.ParseError:
            pass
        self.gdata = None
        syslog.syslog('unknown %s' % plain_raw_data)

    def _cypher(self, cypher_func):
        if isinstance(self.gdata, gdata.GDataFeed):
            entries = self.gdata.entry
        elif isinstance(self.gdata, gdata.GDataEntry):
            entries = [self.gdata, ]
        else:
            return

        for entry in entries:
            entry.title.text = cypher_func(entry.title.text)

    def _compose(self):
        return str(self.gdata)
