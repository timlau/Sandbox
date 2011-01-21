#!/usr/bin/env bash
fasLogin=timlau
repoLocalDir=~/udv/repos
repoName=yumex
rawhide=fedora-15
declare -a branch=(fedora-13 fedora-14 epel-6)
declare -a rpmdir=(i386 x86_64)
declare -a rsyncParam=(-avtz --delete)

cd $repoLocalDir
for dir2 in "${branch[@]}"
do
    echo -e "\033[31mUpdate $dir2 repos:\033[0m"
    cd $dir2
    # Bin RPM
    for dir3 in "${rpmdir[@]}"
    do
        echo -e "\033[34m\t* $dir3:\033[0m"
        cd $dir3
        rm -f *.rpm
        cp /var/lib/mock/$dir2-i386/result/yumex-*.noarch.rpm .
        cd ..
    done
    # SRPMS
    echo -e "\033[34m\t* SRPMS:\033[0m"
    cd SRPMS
    rm -f *.rpm
    cp /var/lib/mock/$dir2-i386/result/yumex-*.src.rpm .
    cd ..
    cd ..
done
cd ..
tree $repoLocalDir
