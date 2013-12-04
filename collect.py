import urllib2
import sqlite3 as lite
import sys
from lxml import etree

def crawl():
    # init sqlite3
    con = lite.connect('feed.db')
    cur = con.cursor()
    
    # get url_id and subject
    cur.execute("SELECT id, subject FROM url")
    urls = cur.fetchall()
    
    for url in urls:
        url_id = url[0]
        url = "http://novel.munpia.com/{0}".format(url_id)
        url_subject = url[1]
    
        # get html
        usock = urllib2.urlopen(url)
        doc = usock.read()
        usock.close()
        
        # html parsing
        hparser = etree.HTMLParser(encoding='utf-8')
        doc = etree.fromstring(doc, hparser)
        articles = doc.xpath("//*[@id=\"ENTRIES\"]/tbody/tr")
        for a in articles:
            article_class = a.xpath("./@class")
            if len(article_class) > 0 and article_class[0] == "notice":
                continue
            article_id = a.xpath("./td[1]/span/text()")[0]
            article_subject = a.xpath("./td[2]/a[1]/text()")[0]
            article_link = 'http://novel.munpia.com' + a.xpath("./td[2]/a[1]/@href")[0]
            article_date = a.xpath("./td[3]/text()")[0]
        
            cur.execute("SELECT count(*) FROM article WHERE url_id = ? AND id = ?", (url_id, article_id))
            ret = cur.fetchall()
    
            # new article
            if(ret[0][0] == 0): 
                cur.execute("INSERT INTO article VALUES (?, ?, ?, ?)",
                        (url_id, article_id, article_subject, article_link))
                print "New article {0} {1} {2}".format(url_id, article_id, article_link)
        
        con.commit()
    
    con.close()

def newUrl(url_id):
    # init sqlite3
    con = lite.connect('feed.db')
    cur = con.cursor()
    
    # get url_id and subject
    cur.execute("SELECT count(*) FROM url WHERE id = ?", (url_id,))
    ret = cur.fetchone()
    if ret[0] != 0:
        print "Existing url id"
        return

    # get subject
    url = "http://novel.munpia.com/{0}".format(url_id)
    usock = urllib2.urlopen(url)
    doc = usock.read()
    usock.close()
        
    hparser = etree.HTMLParser(encoding='utf-8')
    doc = etree.fromstring(doc, hparser)
    subject = doc.xpath("//*[@id=\"board\"]/div[1]/div[2]/h2/a/text()")[0]

    cur.execute("INSERT INTO url VALUES (?, ?)", (url_id, subject))
    print "New url id: {0}".format(url_id)
    con.commit()
    con.close()

def usage():
    print "usage 1: python {0} crawl".format(sys.argv[0])
    print "usage 2: python {0} add <url id>".format(sys.argv[0])
    return

if len(sys.argv) == 1:
    usage()
    sys.exit(-1)

if sys.argv[1] == 'crawl':
    crawl()
else:
    if len(sys.argv) < 3:
        usage()
        sys.exit(-1)

    url_id = int(sys.argv[2])
    newUrl(url_id)
