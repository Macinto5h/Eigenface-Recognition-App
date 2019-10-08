"""
add_user.py

Version: 0.1

By: M.J. Camara

"""

import cv2
import os
from camera_feed import CameraFeed
from eigenface import Eigenface
from controller import Controller

"""
Wrapper class for the Add User Program
"""
class AddUserApp(Controller):

	"""
	Initializer runs the driver program
	"""
	def __init__(self):
		# Variables for program loop
		loop_count = 0
		app_failure = False
		app_run = True
		feed = CameraFeed()

		while (app_run):

			photo = feed.capture('Add as User', self.IMAGE_WIDTH, self.IMAGE_HEIGHT)

			if photo is None:
				# Image is not being received properly, end the function
				app_failure = True
				app_run = False
			else:
				app_run = False
				# Run eigenface app on image
				eigenface = Eigenface("../eigenface-training-images/", self.USER_DIR, "./eigenfaces/", "./avg_face/", (218, 178))
				eigenface.build()
				fc_dist, fs_dist = eigenface.getDistances(cv2.cvtColor(photo, cv2.COLOR_BGR2GRAY))
				# if it is face space proceed
				# if it is not a face class, add the user
				if (fs_dist < self.FACE_SPACE_THRESHOLD):
					if (fc_dist > self.FACE_CLASS_THRESHOLD):
						image_count = 0
						for image in os.listdir(self.USER_DIR):
							image_count += 1
						cv2.imwrite("{}{}.jpg".format(self.USER_DIR, image_count), photo)
					else:
						print("User already exists in the system")
				else:
					print("User face not detected")
				print("This is fc dist: {:.2e}, this is fs dist: {:.2e}".format(fc_dist, fs_dist))
				# else the user already exists in the system deny them.

				# if not in face space
					# bad image? Offers chance to retake image up to 2 more times
		print ("Image Retrieved Successfully" if not app_failure else "Photo failed to load")
		

if __name__ == '__main__':
	# Initialize class
	add_user_app = AddUserApp()