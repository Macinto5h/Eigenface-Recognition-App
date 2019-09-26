"""
add_user.py

Version: 0.1

By: M.J. Camara

"""

import cv2
import os
from camera_feed import CameraFeed
from eigenface import Eigenface

"""
Wrapper class for the Add User Program
"""
class AddUserApp:

	"""
	Initializer runs the driver program
	"""
	def __init__(self):

		# "Constants"
		IMAGE_WIDTH = 178
		IMAGE_HEIGHT = 218
		USER_DIR = "./users/"


		# Variables for program loop
		loop_count = 0
		app_failure = False
		app_run = True
		feed = CameraFeed()

		while (app_run):

			photo = feed.capture('Add as User', IMAGE_WIDTH, IMAGE_HEIGHT)

			if photo is None:
				# Image is not being received properly, end the function
				app_failure = True
				app_run = False
			else:
				app_run = False
				# Run eigenface app on image
				# if it is face space proceed
				# if it is not a face class, add the user
				image_count = 0
				for image in os.listdir(USER_DIR):
					image_count += 1
				cv2.imwrite("{}{}.jpg".format(USER_DIR, image_count), photo)
				# else the user already exists in the system deny them.
				# if not in face space
					# bad image? Offers chance to retake image up to 2 more times
		print ("Image Retrieved Successfully" if not app_failure else "Photo failed to load")
		

if __name__ == '__main__':
	# Initialize class
	add_user_app = AddUserApp()