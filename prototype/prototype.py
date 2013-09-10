#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
Created on 4 wrz 2013

@author: kowald
'''

import urllib
import HTMLParser


class PrintAllHTMLParser(HTMLParser.HTMLParser):
    def handle_starttag(self, tag, attrs):
        print "Start tag:", tag
        for attr in attrs:
            print "     attr:", attr

    def handle_endtag(self, tag):
        print "End tag  :", tag

    def handle_data(self, data):
        print "Data     :", data

    def handle_comment(self, data):
        print "Comment  :", data

    '''def handle_entityref(self, name):
        c = unichr(name2codepoint[name])
        print "Named ent:", c'''

    def handle_charref(self, name):
        if name.startswith('x'):
            c = unichr(int(name[1:], 16))
        else:
            c = unichr(int(name))
        print "Num ent  :", c

    def handle_decl(self, data):
        print "Decl     :", data


class GetPicAndNextPageHTMLParser(HTMLParser.HTMLParser):
    def __init__(self):
        HTMLParser.HTMLParser.__init__(self)
        self.start = False

    def handle_starttag(self, tag, attrs):
        def print_tag(tag, attrs):
            print "Start tag:", tag
            for attr in attrs:
                print "     attr:", attr

        if (tag == 'div' and ('id', 'viewer') in attrs):
            self.start = True
            print_tag(tag, attrs)
        elif (tag == 'a' and self.start == True):
            print_tag(tag, attrs)
        elif (tag == 'img' and self.start == True):
            print_tag(tag, attrs)
        

    def handle_endtag(self, tag):
        if (tag == "div" and self.start == True):
            self.start = False
            print "End tag  :", tag


if __name__ == '__main__':
    print "Cześć"
    parser = GetPicAndNextPageHTMLParser()
    url = "http://mangafox.me/manga/naruto/v51/c479/1.html"
    parser.feed(urllib.urlopen(url).read())
