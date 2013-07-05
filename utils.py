import urllib2

def URL2html(url):
    return urllib2.urlopen(urllib2.Request(url)).read()

def URL2file(url, path):
    f = open(path, 'wb')
    resp = urllib2.urlopen(urllib2.Request(url))

    buf = resp.read(102400)
    while buf:
        f.write(buf)
        buf = resp.read(102400)
    f.close()