# Eigenface-Recognition-App
Standalone python application with OpenCV that demonstrates facial recognition through the Eigenface algorithm.

# Installation
1. Required packages
Install the required packages by running the following commands.

```
sudo apt-get install python3.6 python3-dev python3-pip libpam-dev
pip install opencv-python
```

*There may be more libraries I have neglected to mention, but the ones above are the most significant.*

2. System Preparation

**IMPORTANT: If configured incorrectly, this application could make `sudo` unusuable. Enable the `su` command for your user before attempting to install this program.**

The plugin may only load a grey window when launched. To resolve this issue with X11 simply apply the following line to the bottom of the file `/etc/environment/`

`export QT_X11_NO_MITSHM=1`

To permanently add `eigencu` as a command for the user simply add this line to the end of the `~./bashrc` file

```
# alias for eigencu add user
alias eigencu='/usr/local/libexec/sudo/eigencu_add_usr.o'
```

To allow the eigencu add user utility to communicate with `unix-pam.so` the file `/etc/pam.d/eigencu_add_usr` needs to be added. The content of the file is as follows.

```
auth required  pam_unix.so
account required  pam_unix.so
password  required  pam_unix.so
```

The `/etc/sudo.conf` needs to modified so that it recognizes EigenCU as the policy plugin (If there is no file simply create one in the exact location). The content should look like the following.

```
Plugin eigencu_policy eigencu.so
Plugin sudoers_io sudoers.so
```

3. Installing the plugin
To install the program follow the commands below and it will setup the files automatically.

```
git clone https://github.com/Macinto5h/Eigenface-Recognition-App/
cd ./Eigenface-Recognition-App/
su
./install_plugin.sh
```

**More instructions to come in the near future**
