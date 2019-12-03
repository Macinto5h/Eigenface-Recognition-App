# Eigenface-Recognition-App
Standalone python application with OpenCV that demonstrates facial recognition through the Eigenface algorithm.

# Installation

1. Required packages

To install the packages in Debian/Ubuntu Distros:

```bash
sudo apt install python3.6 python3-dev python3-pip libpam-dev git
sudo pip3 install opencv-python
```

For other distros, install the packages with the appropriate package tool or manually.

2. Installing the Program

**IMPORTANT: If configured incorrectly, this application could make `sudo` unusuable. Enable the `su` command for your user to access root privileges before attempting to install this program.**

To install the program follow the commands below and it will setup the files automatically.

```bash
git clone https://github.com/Macinto5h/Eigenface-Recognition-App/
cd ./Eigenface-Recognition-App/
chmod +x ./install_plugin.sh
chmod +x ./uninstall_plugin.sh
su
./install_plugin.sh
```

Add the following to the end of the `~.bashrc` file

```bash
# alias for eigencu add user
alias eigencu='/usr/local/libexec/sudo/eigencu_add_usr.o'
```

3. Uninstalling the Program

To Uninstall the program first run the uninstall shell file.

```bash
su
./uninstall_plugin.sh
```

Some lines appended to files need to be removed manually. 

The file `/etc/environment` has a line appended for EigenCU `export QT_X11_NO_MITSHM=1`. Remove the last instance of this line if there is more than one (means that other utilities may still need this setting or you ran `install_plugin.sh` more than once).

The file `~.bashrc` has the following appended that should be deleted by the user:

```bash
# alias for eigencu add user
alias eigencu='/usr/local/libexec/sudo/eigencu_add_usr.o'
```

4. User Images

To add an instance of the user's face into the system, run the command `eigencu -a`.

To export all instances of the user's face from the system into a directory, run the command `eigencu -e /directory/name/here`

To remove all instances of the user's face from the system, run the command `eigencu -r`

5. Running the program

This step is very simple: `sudo the_command_you_want_to_run`
