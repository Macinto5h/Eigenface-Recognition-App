"""
login.py

Version 0.1

By: M.J. Camara
"""

import cv2
import os
import numpy as np
from camera_feed import CameraFeed
from eigenface import Eigenface
from controller import Controller

"""
Class that handles the login controller
"""
class LoginApp(Controller):
	"""
	Initializer starts the driver
	"""
	def __init__(self):
		feed = CameraFeed()

		photo = feed.capture("User login", self.IMAGE_WIDTH, self.IMAGE_HEIGHT)
		eigenface = Eigenface(self.TRAINING_DIR, self.USER_DIR, self.EIGENFACE_DIR, self.AVG_DIR, (self.IMAGE_HEIGHT, self.IMAGE_WIDTH))
		eigenface.build()
		fc_dist, fs_dist = eigenface.getDistances(cv2.cvtColor(photo, cv2.COLOR_BGR2GRAY))

		if (fs_dist < self.FACE_SPACE_THRESHOLD):
			if (fc_dist < self.FACE_CLASS_THRESHOLD):
				print("Login is successful")
			else:
				print("Failed to recognize user")
		else:
			print("Failed to recognize a face in the image.")
		print("This is fc dist: {:.2e}, this is fs dist: {:.2e}".format(fc_dist, fs_dist))
if __name__ == "__main__":
	login_app = LoginApp()