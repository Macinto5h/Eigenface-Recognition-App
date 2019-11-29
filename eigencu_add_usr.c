/* PAM development headers */
#include <security/pam_appl.h>
#include <security/pam_misc.h>
#include <stdlib.h>
#include <limits.h>
#include <python3.6/Python.h>
#include <string.h>
#include <pwd.h>
#include <unistd.h>
#include "ecuconst.h"

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

    // pam_unix returns 'Login Successful' without \n
    // To fix that I added this line
    printf("\n");

    // Run the add_user py object
    Py_Initialize();
    PyObject *sys_path = PySys_GetObject("path");
    char alt_path[PATH_MAX];
    // char *current_path = realpath(THIS_FILE_NAME, alt_path);
    // Works only with Linux systems...
    readlink("/proc/self/exe", alt_path, PATH_MAX);
    alt_path[strlen(alt_path) - strlen(THIS_FILE_NAME)] = 0;
    PyObject* alt_path_as_string = PyUnicode_FromString(alt_path);
    PyList_Append(sys_path, alt_path_as_string);
    Py_DECREF(alt_path_as_string);
    
    int try_count = 0;
    int add_finish = 0;
    char *msg;
    msg = "Press 'space' to add yourself as a user.";

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
        username,
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

    while (!add_finish && try_count < 3) {
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
        PyObject* input_photo = PyObject_CallMethod(call_cam_feed, 
            "capture", 
            "(s,i,i,s)",
            "Add as User",
            IMG_WIDTH,
            IMG_WIDTH,
            msg);
        if (input_photo == NULL) {
            PyErr_Print();
            printf("input_photo returned null \n");
            add_finish = 1;
        } else {
            
            // call the getFaceClassDist method of Eigenfaces
            PyObject* class_dist = PyObject_CallMethod(call_eigenface, 
                "getFaceClassDist",
                "(O)",
                input_photo);
            if (class_dist == NULL) {
                PyErr_Print();
                printf("class_dist returned null \n");
                add_finish = 1;
            }

            // call the getFaceSpaceDist method of Eigenfaces
            PyObject* space_dist = PyObject_CallMethod(call_eigenface,
                "getFaceSpaceDist",
                "(O)",
                input_photo);
            if (space_dist == NULL) {
                PyErr_Print();
                printf("space_dist returned null \n");
                add_finish = 1;
            }

            // Convert from PyObjects into doubles
            double face_class = PyLong_AsDouble(class_dist);
            double face_space = PyLong_AsDouble(space_dist);

            if (face_space < FS_THRES) {
                // Face is detected from input image
                if (face_class > FC_THRES) {
                    // Face is unknown, must be added to user
                    PyObject* add_img = PyObject_CallMethod(call_eigenface,
                        "addUserImage",
                        "(O)",
                        input_photo);
                    add_finish = 1;
                    printf("MSG: user image added successfully. \n");
                } else {
                    // Face is near identical to another photo in the system.
                    try_count++;
                    printf("MSG: user image near identical to previous entry. \n");
                    msg = "Image already in system";
                }
            } else {
                // Face is not detected.
                printf("MSG: face not found, please try again. \n");
                msg = "Face not found, try again";
            }
            Py_DECREF(class_dist);
            Py_DECREF(space_dist);
        }
        Py_DECREF(call_cam_feed);
        Py_DECREF(input_photo);
    }

    if (try_count == 3) {
        printf("MSG: Amount of attempts exceeded, program has automatically closed.");
    }
    Py_DECREF(call_eigenface);
    Py_DECREF(sys_path);
    Py_Finalize();
    return 1;
}