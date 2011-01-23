#!/usr/bin/env python

from bugzilla import Bugzilla
import subprocess
from subprocess import call, Popen
from urlparse import urlparse
import os.path
import re

BZ_URL='https://bugzilla.redhat.com/xmlrpc.cgi'

class SpecFile:
    def __init__(self, filename):
        self.filename = filename
        self.name = self.get_from_spec('name')
        self.version = self.get_from_spec('version')
        self.release = self.get_from_spec('release')
        f = None
        try:
             f = open(filename,"r")
             self.lines = f.readlines()
        finally:
             f and f.close()
             
    def get_from_spec(self, macro):
        
        qf = '%{' + macro.upper() + "}"
        print qf
         # get the name
        cmd = ['rpm', '-q', '--qf', qf, '--specfile', self.filename]
                # Run the command
        try:
            proc = Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            output, error = proc.communicate()
        except OSError, e:
            print "OSError : %s" % str(e)
        return output.split()[0]
            
             
    def parse(self):
        re_fields = { 
                  'source'    : [ re.compile(r"^Source\d*\s*:\s*(.*)", re.I) ]
                 }
        for line in self.lines:
            # check for release
            for attr in re_fields:
                re_list = re_fields[attr]
                for regex in re_list:
                    res = regex.search(line)
                    if res:
                        value = res.group(1)
                        setattr(self,attr, value)
                        print "%s : %s" % (attr,value)
        
class PackageReview:
    def __init__(self,bug):
        self.bug_num = bug
        self.spec_url = None
        self.srpm_url = None
        self.spec_file = None
        self.srpm_file = None
        self.bugzilla = Bugzilla(url=BZ_URL)
        self.bug = self.bugzilla.getbug(self.bug_num)

    def find_urls(self):
        if self.bug.longdescs:
            for c in self.bug.longdescs:
                body = c['body']
                urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', body)
                if urls:
                    for url in urls:
                        if url.endswith(".spec"):
                            self.spec_url = url
                        elif url.endswith(".src.rpm"):
                            self.srpm_url = url
                            
    def download_files(self):
        if self.spec_url and self.srpm_url:
            self.spec_file = self._get_file(self.spec_url)
            self.srpm_file = self._get_file(self.srpm_url)
            return True
        else:
            return False

    def _get_file(self, link):
        url = urlparse(link)
        fname = os.path.basename(url.path)
        call('wget --quiet --tries=1 --read-timeout=90 -O work/%s --referer=%s %s' % (fname, link, link) , shell=True)
        return "work/%s" % fname

    def install_srpm(self):
        call('rpmdev-wipetree 2>1 1>/dev/null', shell=True)
        call('rpm -ivh %s 2>1 1>/dev/null' % self.srpm_file, shell=True)
        call('md5sum ~/rpmbuild/SOURCES/*.tar.gz', shell=True)
            

    def process(self):
        self.find_urls()
        if self.download_files():
            self.install_srpm()
            spec = SpecFile(self.spec_file)
            print spec.name, spec.version, spec.release
            spec.parse()
        else:
            if not self.spec_url:
                print("no spec file found in bugzilla report #%s" % self.bug_num)
            if not self.srpm_url:
                print("no srpm file found in bugzilla report #%s" % self.bug_num)                            
            
if __name__ == "__main__":
    review = PackageReview(671434)
    review.process()
            
            
            
            
            
            
            
            
            
            
            
            
            
