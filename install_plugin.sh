#!/bin/bash
# Script installs and compiles the files in the /usr/local/libexec/sudo directory
PROGDIR=/usr/local/libexec/sudo

# Copy all of the py/npy files into the directory
cp ./eigenface.py $PROGDIR/eigenface.py
cp ./camera_feed.py $PROGDIR/camera_feed.py

# Copy the c files into the directory
cp ./eigencu.c $PROGDIR/eigencu.c
cp ./eigencu_add_usr.c $PROGDIR/eigencu_add_usr.c
cp ./ecuconst.h $PROGDIR/ecuconst.h

# Compile the c files into the appropriate object files
gcc -shared -I/usr/include/python3.6 -I$PROGDIR -o $PROGDIR/eigencu.so -fPIC $PROGDIR/eigencu.c -L/usr/lib/python3.6/config-3.6m-x86_64-linux-gnu -lpython3.6
gcc -I/usr/include/python3.6 -I$PROGDIR -o $PROGDIR/eigencu_add_usr.o $PROGDIR/eigencu_add_usr.c -L/usr/lib/python3.6/config-3.6m-x86_64-linux-gnu -lpython3.6 -lpam -lpam_misc

# Create local dir for each user's content
# mkdir -m 777 /home/*/.eigencu/
for dir in /home/*/; do mkdir -m 777 $dir.eigencu; done
for dir in /home/*/.eigencu; do cp ./images.npy $dir/images.npy && chmod 777 $dir/images.npy; done