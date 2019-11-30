#!/bin/bash
#Script uninstalls everything the install script added or modified
PROGDIR=/usr/local/libexec/sudo

# remove py files
rm $PROGDIR/eigenface.py
rm $PROGDIR/camera_feed.py

# remove c files
rm $PROGDIR/eigencu.c
rm $PROGDIR/eigencu.so
rm $PROGDIR/eigencu_add_usr.o
rm $PROGDIR/eigencu_add_usr.c

# remove hidden files in home dirs
for dir in /home/*/; do rm -r $dir.eigencu; done
