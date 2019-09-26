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

"""
Class that handles the login controller
"""
class LoginApp:
	"""
	Initializer starts the driver
	"""
	def __init__(self):
		# "constants"
		IMAGE_WIDTH = 178
		IMAGE_HEIGHT = 218
		USER_DIR = "./users"

		feed = CameraFeed()

		photo = feed.capture("User login", IMAGE_WIDTH, IMAGE_HEIGHT)
		eigenface = Eigenface("../eigenface-training-images/", "./users/", "./eigenfaces/", "./avg_face/", (IMAGE_HEIGHT, IMAGE_WIDTH))
		eigenface.build()
		fc_dist, fs_dist = eigenface.getDistances(photo)
		print("This is fc dist: {:.2e}, this is fs dist: {:.2e}".format(fc_dist, fs_dist))
if __name__ == "__main__":
	login_app = LoginApp()