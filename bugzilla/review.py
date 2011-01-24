#!/usr/bin/env python

from bugzilla import Bugzilla
import subprocess
from subprocess import call, Popen
from urlparse import urlparse
import os.path
import re

BZ_URL='https://bugzilla.redhat.com/xmlrpc.cgi'
TRYTON_SOURCE_URL = "http://downloads.tryton.org/%(tryton_major)s/%(pkgname)s-%(version)s.tar.gz"
TRYTON_MAYOR = '1.8'

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
        ''' Use a rpm to quiry for a value'''
        qf = '%{' + macro.upper() + "}" # The RPM tag to search for
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
        
class PackageReview:
    def __init__(self,bug):
        self.bug_num = bug
        self.spec_url = None
        self.srpm_url = None
        self.spec_file = None
        self.srpm_file = None
        self.bugzilla = Bugzilla(url=BZ_URL)
        self.bug = self.bugzilla.getbug(self.bug_num)
        self.spec = None

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
                            
    def _check_upstream_md5(self):
        values = {
                  'tryton_major' : TRYTON_MAYOR,
                  'pkgname' : self.spec.name.replace("-","_"),
                  'version' : self.spec.version
                  }
        url = TRYTON_SOURCE_URL % values
        src = self._get_file(url)
        sum ,file = self._md5sum(src)      
        return sum 
                            
    def _run_cmd(self, cmd):
        cmd = cmd.split(' ')
        try:
            proc = Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            output, error = proc.communicate()
        except OSError, e:
            print "OSError : %s" % str(e)
        return output
    
    
    def _md5sum(self, file):
        cmd = "md5sum %s" % file
        out = self._run_cmd(cmd)
        lines = out.split(' ',1)
        if len(lines) == 2:
            return lines[0], lines[1][1:-1]
        else:
            return None,out
                            
                            
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

    def _check_local_md5(self):
        call('rpmdev-wipetree &>/dev/null', shell=True)
        call('rpm -ivh %s &>/dev/null' % self.srpm_file, shell=True)
        src = os.path.expanduser('~/rpmbuild/SOURCES/%s-%s.tar.gz' % (self.spec.name.replace("-","_"), self.spec.version))
        sum,file = self._md5sum(src)      
        return sum
    
    def check_md5(self):
        local = self._check_local_md5()
        upstream = self._check_upstream_md5()
        if local == upstream:
            check = "x"
        else:
            check = "!"
        print "[%s]  Sources used to build the package matches the upstream source, as provided in the spec URL." % check
        print "     MD5SUM this package     : %s" % local
        print "     MD5SUM upstream package : %s" % upstream                

    def process(self):
        self.find_urls()
        if self.download_files():
            self.spec = SpecFile(self.spec_file)
            self.check_md5()
        else:
            if not self.spec_url:
                print("no spec file found in bugzilla report #%s" % self.bug_num)
            if not self.srpm_url:
                print("no srpm file found in bugzilla report #%s" % self.bug_num)                            
            
if __name__ == "__main__":
    review = PackageReview(671434)
    review.process()
            
            
            
            
            
            
            
            
            
            
            
            
            
