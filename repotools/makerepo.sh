#!/usr/bin/env bash
repoLocalDir=~/udv/repos
declare -a branches=(fedora-13 fedora-14 fedora-15 epel-6)
declare -a rpmdir=(i386 x86_64 noarch SRPMS)

IFS=",$IFS"
eval mkdir -pv $repoLocalDir/{"${branches[*]}"}/{"${rpmdir[*]}"}
