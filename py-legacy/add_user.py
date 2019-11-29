"""
add_user.py

Version: 0.1

By: M.J. Camara

"""

import cv2
from camera_feed import CameraFeed
from eigenface import Eigenface
from controller import Controller

"""
Wrapper class for the Add User Program
"""
class AddUserApp(Controller):
	# Run method starts the program, initializing the camera_feed
	def run(self, user):
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
				eigenface = Eigenface(self.IMAGE_WIDTH, user, self.FACE_NUMBER)
				gray_photo = cv2.cvtColor(photo, cv2.COLOR_BGR2GRAY)
				value = 0
				for i in range(gray_photo.shape[0]):
					for j in range(gray_photo.shape[1]):
						value += gray_photo[i,j]
				mean = value / (gray_photo.shape[0] ** 2)
				fc_dist, fs_dist = eigenface.getDistances(gray_photo)
				# if it is face space proceed
				# if it is not a face class, add the user
				if (fs_dist < self.FACE_SPACE_THRESHOLD):
					if ((fc_dist > self.FACE_CLASS_THRESHOLD and usr_img_count == 0) or (fc_dist < self.FACE_CLASS_THRESHOLD and usr_img_count > 0)):
						eigenface.add_user_image(gray_photo)
						try_count = 0
						usr_img_count += 1
						message = "Another pic at a different angle"
					else:
						try_count += 1
						message = "User already in system."
				else:
					message = "Face not found, try again."
					try_count += 1
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
	add_user_app.run("mac")