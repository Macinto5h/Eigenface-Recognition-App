#!/bin/bash
# Script installs and compiles the files in the /usr/local/libexec/sudo directory
DIR=/usr/local/libexec/sudo

# Set permissions of the npy files
chmod -R 777 $DIR/npy/

# Copy all of the py files into the directory
cp ./controller.py $DIR/controller.py
cp ./eigenface.py $DIR/eigenface.py
cp ./add_user.py $DIR/add_user.py
cp ./login.py $DIR/login.py
cp ./camera_feed.py $DIR/camera_feed.py

# Copy the npy files into the directory
cp -r ./npy/ $DIR/npy/

# Copy the c files into the directory
cp ./eigencu.c $DIR/eigencu.c
cp ./eigencu_add_usr.c $DIR/eigencu_add_usr.c

# Compile the c files into the appropriate object files
gcc -shared -I/usr/include/python3.6 -o $DIR/eigencu.so -fPIC $DIR/eigencu.c -L/usr/lib/python3.6/config-3.6m-x86_64-linux-gnu -lpython3.6
gcc -I/usr/include/python3.6 -o $DIR/eigencu_add_usr.o $DIR/eigencu_add_usr.c -L/usr/lib/python3.6/config-3.6m-x86_64-linux-gnu -lpython3.6 -lpam -lpam_misc