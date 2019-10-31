/*	custom PAM Module for eigenface application
    By: M.J. Camara
    Based on fedetasks's PAM module tutorial: https://fedetask.com/write-linux-pam-module/
*/

/* Include PAM headers */
#include <security/pam_ext.h>
#include <security/pam_modules.h>
#include <stdio.h>

/* PAM entry point for session creation */
int pam_sm_open_session(pam_handle_t *pamh, int flags, int argc, const char **argv) {
	printf("eigen_module MSG: open session called \n");
	return(PAM_SUCCESS);
}

/* PAM entry point for session cleanup */
int pam_sm_close_session(pam_handle_t *pamh, int flags, int argc, const char **argv) {
	return(PAM_SUCCESS);
}

/* PAM entry point for accounting */
int pam_sm_acct_mgmt(pam_handle_t *pamh, int flags, int argc, const char **argv) {
	return(PAM_SUCCESS);
}

/* PAM entry point for authentication verification */
int pam_sm_authenticate(pam_handle_t *pamh, int flags, int argc, const char **argv) {
	int pam_code;
	const char *username = NULL;
	const char *password = NULL;

	/* Ask for a username */
	pam_code = pam_get_user(pamh, &username, "User: ");
	if (pam_code != PAM_SUCCESS) {
		fprintf(stderr, "Username not found");
		return PAM_PERM_DENIED;
	}

	/* Ask for authentication token */
	pam_code = pam_get_authtok(pamh, PAM_AUTHTOK, &password, "Authentication: ");
	if (pam_code != PAM_SUCCESS) {
		fprintf(stderr, "Authentication token not found");
		return PAM_PERM_DENIED;
	}

	// TODO: Check for null password

	if (password != NULL) {
		printf("Login successful");
		return PAM_SUCCESS;
	} else {
		fprintf(stderr, "Wrong user or authentication");
		return PAM_PERM_DENIED;
	}
}

/* PAM entry point for setting user credentials 9that is, to actually establish the 
   authenticated user's credentials to the service provider) */
int pam_sm_setcred(pam_handle_t *pamh, int flags, int argc, const char **argv) {
	return(PAM_SUCCESS);
}

/* PAM entry point for authentication token (password) changes */
int pam_sm_chauthtok(pam_handle_t *pamh, int flags, int argc, const char **argv) {
	return(PAM_SUCCESS);
}