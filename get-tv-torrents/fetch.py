#!/usr/bin/env python
"""
fetch.py - Downloads new torrents from tvrss.net feeds

Download torrent for the lastest episodes of tv serie.

The series must be defined in a file named 'series' in following format

Serie,Season

Ex.

Chuck,3

torrents will be download to a directory named torrents/ under the current work dir.
You must create that your self.

just run 'python fetch.py' to download the lastest torrents.

"""

import os, time, shelve, feedparser
from urlparse import urlparse

from datetime import date, timedelta

debug = False
start_date = date.today() - timedelta(days=21) # 14 days ago



def get_feed_url(serie, season):
    url ="http://ezrss.it/search/index.php?show_name=%s&quality=HDTV&season=%s&video_format=XVID&mode=rss" % (serie, season)
    return url

#base = os.getenv('HOME') + '/tvrss'
base = '.'

print "Reading active series"
file = open(base + "/series")
lines = [line[:-1] for line in file.readlines() if line.strip()]
file.close()
series = []
for line in lines:
    serie,season = line.split(",")
    if debug: print " --> Serie : %-40s Season : %-4s " % (serie,season)    
    serie = serie.replace(" ", "%20") # convert spaces to url spaces
    series.append("%s-%s" % (serie,season))

store = shelve.open(base + "/feeds.store", writeback=True)

todel = [line for line in store if not line in series]
for line in todel:
        del store[line]

for line in series:
        if line not in store:
                store[line] = start_date.timetuple()

store.sync()

#base_command = 'wget --quiet --tries=1 --read-timeout=90 -O out.torrent --referer=%s %s && transmission-remote --add out.torrent && rm out.torrent 1>/dev/null 2>&1'
base_command = 'wget --quiet --tries=1 --read-timeout=90 -O %s --referer=%s %s'

os.chdir(base)

print "Reading feeds"
for line in store:
        serie,season = line.split("-")
        print " --> Serie : %-40s Season : %-4s " % (serie.replace("%20"," "),season)    
        feed_url = get_feed_url(serie,season)
        feed = feedparser.parse(feed_url)
        last = store[line]
        for entry in feed.entries:
                url = urlparse(entry.link)
                if debug: print " --> Torrent : %s " % url.path[1:]
                if store[line] < entry.updated_parsed:
                        command = base_command % ("torrents%s" % url.path, entry.link, entry.link)
			if debug: print command 
                        if os.system(command) != 0:
                                print(" ----> Failed to add %s (%s)" % (entry.title, entry.link))
                        elif last < entry.updated_parsed:
                                last = entry.updated_parsed
                                #os.system('transmission-remote 192.168.0.222:9091 --add torrents%s' % url.path)
                                print(" ----> Added %s" % entry.title)
                else:
                    if debug: print " -----> Skipping :  Feed : %s  Store: %s) " % (time.asctime(entry.updated_parsed),time.asctime(store[line]))
        store[line] = last

store.close()

