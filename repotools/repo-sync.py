#!/usr/bin/python

import os.path
import shutil
import os
import glob

package = 'yumex'
system_arch = 'i386'

fedora_branches = {
'13': 'fedora-13',
'14': 'fedora-14',
'rawhide': 'fedora-15'
}

epel_branches = {
'6' : 'epel-6'
}

archs = ['i386', 'x86_64', 'SRPMS']

mock_dir = "/var/lib/mock/%s-%s/result/%s-*.%s"
repo_dir = "/home/timlau/udv/repos"

def update_local_repo(branches, prefix="fedora"):
    for src in branches:
        target = branches[src]
        target_dir = repo_dir + '/' + target
        shutil.rmtree(target_dir, ignore_errors=True)
        for arch in archs:
            if arch == 'srpm':
                ext = 'src.rpm'
            else:
                ext = 'noarch.rpm'
            rpm_fn = mock_dir % (prefix+"-"+src, system_arch, package, ext)
            print "Source : ", rpm_fn
            arch_dir = target_dir+'/'+arch  
            print "Processing : %s" % arch_dir          
            os.makedirs(arch_dir)
            for fn in glob.glob(rpm_fn):
                print "  --> Copying : %s " % fn
                shutil.copy(fn, arch_dir)

update_local_repo(fedora_branches)
update_local_repo(epel_branches, prefix='epel')

