"""
camera_feed_exp.py

adapted from select-image-app-prototype.py

Version: 0.1

By: M.J. Camara

Allows user to take a picture of themselves for the program to reference during login
"""

# import opencv 
import cv2
import numpy as np
from eigenface import Eigenface
from controller import Controller 

"""
Wrapper class for the select image app.
"""
class CameraFeedExp:
	"""
	Returns a photo captured from the default webcam
	"""
	def capture(self, window_name, image_width, image_height, message):
		try:
			# Set webcam to variable
			camera = cv2.VideoCapture(0)

			# Set up user window
			cv2.namedWindow(window_name)

			# Image brightness offset
			brightness = 0

			# Setup eigenface file
			eigenface = Eigenface(Controller.TRAINING_DIR, Controller.USER_DIR, Controller.EIGENFACE_DIR, Controller.AVG_DIR, (Controller.IMAGE_HEIGHT, Controller.IMAGE_WIDTH))
			eigenface.build()
			# Infinite loop until escape is pressed or window closed
			while cv2.getWindowProperty(window_name, cv2.WND_PROP_VISIBLE) >= 1:
				# Read camera frames from webcam
				ret, frame = camera.read()

				# Grab dimensions of video capture
				video_width = camera.get(cv2.CAP_PROP_FRAME_WIDTH)
				video_height = camera.get(cv2.CAP_PROP_FRAME_HEIGHT)

				# Calculate x and y starting positions for highlight rectangle
				x_pos = (int(video_width) // 2) - (image_width)
				y_pos = (int(video_height) // 2) - (image_height)

				# Draw rectangle on live image
				# frame_temp = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
				# frame_copy = self.brighten(frame_temp,brightness)
				frame_copy = frame.copy()
				
				break_loop = False
				for i in range(int(video_width) - image_width):
					for j in range (int(video_height) - image_height):
						pos_face = cv2.cvtColor(frame_copy[j:j + image_height, i:i + image_width], cv2.COLOR_BGR2GRAY)
						fs_dist = eigenface.getFaceSpaceDistance(pos_face)
						break_loop = True if fs_dist < Controller.FACE_SPACE_THRESHOLD else False
					if (break_loop):
						x_pos = i + (image_width // 2)
						y_pos = j + (image_height // 2)
						break
				cv2.rectangle(frame_copy, 
					(x_pos - 8, y_pos - 8), 
					(x_pos + (image_width), y_pos + (image_height)), 
					(0, 0, 255), 
					thickness = 1, 
					lineType = 8, 
					shift = 0)
				cv2.putText(frame_copy,
					message,
					(0,25),
					cv2.FONT_HERSHEY_SIMPLEX,
					1,
					(0, 0, 255),
					3)
				# Show image in rendered window
				cv2.imshow(window_name, frame_copy)

				# If no frame is retrieved end loop
				if not ret:
					break
				# Set program to wait infinitely until keyboard input occurs
				keypress = cv2.waitKey(1)

				if keypress % 256 == 27:
					# ESC pressed, breaks out of loop
					break
				elif keypress % 256 == 32:
					# SPACE pressed
					# Crop image to desired length and return it
					captured_photo = frame[y_pos:y_pos + (image_height), x_pos:x_pos + (image_width)].copy()
					# captured_photo = cv2.cvtColor(captured_photo, cv2.COLOR_BGR2GRAY)
					# captured_photo = cv2.resize(captured_photo, (image_width, image_height))
					break
				elif keypress % 256 == 91:
					brightness -= 10
				elif keypress % 256 == 93:
					brightness += 10
			camera.release()
			cv2.destroyAllWindows()
			# return self.brightness(captured_photo, brightness)
			return captured_photo
		except cv2.error as e:
			print('Default webcam not found. Make sure the device is connected.')
			return None
	def brighten(self, image, offset):
		return image

if __name__ == '__main__':
	# Initialize class
	add_user_app = CameraFeedExp()
	photo = add_user_app.capture('Add as user', 178, 178, "Test")
	cv2.imwrite("test_photograph_3.jpg", photo)