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

	def run(self):
		# Variables for program loop
		try_count = 0
		usr_img_count = 0
		app_failure = False
		feed = CameraFeed()
		message = "Press 'space' to add yourself as a user."

		while ((not app_failure) and (try_count < 3) and (usr_img_count < 3)):
			photo = feed.capture('Add as User', self.IMAGE_WIDTH, self.IMAGE_HEIGHT, message)

			if photo is None:
				# Image is not being received properly, end the function
				app_failure = True
			else:
				# Run eigenface app on image
				eigenface = Eigenface(self.TRAINING_DIR, self.USER_DIR, self.EIGENFACE_DIR, self.AVG_DIR, (self.IMAGE_WIDTH, self.IMAGE_HEIGHT))
				eigenface.build()
				gray_photo = cv2.cvtColor(photo, cv2.COLOR_BGR2GRAY)
				value = 0
				for i in range(gray_photo.shape[0]):
					for j in range(gray_photo.shape[1]):
						value += gray_photo[i,j]
				mean = value / (gray_photo.shape[0] ** 2)
				# print("----- MEAN BRIGHTNESS IS: {}".format(mean))
				fc_dist, fs_dist = eigenface.getDistances(gray_photo)
				# if it is face space proceed
				# if it is not a face class, add the user
				if (fs_dist < self.FACE_SPACE_THRESHOLD):
					if ((fc_dist > self.FACE_CLASS_THRESHOLD and usr_img_count == 0) or (fc_dist < self.FACE_CLASS_THRESHOLD and usr_img_count > 0)):
						image_count = len(os.listdir(self.USER_DIR))
						cv2.imwrite("{}{}.jpg".format(self.USER_DIR, image_count), photo)
						try_count = 0
						usr_img_count += 1
						message = "Another pic at a different angle"
					else:
						# print("----- User already exists in the system")
						try_count += 1
						message = "User already in system."
				else:
					# print("----- face space distance too far")
					message = "Face not found, try again."
					try_count += 1
				# print("----- This is fc dist: {:.2e}, this is fs dist: {:.2e}".format(fc_dist, fs_dist))
		if (try_count == 3):
			print("MESSAGE: Amount of attempts exceeded, program has automatically closed.")
		elif (usr_img_count == 3):
			print("MESSAGE: All images have been received, user successfully added.")
			return True
		else:
			print ("MESSAGE: Photo failed to load")
		return False
if __name__ == '__main__':
	# Initialize class
	add_user_app = AddUserApp()