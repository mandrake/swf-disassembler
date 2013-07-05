from scrapohr.scrapohr import *
import zlib

class SWF:
    def __init__(self, data):
        self.data = data
        self.meta = {}
        self.scrp = ScrapohrPro(data)
        self.scrapa()
        self.prettyprint()
    
    def prettyprint(self):
        for k in self.meta.keys():
            if k == 'tags':
                count = 0
                for t in self.meta[k]:
                    print 'Tag %d' % count
                    print 'Code: %d' % t['code']
                    print 'Length: %d' % t['len']
                    #print 'Data: ',
                    #print t['data']
                    print
                    count += 1
            else:
                print '%s: ' % k,
                print self.meta[k]

    def scrapa_rect(self):
        scrp = self.scrp
        ret = {}

        self.sz = scrp.getBits(5)
        ret['xmin'] = scrp.getSBits(self.sz)
        ret['xmax'] = scrp.getSBits(self.sz)
        ret['ymin'] = scrp.getSBits(self.sz)
        ret['ymax'] = scrp.getSBits(self.sz)

        return ret

    def scrapa_tag(self):
        s = self.scrp
        ret = {}

        tagCodeAndLength = s.getUI16(False)
        ret['code'] = tagCodeAndLength >> 6
        ret['len'] = tagCodeAndLength % (2**6)

        if ret['len'] == 0x3F:
            ret['len'] = s.getUI32(False)
        ret['data'] = s.getLBytes(ret['len'])
        return ret

    def scrapa(self):
        scrapac = self.scrp
        h = scrapac.getASCIIString(3)
        if h not in ['FWS', 'CWS', 'ZWS']:
            raise Exception('Wrong file format')

        self.meta['type'] = h
        self.meta['version'] = scrapac.getBytes(1)
        self.meta['length'] = scrapac.getUI32(False)

        if (self.meta['type'] == 'CWS'):
            dec = zlib.decompressobj().decompress(self.data[8:])
            if len(dec) + 8 != self.meta['length']:
                raise Exception('Length don\'t match')
            self.scrp = ScrapohrPro(dec)
            scrapac = self.scrp
        elif (self.meta['type'] == 'ZWS'):
            raise Exception('Not implemented yet')
        else:
            # ?????
            if len(self.data) != self.meta['length'] + 1:
                raise Exception('Length don\'t match')

        self.meta['frame_size'] = self.scrapa_rect()
        self.meta['frame_rate'] = scrapac.getUI16(True)
        self.meta['frame_count'] = scrapac.getUI16(False)
        self.meta['tags'] = []

        tag = self.scrapa_tag()
        while tag['code'] != 0:
            self.meta['tags'].append(tag)
            tag = self.scrapa_tag()
        self.meta['tags'].append(tag)

import urllib2
url = 'http://vimeo.com/moogaloop.swf?clip_id=31328220'
SWF(urllib2.urlopen(urllib2.Request(url)).read())