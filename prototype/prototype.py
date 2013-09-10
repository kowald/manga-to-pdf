#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
Created on 4 wrz 2013

@author: kowald
'''

MANGA_TITLE = 'naruto'
MANGA_CHAPTER = 600
TEMP_DIR = '/tmp/nar'

import sys
import os
import re
import urllib
import urlparse
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


#for PyLint
def dummy_log(s):
    s = s


class GetFirstPageHTMLParser(HTMLParser.HTMLParser):
    def __init__(self, chapter_number=0):
        HTMLParser.HTMLParser.__init__(self)
        self.__link_re = re.compile( \
            '.*\D0*{0}/\d*\.html'.format(chapter_number), re.IGNORECASE)
        self.__title_re = re.compile('.*\s{0}$'.format(chapter_number), \
                                   re.IGNORECASE)
        #print self.__link_re.pattern
        self.log_func = dummy_log
        self.__temp_link = None
        self.link = None

    def feed(self, data):
        self.__temp_link = None
        self.link = None
        HTMLParser.HTMLParser.feed(self, data)

    def handle_starttag(self, tag, attrs):
        def print_tag(tag, attrs):
            if self.log_func:
                self.log_func("Start tag: {0}\n".format(tag))
            for attr in attrs:
                if self.log_func:
                    self.log_func("     attr: {0}\n".format(attr))

        if ((tag == 'a')):
            href_ = title_ = class_ = False
            for attr in attrs:
                if len(attr) == 2:
                    if (attr[0] == 'href'):
                        href_ = attr[1]
                    elif (attr[0] == 'title'):
                        title_ = True
                    elif (attr[0] == 'class'):
                        class_ = True
            if (href_ and title_ and class_):
                self.__temp_link = href_
                print_tag(tag, attrs)

    def handle_data(self, data):
        if (self.__temp_link):
            if (self.__link_re.match(self.__temp_link) and
                self.__title_re.match(data)):
                self.link = self.__temp_link
                #self.log_func( \
                print(    'Found: {0} - {1}\n'.format(data, self.__temp_link))

    def handle_endtag(self, tag):
        if (tag == 'a' and self.__temp_link):
            self.__temp_link = None


class GetPicAndNextPageHTMLParser(HTMLParser.HTMLParser):
    def __init__(self):
        HTMLParser.HTMLParser.__init__(self)
        self.log_func = dummy_log
        self.start = 0
        self.link = None
        self.pic = None

    def feed(self, data):
        self.start = 0
        self.link = None
        self.pic = None
        HTMLParser.HTMLParser.feed(self, data)

    def handle_starttag(self, tag, attrs):
        def print_tag(tag, attrs):
            if self.log_func:
                self.log_func("Start tag: {0}\n".format(tag))
            for attr in attrs:
                if self.log_func:
                    self.log_func("     attr: {0}\n".format(attr))

        if ((tag == 'div') and
            ((('id', 'viewer') in attrs) or self.start > 0)):
            self.start += 1
            print_tag(tag, attrs)
        elif (tag == 'a' and self.start == 1):
            for attr in attrs:
                if len(attr) == 2:
                    if attr[0] == 'href':
                        self.link = attr[1]
            print_tag(tag, attrs)
        elif (tag == 'img' and self.start == 1):
            for attr in attrs:
                if len(attr) == 2:
                    if attr[0] == 'src':
                        self.pic = attr[1]
            print_tag(tag, attrs)

    def handle_endtag(self, tag):
        if (tag == "div" and self.start > 0):
            self.start -= 1
            if self.log_func:
                self.log_func("End tag  : {0}\n".format(tag))


if __name__ == '__main__':
    main_page = 'http://mangafox.me/manga/{0}'.format(MANGA_TITLE)
    print 'Connecting to main page: {0} to search for chapter: {1}'.format(main_page, MANGA_CHAPTER)
    page = urllib.urlopen(main_page)
    first_page_parser = GetFirstPageHTMLParser(MANGA_CHAPTER)
    #first_page_parser.log_func = sys.stdout.write
    first_page_parser.feed(page.read())
    if (not first_page_parser.link):
        print 'First page not found'
        exit(1)

    page_parser = GetPicAndNextPageHTMLParser()
    page_url = first_page_parser.link
    page_prefix = page_url[:str(page_url).rfind('/') + 1]
    #print page_prefix
    while page_url:
        print ('Connecting to url: {0}'.format(page_url))
        page_parser.feed(urllib.urlopen(page_url).read())
        if page_parser.pic:
            pic_url = page_parser.pic
            print '  Downloading picture...'
            print '  Picture url: {0}'.format(pic_url)
            picture = urllib.urlopen(pic_url).read()
            f = open(pic_url[str(pic_url).rfind('/') + 1:], 'wb')
            f.write(picture)
            f.close()
        if not page_parser.link:
            print 'Link to next page not found - STOP'
            exit(1)
        if ((page_parser.link.find('.html') < 0) or
        page_parser.link == 'javascript:void(0);'):
            page_url = None
        else:
            page_url = '{0}{1}'.format(page_prefix, page_parser.link)

    print 'Making PDF file'
