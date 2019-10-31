/* PAM development headers */
#include <security/pam_appl.h>
#include <security/pam_misc.h>
#include <stdlib.h>
#include <python3.6/Python.h>

#define PASS_MAX_LEN 1000

/* custom conversation function */
int conversation(int num_msg, const struct pam_message **msg, struct pam_response **resp, void *appdata_prt) {
	/* malloc an array of num_msg responses */
	struct pam_response *array_resp = (struct pam_response*) malloc(num_msg * sizeof(struct pam_response));

	/* Begin Python Initialization */
	Py_Initialize();
	// Get a reference to the main module
	PyObject* main_module = PyImport_AddModule("__main__");
	// Get the main module's dictionary
	PyObject* main_dict = PyModule_GetDict(main_module);

	printf("Num of messages is %d \n", num_msg);
	array_resp[0].resp_retcode = 0;
	const char *msg_content = msg[0] -> msg;
	printf("%s", msg_content);
	char pass[PASS_MAX_LEN];
	// Execute the file
	FILE* file = fopen("camera_feed.py", "r");
	PyObject* output = PyRun_File(file, "camera_feed.py", Py_file_input, main_dict, main_dict);
	PyObject* output_rep = PyObject_Repr(output);
	PyObject* output_str = PyUnicode_AsEncodedString(output_rep, "utf-8", "Error");
	const char *outputToString = PyBytes_AsString(output_str);
	strcpy(pass, outputToString);
	array_resp[0].resp = (char *)malloc(strlen(pass) + 1);
	strcpy(array_resp[0].resp, pass);
	Py_DECREF(output_str);
	Py_DECREF(output_rep);
	Py_DECREF(output);
	Py_DECREF(main_module);
	Py_DECREF(main_dict);
	Py_Finalize();
	*resp = array_resp;
	return PAM_SUCCESS;
}

/* structure for PAM conversation */
static struct pam_conv conv = {
	conversation, /* Conversation function defined in pam_misc.h */
	NULL /* No additional data need atm */ 
};

int main() {
	pam_handle_t *handle = NULL;
	const char *service_name = "pam_example";
	int retval;
	char *username;


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

	retval = pam_acct_mgmt(handle, 0);
	if (retval != PAM_SUCCESS) {
		fprintf(stderr, "Failure in pam mgmt: %s \n", pam_strerror(handle, retval));
		return 1;
	} else {
		printf("Pam acct mgmt success \n");
	}

	/*pam_get_item(handle, PAM_USER, (const void **)&username);
	printf("Welcome, %s\n", username);

	printf("Do you want to change your password? (answer y/n): ");
	char answer = getc(stdin);
	if (answer == 'y') {
		retval = pam_chauthtok(handle, 0);
		if (retval != PAM_SUCCESS) {
			fprintf(stderr, "Failure in pam password: %s", pam_strerror(handle, retval));
			return 1;
		}
	}*/
	pam_end(handle, retval);
}