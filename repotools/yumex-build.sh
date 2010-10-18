#!/usr/bin/env bash

# use mock to build yumex for fedora-13 & fedora-14
mock -r fedora-13-i386 yumex*.src.rpm
mock -r fedora-14-i386 yumex*.src.rpm

