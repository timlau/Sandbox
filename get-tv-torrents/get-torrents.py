#!/usr/bin/env python
'''
get-torrentsh.py - Downloads new torrents from tvrss.net feeds

Download torrent for the lastest episodes of tv serie.

The series must be defined in a file named 'series.ini' in following format

[Name of Serie]
episode = 1
last_episode = 0

torrents will be download to a directory named tv-torrents/ under ~/Download/tv-torrents.
You must create that your self.

just run './get-torrents.py' to download the lastest torrents.

'''

import os
import os.path
import feedparser
from urlparse import urlparse
from iniparse import INIConfig
from subprocess import call

# Constants
BASE_DIR = os.getenv('HOME') + '/.get-tv-torrents'
TORRENT_DIR = os.getenv('HOME') + '/Downloads/tv-torrents'
BASE_CMD = 'wget --quiet --tries=1 --read-timeout=90 -O %s --referer=%s %s'

class GetTorrents:
    def __init__(self):
        self._setup_dirs()
        self.cfg = self._read_ini()


    def _setup_dirs(self):
        for dir in (BASE_DIR, TORRENT_DIR):
            if not os.path.exists(dir):
                os.makedirs(dir)

    def _read_ini(self):
        ''' Read the series from the series.ini file '''
        fp = open(BASE_DIR + '/series.ini', "r")
        cfg = INIConfig(fp)
        fp.close()
        # Make sure we have need options in all sections else use defaults
        for section in cfg:
            if not 'last_episode' in cfg[section]:
                section.last_episode = 0
            if not 'season' in cfg[section]:
                section.season = 1
        return cfg

    def write_ini(self):
        ''' Write the series.ini back to disk '''
        f = open(BASE_DIR + '/series.ini',"w")
        print >>f, self.cfg
        f.close()    


    def get_summary_values(self, entry):
        ''' get values from the feed entry summary '''
        values = entry.summary.split(';')
        dict = {}
        i = 0
        for key in ['show','title',  'season', 'episode']:
            line = values[i]
            k,v = line.split(': ')
            dict[key] = v
            i += 1
        return dict


    def get_feed_url(self, serie, season):
        ''' get feed request url for a given serie and season'''
        serie=serie.replace(" ","%20")
        url ="http://ezrss.it/search/index.php?show_name=%s&quality=HDTV&season=%s&video_format=XVID&mode=rss" % (serie, season)
        return url

    def process(self):
        print("Processing Active Series")
        os.chdir(BASE_DIR)
        for serie in list(self.cfg): #Process the active series
                season = self.cfg[serie].season 
                last_episode = int(self.cfg[serie].last_episode)
                print("--> Serie : %-30s Season : %-4s Lastest Episode: %i " % (serie, season, last_episode))    
                feed_url = self.get_feed_url(serie,season)
                feed = feedparser.parse(feed_url)
                max_episode = 0
                new_episodes = set()
                for entry in feed.entries:
                    episode = self.get_summary_values(entry)
                    current_episode = int(episode['episode'])
                    if current_episode > max_episode: 
                        max_episode = current_episode
                    if current_episode > last_episode and not current_episode in new_episodes:
                        print "     NEW: show : %(show)s, title : %(title)s, season : %(season)s, episode : %(episode)s " % episode
                        url = urlparse(entry.link)
                        print "     --> Torrent : %s " % url.path[1:]
                        command = BASE_CMD % ("%s/%s" % (TORRENT_DIR, url.path), entry.link, entry.link)
                        if call(command) != 0:
                            print(" ----> Failed to add %s (%s)" % (entry.title, entry.link))
                        else:
                            if call('transmission-remote localhost:9091 --add %s' % "%s/%s" % (TORRENT_DIR, url.path)) != 0:
                                print("     --> Failed to add torrent to transmision")
                            else:
                                print("     --> Added to transmission %s" % entry.title)
                        new_episodes.add(current_episode)
                print "      Latest found episode : %i" % max_episode
                if max_episode > last_episode:
                    self.cfg[serie].last_episode = max_episode
        self.write_ini()

if __name__ == "__main__":
    app = GetTorrents()
    app.process()
    
    