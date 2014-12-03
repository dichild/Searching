__author__ = 'Dichild'
# ver 0.1
import os
import urllib
import urllib2
import sys
import re
import urlparse
from collections import Counter
from sys import exit

import MySQLdb
import pygame

import semantic


global LEFT_PAGES
global InitialIndex


def check_en(word):
    for chara in word:
        if chara not in [u'a', u'b', u'c', u'd', u'e', u'f', u'g', u'h', u'i', u'j', u'k', u'l',
                         u'm', u'n', u'o', u'p', u'q', u'r', u's', u't', u'u', u'v', u'w', u'x', u'y', u'z']:
            return False
    return True


def UpdateSQL():
    # cur.execute('DROP TABLE')
    print 'sU'
    cur.execute(
        "CREATE  TABLE dataexchange SELECT indexer.words, group_concat(indexer.pages ORDER BY indexer.words SEPARATOR ',') AS 'words',group_concat(indexer.pagewords ORDER BY indexer.words SEPARATOR ',') AS 'words' from indexer GROUP BY indexer.words")
    cur.execute("DROP TABLE  indexer")
    cur.execute("CREATE TABLE indexer SELECT* FROM dataexchange")
    print 'eU'


def AddPagedicSQL(URL):  # Add url in mysql format : ID, Url
    try:  # start msql and creat stable at first time
        global InitialIndex
        InitialIndex = InitialIndex + 1

        print InitialIndex
        print 'sP'
        cur.execute('insert into pagedic values(%s,%s)', [InitialIndex, URL])
        conn.commit()
        print 'eP'
    except MySQLdb.Error, e:
        print "Mysql Error %d: %s" % (e.args[0], e.args[1])


def AddWordsSQL(word, frequency):  # Add url in mysql format : ID, Url
    global InitialIndex
    frequencydic = {InitialIndex: frequency}
    cur.execute('insert into indexer values(%s,%s,%s)', [word, InitialIndex, str(frequencydic)])  # eval str-dic
    conn.commit()


def CountFrequency(words):  # for a group of words
    word_counts = Counter(words)
    frequencies = word_counts.most_common(len(words))
    return frequencies  # format:[ ('eyes', 8), ('the', 5)]


def analyse_and_download():
    if len(LEFT_PAGES) == 0:
        print "No more pages!!! END"
        cur.close()
        conn.close()
        exit()

    urls_list = []
    for page in LEFT_PAGES:
        urls_list.append(page)
    # Process very link
    for HandledUrl in urls_list:
        try:
            linked_url = urllib2.urlopen(HandledUrl)
        except urllib2.HTTPError as err:
            print err.code
            continue
        finally:
            LEFT_PAGES.remove(HandledUrl)
        try:
            # Try to find which type of files(and judge it's html file or Others likes img, pdf..... )
            content_type = linked_url.headers.get("Content-Type")
            if content_type is not None:
                type1, type2 = content_type.split(";")[0].split("/")
                # print type1, type2
            link_ele = HandledUrl.split('/')
            if link_ele[-1].split('.')[-1] == type2:
                linkisfile = True
            else:
                linkisfile = False

            url_info = urlparse.urlparse(HandledUrl)  # analysing composition of links
            path_splited = url_info.path.split('/')  # rebuild links path and...
            if linkisfile == True:
                try:
                    end = path_splited.pop()
                except:
                    continue
                path_new = '/'.join(path_splited)
            else:
                path_new = url_info.path
            DirPath = 'doc/' + url_info.netloc + path_new
            if not os.path.exists(DirPath):  # and build directory path in local disk  Based on /doc/..
                os.makedirs(DirPath)

            if linkisfile == True:  # download file
                print HandledUrl, DirPath + '/' + end
                #urllib.urlretrieve(HandledUrl, DirPath + '/' + end)
            else:  # it is a dir
                print HandledUrl, DirPath + '/index' + '.' + type2
                #urllib.urlretrieve(HandledUrl, DirPath + '/index' + '.' + type2)

            # pick up all new links from old file
            if type1 == 'text':
                source = linked_url.read()
                if InitialIndex % 10 == 0:  # Update database for every 10 times
                    # UpdateSQL()
                    pass
                keywords = semantic.pasrsing(source)  # * * * * * * Get keywords * * * * * * *
                WordsFrequency = CountFrequency(keywords)
                print WordsFrequency
                if len(WordsFrequency)>0:
                    AddPagedicSQL(HandledUrl)  # Add url in Database, means it has meet and hanlded
                    for word in WordsFrequency:
                        if len(word[0]) < 15:
                            if check_en(word[0]):
                                AddWordsSQL(word[0], word[1])
                                pass
                            else:
                                pass

                current_url = linked_url.geturl()
                linked_url.close()
                hrefs = re.findall(PATTERN, source)
                if len(hrefs) > 0:
                    for each in hrefs:
                        href = each[1]
                        href = urlparse.urljoin(current_url, href)
                        href = href.replace("/../", "/")
                        if href not in HAS_FOUND_PAGES:  # Here needed to be improve. Now it's a simple String list
                            HAS_FOUND_PAGES.append(href)
                            LEFT_PAGES.append(href)  # Add new link in LEFT_PAGES
        except:
            print 'err'
            continue


if __name__ == '__main__':
    pygame.init()
    HAS_FOUND_PAGES = []
    try:  # start msql and creat stable at first time
        conn = MySQLdb.connect(host='localhost', user='root', passwd='', port=3306)
        cur = conn.cursor()
        conn.select_db('python')
        InitialIndex = cur.execute('select url from pagedic')
        result = cur.fetchall()
        for url in result:
            HAS_FOUND_PAGES.append(url[0])

    except MySQLdb.Error, e:
        print "Mysql Error %d: %s" % (e.args[0], e.args[1])

    LEFT_PAGES = []
    try:
        InFile = open(sys.argv[1])
    except:
        InFile = open('links')
    "Read links from dir file"
    for line in InFile:
        line = line.strip()
        LEFT_PAGES.append(line)
    InFile.close()

    for page in LEFT_PAGES:
        if page in HAS_FOUND_PAGES:
            LEFT_PAGES.remove(page)

    PATTERN = re.compile('(href|src|area)="([^\s;]+)"')
    while True:
        analyse_and_download()
