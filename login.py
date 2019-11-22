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
	def run(self, user):
		feed = CameraFeed()

		photo = feed.capture("User login", self.IMAGE_WIDTH, self.IMAGE_HEIGHT, "Press 'Space' to Login")
		eigenface = Eigenface(self.IMAGE_WIDTH, user, self.FACE_NUMBER)
		gray_photo = cv2.cvtColor(photo, cv2.COLOR_BGR2GRAY)
		value = 0
		for i in range(gray_photo.shape[0]):
			for j in range(gray_photo.shape[1]):
				value += gray_photo[i,j]
		mean = value / (gray_photo.shape[0] * gray_photo.shape[1])
		dif = 110 - mean
		if dif > 0:
			for i in range(gray_photo.shape[0]):
				for j in range(gray_photo.shape[1]):
					if ((1.1*gray_photo[i,j]) + dif > 255):
						gray_photo[i,j] = 255
					else:
						gray_photo[i,j] = (1.1 * gray_photo[i,j]) + dif
		fc_dist, fs_dist = eigenface.getDistances(gray_photo)

		if (fs_dist < self.FACE_SPACE_THRESHOLD):
			if (fc_dist < self.FACE_CLASS_THRESHOLD):
				print("MESSAGE: Login successful")
				return True
			else:
				print("MESSAGE: Failed to recognize user")
		else:
			print("MESSAGE: Failed to recognize face")
		return False
if __name__ == "__main__":
	login_app = LoginApp()
	login_app.run("mac")