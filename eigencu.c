// Plugin for sudo
#include <sudo_plugin.h>
#include <limits.h>
#include <python3.6/Python.h>
#include <string.h>

// Global definitions
#define PASS_MAX_LEN 1000
#define THIS_FILE_NAME "eigencu.so"

int conversation(int num_msgs,
	const struct sudo_conv_message msgs[],
	struct sudo_conv_reply replies[]) {

	Py_Initialize();
	PyObject *sys_path = PySys_GetObject("path");
	char alt_path[PATH_MAX];
	char *current_path = realpath(THIS_FILE_NAME, alt_path);
	alt_path[strlen(alt_path) - strlen(THIS_FILE_NAME)] = 0;
	PyObject* alt_path_as_string = PyUnicode_FromString(alt_path);
	PyList_Append(sys_path, alt_path_as_string);
	for (int i = 0; i < num_msgs; i++) {
		char pass[PASS_MAX_LEN];
		PyObject* login_mod = PyImport_ImportModule("login");
		if (login_mod == NULL) {
			PyErr_Print();
			return 0;
		}
		// Retrieve class in the module
		PyObject* login_app_class = PyObject_GetAttrString(login_mod, "LoginApp");
		if (login_app_class == NULL) return 0;
		Py_DECREF(login_mod);
		// Build arguments to be fed into class/function
		PyObject* resp_args = Py_BuildValue("()");
		if (resp_args == NULL) return 0;
		// Call login class
		PyObject* callable_login = PyObject_CallObject(login_app_class, resp_args);
		if (callable_login == NULL) return 0;
		Py_DECREF(login_app_class);
		Py_DECREF(resp_args);
		// Call run method
		PyObject* call_run_func = PyObject_CallMethod(callable_login, "run", "()");
		if (call_run_func == NULL) return 0;
		Py_DECREF(callable_login);
		// Convert output to a string format
		PyObject* run_func_repr = PyObject_Repr(call_run_func);
		if (run_func_repr == NULL) return 0;
		Py_DECREF(call_run_func);
		// Encode the string
		PyObject* run_func_str = PyUnicode_AsEncodedString(run_func_repr,"utf-8", "~E~");
		if (run_func_str == NULL) return 0;
		Py_DECREF(run_func_repr);
		// Move to string to char pointer
		char *output_to_str = PyBytes_AS_STRING(run_func_str);
		if (output_to_str == NULL) return 0;
		Py_DECREF(run_func_str);
		// Copy to pass array
		strcpy(pass, output_to_str);
		replies[i].reply = pass;
	}
	Py_DECREF(alt_path_as_string);
	Py_DECREF(sys_path);
	Py_Finalize();
	return 1;
}

int open(unsigned int version, 
	sudo_conv_t conversation, 
	sudo_printf_t plugin_printf,
	char * const settings[],
	char * const user_info[],
	char * const user_env[],
	char * const plugin_options[]) {

	// return successful open
	return 1;
}

void plugin_close(int exit_status, int error) {
	// do nothing
}

int show_version(int verbose) {
	return 1;
}

int check_policy(int argc, 
	char * const argv[],
	char *env_add[], 
	char **command_info[],
	char **argv_out[],
	char **user_env_out[]) {

	// bad idea to leave function like this.
	return 1;
}

int list(int argc,
	char * const argv[],
	int verbose,
	const char *list_user) {

	return 1;
}

int init_session(struct passwd *pwd, char **user_env[]) {
	return 1;
}


/*
struct policy_plugin {
	#define SUDO_POLICY_PLUGIN 1
	unsigned int type = SUDO_POLICY_PLUGIN;
	unsigned int version;
	int (*open)(unsigned int version, 
		sudo_conv_t conversation, 
		sudo_printf_t plugin_printf,
		char * const settings[],
		char * const user_info[],
		char * const user_env[],
		char * const plugin_options[])
	void (*close)(int exit_status,
		int error);
	int (*show_version)(int verbose);
	int (*check_policy)(int argc, 
		char * const argv[],
		char *env_add[],
		char **command_info[],
		char **argv_out[],
		char **user_env_out[]);
	int (*list)(int argc,
		char * const argv[],
		int verbose,
		const char *list_user);
	int (*validate)(void);
	void (*invalidate)(int remove);
	int (*init_session)(struct passwd *pwd, char **user_env[]);
	void (*register_hooks)(int version,
		int (*register_hook)(struct sudo_hook *hook));
	void (*deregister_hooks)(int version,
		int (*deregister_hook)(struct sudo_hook *hook));
}*/

struct policy_plugin eigencu_policy = {SUDO_POLICY_PLUGIN,
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