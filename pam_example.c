/* PAM development headers */
#include <security/pam_appl.h>
#include <security/pam_misc.h>
#include <stdlib.h>
#include <limits.h>
#include <python3.6/Python.h>
#include <string.h>

#define PASS_MAX_LEN 1000
#define THIS_FILE_NAME "pam_example.c"

// Global variable
char *mode;

/* custom conversation function */
int conversation(int num_msg, const struct pam_message **msg, struct pam_response **resp, void *appdata_prt) {
	// Create an array of responses for the PAM module
    struct pam_response *array_resp = (struct pam_response*) malloc(num_msg * sizeof(struct pam_response));
    // Initialize python/c api
    Py_Initialize();
    // Get the system path
    PyObject *sys_path = PySys_GetObject("path");
    // Declare char array to contain alternate path
    char alt_path[PATH_MAX];
    // Places the absolute path of this file into alt_path
    char *current_path = realpath(THIS_FILE_NAME, alt_path);
    // Remove the filename at the end of alt_path
    alt_path[strlen(alt_path) - strlen(THIS_FILE_NAME)] = 0;
    // Convert alt_path into a PyObject string
    PyObject* alt_path_as_string = PyUnicode_FromString(alt_path);
    // Append alt_path_to_string to the system path
	PyList_Append(sys_path, alt_path_as_string);
    // Iterate through all message received from pam_message
    for (int i = 0; i < num_msg; i++) {
    	// Set resp_retcode to zero
        array_resp[i].resp_retcode = 0;
        // Retrieve message from module
        const char *msg_content = msg[i] -> msg;
        // Declare pass method
        char pass[PASS_MAX_LEN]; 
        // Import the module to be used
        PyObject* login_mod = PyImport_ImportModule("login");
        if (login_mod == NULL) {
        	PyErr_Print();
        	return PAM_AUTH_ERR;
        }
        // Retrieve class in the module
        PyObject* login_app_class = PyObject_GetAttrString(login_mod, "LoginApp");
        if (login_app_class == NULL) return PAM_AUTH_ERR;
        Py_DECREF(login_mod);
        // Build arguments to be fed into class/function
        PyObject* resp_args = Py_BuildValue("()");
        if (resp_args == NULL) return PAM_AUTH_ERR;
        // Call login class
        PyObject* callable_login = PyObject_CallObject(login_app_class, resp_args);
        if (callable_login == NULL) return PAM_AUTH_ERR;
        Py_DECREF(login_app_class);
        Py_DECREF(resp_args);
        // Call run method
        PyObject* call_run_func = PyObject_CallMethod(callable_login, "run", "()");
        if (call_run_func == NULL) return PAM_AUTH_ERR;
        Py_DECREF(callable_login);
        // Convert output to a string format
        PyObject* run_func_repr = PyObject_Repr(call_run_func);
        if (run_func_repr == NULL) return PAM_AUTH_ERR;
        Py_DECREF(call_run_func);
        // Encode the string
        PyObject* run_func_str = PyUnicode_AsEncodedString(run_func_repr,"utf-8", "~E~");
        if (run_func_str == NULL) return PAM_AUTH_ERR;
        Py_DECREF(run_func_repr);
        // Move to string to char pointer
        char *output_to_str = PyBytes_AS_STRING(run_func_str);
        if (output_to_str == NULL) return PAM_AUTH_ERR;
        Py_DECREF(run_func_str);
        // Copy to pass array
        strcpy(pass, output_to_str);
        // Add pass to the response structure
        array_resp[i].resp = (char *)malloc(strlen(pass) + 1);
        strcpy(array_resp[i].resp, pass);
	}
	// Dereference PyObjects initialized before for loop
	Py_DECREF(alt_path_as_string);
	// End python functions
	Py_Finalize();
    *resp = array_resp; /* setting the param resp with our array of responses */ 
    /* Here we return PAM_SUCCESS, which means that the conversation happened correctly.
     * You should always check that, for example, the user didn't insert a NULL password etc */
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
	printf("argv 0: %s \n", argv[0]);
	printf("argv 1: %s \n", argv[1]);

	char *argument = argv[1];

	if (argc > 1 && strcmp(argument, "-a") == 0) {
		mode = "add_user";
	} else if (argc == 1 || strcmp(argument, "-l") == 0 ) {
		mode = "login";
	} else {
		printf("Invalid argument. To login use no argument or '-l'. To add yourself as a user use '-a'");
		return 1;
	}

	retval = pam_start(service_name, NULL, &conv, &handle);
	if (retval != PAM_SUCCESS) {
		fprintf(stderr, "Failure in pam start: %s \n", pam_strerror(handle, retval));
		return 1;
	} else {
		printf("Pam start success \n");
	}

	pam_set_item(handle, PAM_USER, "mac");

	retval = pam_authenticate(handle, 0);
	if (retval != PAM_SUCCESS) {
		fprintf(stderr, "Failure in pam authentication: %s \n", pam_strerror(handle, retval));
		return 1;
	} else {
		printf("Pam authenticate success \n");
	}
	pam_end(handle, retval);
}