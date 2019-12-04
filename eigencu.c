// Plugin for sudo
#define _GNU_SOURCE
#include <sudo_plugin.h>
#include <limits.h>
#include <python3.6/Python.h>
#include <string.h>
#include <pwd.h>
#include <grp.h>
#include <stdio.h>
#include <paths.h>
#include "ecuconst.h"

// Global definitions
#define PASS_MAX_LEN 1000
#define THIS_FILE_NAME "eigencu.so"
#define PACKAGE_VERSION "0.0.1a"

static struct plugin_state {
	char **envp;
	char * const *settings;
	char * const *user_info;
} plugin_state;
// Sudo conversation function with PAM
static sudo_conv_t sudo_conv;
// Print method for sudo
static sudo_printf_t sudo_log;
// User ID to run the program
static uid_t runas_uid = 0;
// Group ID to run the program
static gid_t runas_gid = -1;
// Sudo edit mode, default false
static int use_sudoedit = 0;
// Directory of plugin
const char *file_dir;
// User invoking sudo
const char *invoking_user = NULL;

static int open(
	unsigned int version, 
	sudo_conv_t conversation, 
	sudo_printf_t plugin_printf,
	char * const settings[],
	char * const user_info[],
	char * const user_env[],
	char * const plugin_options[]) {

	char * const *ui;
	char * const *usr;
	struct passwd *pw;
	const char *runas_user = NULL;
	struct group *gr;
	const char *runas_group = NULL;

	// Set conversation var
	if(!sudo_conv) {
		sudo_conv = conversation;
	}

	// Set print var
	if(!sudo_log) {
		sudo_log = plugin_printf;
	}

	// Test for correct API version
	if (SUDO_API_VERSION_GET_MAJOR(version) != SUDO_API_VERSION_MAJOR) {
		sudo_log(
			SUDO_CONV_ERROR_MSG,
			"the plugin requires API version %d.x\n",
			SUDO_API_VERSION_MAJOR);
	}

	// Only allow commands to be run as the root user
	for (ui = settings; *ui != NULL; ui++) {
		// Get runas_user from settings
		if (strncmp(*ui, "runas_user=", sizeof("runas_user=") - 1) == 0) {
			runas_user = *ui + sizeof("runas_user=") - 1;
		}
		// Get runas_group from settings
		if (strncmp(*ui, "runas_group=", sizeof("runas_group=") - 1) == 0) {
			runas_group = *ui + sizeof("runas_group=") - 1;
		}
		// Get progname from settings var
		if (strncmp(*ui, "progname=", sizeof("progname=") - 1) == 0) {
			// initprogname(*ui + sizeof("progname=") - 1);
		}
		// Check to see if sudo was called as sudoedit or with -e flag
		if (strncmp(*ui, "sudoedit=", sizeof("sudoedit=") - 1) == 0) {
			if (strcasecmp(*ui + sizeof("sudoedit=") - 1, "true") == 0) {
				use_sudoedit = 1;
			}
		}
		// Plugin does not support running sudo with no arguments
		if (strncmp(*ui, "implied_shell=", sizeof("implied_shell=") - 1) == 0) {
			if (strcasecmp(*ui + sizeof("implied_shell=") - 1, "true") == 0) {
				return -2;
			}
		}
		// Get the directory the plugin originated from
		if (strncmp(*ui, "plugin_dir=", sizeof("plugin_dir=") - 1) == 0) {
			file_dir = *ui + sizeof("plugin_dir=") -1;
		}
	}

	for (usr = user_info; *usr != NULL; usr++) {
		// Get the name of the user invoking sudo
		if (strncmp(*usr, "user=", sizeof("user=") - 1) == 0) {
			invoking_user = *usr + sizeof("user=") - 1;
		}
	}

	// Check to make sure user is known
	if (runas_user != NULL) {
		if ((pw = getpwnam(runas_user)) == NULL) {
			sudo_log(SUDO_CONV_ERROR_MSG, "unknown user %s\n", runas_user);
			return 0;
		}
		runas_uid = pw -> pw_uid;
	}

	// Check to make sure group is known
	if (runas_group != NULL) {
		if ((gr = getgrnam(runas_group)) == NULL) {
			sudo_log(SUDO_CONV_ERROR_MSG, "unknown group %s\n", runas_group);
			return 0;
		}
		runas_gid = gr -> gr_gid;
	}

	// Add values to plugin state struct
	plugin_state.envp = (char **)user_env;
	plugin_state.settings = settings;
	plugin_state.user_info = user_info;

	// return successful open
	return 1;
}

static void plugin_close(int exit_status, int error) {
	// Message print from sample sudo plugin
	if (error) {
		sudo_log(SUDO_CONV_ERROR_MSG, "Command error: %s\n", strerror(error));
	} else {
		if (WIFEXITED(exit_status)) {
			sudo_log(SUDO_CONV_INFO_MSG, "Command exited with status %d\n", WEXITSTATUS(exit_status));
		} else if (WIFSIGNALED(exit_status)) {
			sudo_log(SUDO_CONV_INFO_MSG, "Command killed by signal %d\n", WTERMSIG(exit_status));
		}
	}
}

static int show_version(int verbose) {
	// Based on original version function from sample plugin
	sudo_log(SUDO_CONV_INFO_MSG, "Eigencu policy plugin version %s\n", PACKAGE_VERSION);
	return 1;
}

static int check_authority(void) {

	Py_Initialize();

	PyObject *sys_path = PySys_GetObject("path");
	char alt_path[PATH_MAX];
	strcpy(alt_path, "/usr/local/libexec/sudo");
	PyObject* alt_path_as_string = PyUnicode_FromString(alt_path);
	PyList_Append(sys_path, alt_path_as_string);
	char pass[PASS_MAX_LEN];
	int breakpoint_index = 0;

	// Import the camera_feed py file
	PyObject* cam_feed_mod = PyImport_ImportModule("camera_feed");
	if (cam_feed_mod == NULL) {
	    PyErr_Print();
	    return 0;
	}

	// Fetch the CameraFeed class
	PyObject* cam_feed_cls = PyObject_GetAttrString(cam_feed_mod, "CameraFeed");
	if (cam_feed_cls == NULL) {
	    PyErr_Print();
	    return 0;
	} 
	Py_DECREF(cam_feed_mod);

	// Set empty args
	PyObject* cls_args = Py_BuildValue("()");
	if (cls_args == NULL) {
	    PyErr_Print();
	    return 0;
	}

	// Call and initialize CameraFeed object
	PyObject* call_cam_feed = PyObject_CallObject(cam_feed_cls, cls_args);
	if (call_cam_feed == NULL) {
	    PyErr_Print();
	    return 0;
	}
	Py_DECREF(cls_args);
	Py_DECREF(cam_feed_cls);

	// Retrieve input photo via capture method
	PyObject* input_photo = PyObject_CallMethod(call_cam_feed, 
            "capture", 
            "(s,i,i,s)",
            "Add as User",
            IMG_WIDTH,
            IMG_WIDTH,
            "Press 'Space' to Login");
	if (input_photo == NULL) {
		PyErr_Print();
		return 0;
	} else if (input_photo == Py_None) {
		printf("MSG: Window closed, cancelling operation\n");
		return 0;
	}
	Py_DECREF(call_cam_feed);

	// Import the eigenface py file
	PyObject* eigenface_mod = PyImport_ImportModule("eigenface");
	if (eigenface_mod == NULL) {
	    PyErr_Print();
	    return 0;
	}

	// Fetch the eigenface class
	PyObject* eigenface_cls = PyObject_GetAttrString(eigenface_mod, "Eigenface");
	if (eigenface_cls == NULL) {
	    PyErr_Print();
	    return 0;
	}
	Py_DECREF(eigenface_mod);

	// Create arguments needed for Eigenface class
	PyObject* eig_args = Py_BuildValue("(i,s,i)",
	    IMG_WIDTH,
	    invoking_user,
	    TOTAL_EIG);
	if (eig_args == NULL) {
	    PyErr_Print();
	    return 0;
	}

	// Call and initialize Eigenface Object
	PyObject* call_eigenface = PyObject_CallObject(eigenface_cls, eig_args);
	if (call_eigenface == NULL) {
	    PyErr_Print();
	    return 0;
	}
	Py_DECREF(eigenface_cls);
	Py_DECREF(eig_args);

	// call the getFaceClassDist method of Eigenfaces
	PyObject* class_dist = PyObject_CallMethod(call_eigenface, 
	    "getFaceClassDist",
	    "(O)",
	    input_photo);
	if (class_dist == NULL) {
	    PyErr_Print();
	    return 0;
	}

	// call the getFaceSpaceDist method of Eigenfaces
	PyObject* space_dist = PyObject_CallMethod(call_eigenface,
	    "getFaceSpaceDist",
	    "(O)",
	    input_photo);
	if (space_dist == NULL) {
	    PyErr_Print();
	    return 0;
	}

	// Convert from PyObjects into doubles
	double face_class = PyFloat_AsDouble(class_dist);
	double face_space = PyFloat_AsDouble(space_dist);

	Py_DECREF(class_dist);
    Py_DECREF(space_dist);
    Py_DECREF(call_eigenface);
    Py_DECREF(input_photo);
	Py_DECREF(alt_path_as_string);
	Py_DECREF(sys_path);

	Py_Finalize();

	if (face_space < FS_THRES && face_class < FC_THRES) {
		printf("MSG: Face successfully recognized! \n");
		return 1;
	} else {
		printf("MSG: Face not recognized or found. \n");
		return 0;
	}
}

static char * find_in_path(char *command, char **envp) {
	struct stat sb;
	char *path, *path0, **ep, *cp;
	char pathbuf[PATH_MAX], *qualified = NULL;

	if (strchr(command, '/') != NULL) {
		return command;
	}

	path = _PATH_DEFPATH;
	for (ep = plugin_state.envp; *ep != NULL; ep++) {
		if (strncmp(*ep, "PATH=", 5) == 0) {
			path = *ep + 5;
			break;
		}
	}
	path = path0 = strdup(path);
	do {
		if ((cp = strchr(path, ':'))) {
			*cp = '\0';
		}
		snprintf(pathbuf, sizeof(pathbuf), "%s/%s", *path ? path : ".", command);
		if (stat(pathbuf, &sb) == 0) {
			if (S_ISREG(sb.st_mode) && (sb.st_mode & 0000111)) {
				qualified = pathbuf;
				break;
			}
		}
		path = cp + 1;
	} while (cp != NULL);
	free(path0);
	return qualified ? strdup(qualified) : NULL;
}

static char * sudo_new_key_val(const char *key, const char *val) {
	size_t key_len = strlen(key);
	size_t val_len = strlen(val);
	char *cp, *str;

	cp = str = malloc(key_len + 1 + val_len + 1);
	if (cp != NULL) {
		memcpy(cp, key, key_len);
		cp += key_len;
		*cp++ = '=';
		memcpy(cp, val, val_len);
		cp += val_len;
		*cp = '\0';		
	}

	return str;
}

static char ** build_command_info(const char *command) {
	static char **command_info;
	int i = 0;

	// Setup
	command_info = calloc(32, sizeof(char *));
	if (command_info == NULL) {
		return NULL;
	}

	if ((command_info[i++] = sudo_new_key_val("command", command)) == NULL ||
		asprintf(&command_info[i++], "runas_euid=%ld", (long)runas_uid) == -1 ||
		asprintf(&command_info[i++], "runas_uid=%ld", (long)runas_uid) == -1) {
		return NULL;
	}

	if (runas_gid != (gid_t) - 1) {
		if (asprintf(&command_info[i++], "runas_gid=%ld", (long)runas_gid) == -1 ||
			asprintf(&command_info[i++], "runas_egid=%ld", (long)runas_gid) == -1) {
			return NULL;
		}
	}

	if (use_sudoedit) {
		command_info[i] = strdup("sudoedit=true");
		if (command_info[i++] == NULL) {
			return NULL;
		}
	}
#ifdef USE_TIMEOUT
	command_info[i++] = "timeout=30";
#endif
	return command_info;
}

static char * find_editor(int nfiles, char * const files[], char **argv_out[]) {
	char *cp, *last, **ep, **nargv, *editor, *editor_path;
	int ac, i, nargc, wasblank;

	// Find editor in user env
	editor = _PATH_VI;
	for (ep = plugin_state.envp; *ep != NULL; ep++) {
		if (strncmp(*ep, "EDITOR=", 7) == 0) {
			editor = *ep + 7;
			break;
		}
	}
	editor = strdup(editor);
	if (editor == NULL) {
		sudo_log(SUDO_CONV_ERROR_MSG, "unable to allocate memory\n");
		return NULL;
	}

	nargc = 1;
	for (wasblank = 0, cp = editor; *cp != '\0'; cp++) {
		if (isblank((unsigned char) *cp)) {
			wasblank = 1;
		} else if (wasblank) {
			wasblank = 0;
			nargc++;
		}
	}

	// Give up if editor is not found in user's PATH
	cp = strtok_r(editor, "\t", &last);
	if (cp == NULL || (editor_path = find_in_path(editor, plugin_state.envp)) == NULL) {
		free(editor);
		return NULL;
	}

	if (editor_path != editor) {
		free(editor);
	}

	nargv = malloc((nargc + 1 + nfiles + 1) * sizeof(char *));
	if (nargv == NULL) {
		sudo_log(SUDO_CONV_ERROR_MSG, "unable to allocate memory \n");
		free(editor_path);
		return NULL;
	}

	for (ac = 0; cp != NULL && ac < nargc; ac++) {
		nargv[ac] = cp;
		cp = strtok_r(NULL, "\t", &last);
	}
	nargv[ac++] = "--";
	for (i = 0; i < nfiles;) {
		nargv[ac++] = files[i++];
	}
	nargv[ac] = NULL;

	*argv_out = nargv;
	return editor_path;
}



static int check_policy(
	int argc, 
	char * const argv[],
	char *env_add[], 
	char **command_info[],
	char **argv_out[],
	char **user_env_out[]) {

	char *command;

	if (!argc || argv[0] == NULL) {
		sudo_log(SUDO_CONV_ERROR_MSG, "no command specified\n");
		return 0;
	}

	if (!check_authority()) {
		return 0;
	}

	command = find_in_path(argv[0], plugin_state.envp);
	if (command == NULL) {
		sudo_log(SUDO_CONV_ERROR_MSG, "%s: command not found\n", argv[0]);
		return 0;
	}

	// If sudo vi is run, auto-convert to sudoedit
	if (strcmp(command, _PATH_VI) == 0) {
		use_sudoedit = 1;
	}

	if (use_sudoedit) {
		// Rebuild argv using editor
		free(command);
		command = find_editor(argc - 1, argv + 1, argv_out);
		if (command == NULL) {
			sudo_log(SUDO_CONV_ERROR_MSG, "unable to find valid editor\n");
			return -1;
		}
		use_sudoedit = 1;
	} else {
		*argv_out = (char **)argv;
	}

	// no changes to envp
	*user_env_out = plugin_state.envp;

	// Setup command
	*command_info = build_command_info(command);
	free(command);
	if (*command_info == NULL) {
		sudo_log(SUDO_CONV_ERROR_MSG, "out of memory\n");
		return -1;
	}

	return 1;
}

static int list(
	int argc,
	char * const argv[],
	int verbose,
	const char *list_user) {

	// Based on original list function from sample plugin
	sudo_log(SUDO_CONV_INFO_MSG, "Validate users may run any command\n");
	return 1;
}

struct policy_plugin eigencu_policy = {
	SUDO_POLICY_PLUGIN,
	SUDO_API_VERSION,
	open,
	plugin_close,
	show_version,
	check_policy,
	list,
	NULL,
	NULL,
	NULL,
	NULL,
	NULL
};
