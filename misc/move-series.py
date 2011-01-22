#!/usr/bin/python -tt
import glob
import os.path
import shutil

series = {
'chuck' : ("Chuck","4"),
'stargate' : ('Stargate Universe',"2"),
'fringe' : ('Fringe',"3"),
'v' : ('V',"2")}


home = "/home/timlau"
location = home + "/Videos/tv/%s/Season %s/"

files = glob.glob((home +'/Downloads/*.avi'))
new_files = False

for fn in files:
    for serie in series:    
        p,f = os.path.split(fn)
        if f.lower().startswith(serie):
            target = location % series[serie]
            if not os.path.exists(target):
                os.makedirs(targets)
            if not os.path.exists('%s/%s' % (target,f)):
                print "Copying %s to %s " % (f, target)
                shutil.copy(fn,target)
                new_files = True

if new_files:
    os.system('sync-tv')
