#!/usr/bin/python
# -*- coding: utf-8 -*-

import urllib, urllib2, cookielib
import json
import httplib
import zlib
from config import SharedParams
import commands

def create_opener():
    # debug flag
    # httpHandler = urllib2.HTTPHandler(debuglevel=1) 
    # httpsHandler = urllib2.HTTPSHandler(debuglevel=1) 

    # build cookie
    cj = cookielib.CookieJar();
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj));
    # opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj), httpHandler, httpsHandler);
    urllib2.install_opener(opener);
    return

def gzip_decode(resp, charset):
    if resp.startswith(b'\x1f\x8b'):  
        return zlib.decompress(resp, 16+zlib.MAX_WBITS).decode(charset)  
    else:  
        return resp.decode(charset)

def post(url, header, data):
    try:
        req = urllib2.Request(url, data, header)
        resp = urllib2.urlopen(req)
    except urllib2.HTTPError, e:
        print "--------ERROR occurs-----------------"
        print e.getcode()
        print "------"
        print e.geturl()
        print "------" 
        print e.info()
        print "------"
        print e.read()
        print "------"

    return gzip_decode(resp.read(), "UTF-8")

def get_jquery_by_url(target_url):
    username=SharedParams.get_username()
    password=SharedParams.get_password()

    url = "https://wam.inside.nsn.com/siteminderagent/forms/login.fcc"

    header = {
      "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36",
      "Content-Type": "application/x-www-form-urlencoded",
      "Accept-Encoding": "gzip, deflate, sdch, br",
      "Accept-Language": "en,zh-CN,zh;q=0.8,en;q=0.6,et;q=0.4,zh-TW;q=0.2,en-GB;q=0.4"
    }

    data = urllib.urlencode({
      "SMENC": "ISO-8859-1", 
      "SMLOCALE": "US-EN", 
      "USER": username, 
      "PASSWORD": password, 
      "target": target_url, 
      "smauthreason": 0, 
      "postpreservationdata": ""
    })

    return post(url, header, data)