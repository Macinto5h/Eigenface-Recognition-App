/* PAM development headers */
#include <security/pam_appl.h>
#include <security/pam_misc.h>
#include <stdlib.h>
#include <limits.h>
#include <python3.6/Python.h>
#include <string.h>
#include <pwd.h>
#include <unistd.h>

#define PASS_MAX_LEN 1000
#define THIS_FILE_NAME "eigencu_add_usr.o"

// custom conversation to communicate with PAM module
int conversation(int num_msg, const struct pam_message **msg, struct pam_response **resp, void *appdata_prt) {
	// Create an array of responses for the PAM module
    struct pam_response *array_resp = (struct pam_response*) malloc(num_msg * sizeof(struct pam_response));

    for (int i = 0; i < num_msg; i++) {
        array_resp[i].resp_retcode = 0;
        const char *msg_content = msg[i] -> msg;
        // printf("%s\n", msg_content);
        char pass[PASS_MAX_LEN];
        char *user_input = getpass(msg_content);
        strcpy(pass, user_input);
        array_resp[i].resp = (char *)malloc(strlen(pass) + 1);
        strcpy(array_resp[i].resp, pass);
    }
    *resp = array_resp;
    return PAM_SUCCESS;
}

/* structure for PAM conversation */
static struct pam_conv conv = {
	conversation, /* Conversation function defined in pam_misc.h */
	NULL /* No additional data need atm */ 
};

int main(int argc, char *argv[]) {
	pam_handle_t *handle = NULL;
	const char *service_name = "pam_example";
	int retval;
	char *username;

	retval = pam_start(service_name, NULL, &conv, &handle);
	if (retval != PAM_SUCCESS) {
		fprintf(stderr, "Failure in pam start: %s \n", pam_strerror(handle, retval));
		return 1;
	}

    struct passwd *p = getpwuid(getuid());
    username = p -> pw_name;

	pam_set_item(handle, PAM_USER, username);

	retval = pam_authenticate(handle, 0);
	if (retval != PAM_SUCCESS) {
		fprintf(stderr, "Failure in pam authentication: %s \n", pam_strerror(handle, retval));
		return 1;
	} 
	pam_end(handle, retval);

    // Run the add_user py object
    Py_Initialize();
    PyObject *sys_path = PySys_GetObject("path");
    char alt_path[PATH_MAX];
    // char *current_path = realpath(THIS_FILE_NAME, alt_path);
    // Works on with Linux systems...
    readlink("/proc/self/exe", alt_path, PATH_MAX);
    alt_path[strlen(alt_path) - strlen(THIS_FILE_NAME)] = 0;
    PyObject* alt_path_as_string = PyUnicode_FromString(alt_path);
    PyList_Append(sys_path, alt_path_as_string);
    Py_DECREF(alt_path_as_string);
    PyObject* add_user_mod = PyImport_ImportModule("add_user");
    if (add_user_mod == NULL) {
        fprintf(stderr, "ERROR: Failure to load add_user module.");
        return 1;
    }
    PyObject* add_user_class = PyObject_GetAttrString(add_user_mod, "AddUserApp");
    if (add_user_mod == NULL) {
        fprintf(stderr, "ERROR: Failure to reference AddUserApp class.");
        return 1;
    }
    Py_DECREF(add_user_mod);
    PyObject* class_args = Py_BuildValue("()");
    if (class_args == NULL) {
        fprintf(stderr, "ERROR: Failure to create method arguments.");
        return 1;
    }
    PyObject* callable_add_user = PyObject_CallObject(add_user_class, class_args);
    if (callable_add_user == NULL) {
        fprintf(stderr, "ERROR: Failure to initialize AddUserApp.");
        return 1;
    }
    Py_DECREF(add_user_class);
    Py_DECREF(class_args);
    PyObject* call_run_func = PyObject_CallMethod(callable_add_user, "run", "(s)", username);
    if (call_run_func == NULL) {
        printf("Enters this conditional");
        PyErr_Print();
        return 1;
    }
    Py_DECREF(callable_add_user);
    Py_DECREF(sys_path);
    Py_Finalize();
    return 1;
}