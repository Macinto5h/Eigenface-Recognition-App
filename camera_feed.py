"""
camera_feed.py

adapted from select-image-app-prototype.py

Version: 0.1

By: M.J. Camara

Allows user to take a picture of themselves for the program to reference during login
"""

# import opencv 
import cv2

"""
Wrapper class for the select image app.
"""
class CameraFeed:
	"""
	Returns a photo captured from the default webcam
	"""
	def capture(self, window_name, image_width, image_height):
		try:
			# Set webcam to variable
			camera = cv2.VideoCapture(0)

			# Set up user window
			cv2.namedWindow(window_name)

			# Infinite loop until escape is pressed or window closed
			while cv2.getWindowProperty(window_name, cv2.WND_PROP_VISIBLE) >= 1:
				# Read camera frames from webcam
				ret, frame = camera.read()

				# Grab dimensions of video capture
				video_width = camera.get(cv2.CAP_PROP_FRAME_WIDTH)
				video_height = camera.get(cv2.CAP_PROP_FRAME_HEIGHT)

				# Calculate x and y starting positions for highlight rectangle
				x_pos = (int(video_width) // 2) - (image_width // 2)
				y_pos = (int(video_height) // 2) - (image_height // 2)

				# Create cropped image

				# Draw rectangle on live image
				cv2.rectangle(frame, 
					(x_pos - 8, y_pos - 8), 
					(x_pos + image_width, y_pos + image_height), 
					(0, 0, 0), 
					thickness = 1, 
					lineType = 8, 
					shift = 0)
				# Show image in rendered window
				cv2.imshow(window_name, frame)

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
					captured_photo = frame[y_pos:y_pos + image_height, x_pos:x_pos + image_width].copy()
					captured_photo = cv2.cvtColor(captured_photo, cv2.COLOR_BGR2GRAY)
					break
			camera.release()
			cv2.destroyAllWindows()
			return captured_photo
		except cv2.error as e:
			print('Default webcame not found. Make sure the device is connected.')
			return None

if __name__ == '__main__':
	# Initialize class
	add_user_app = CameraFeed()
	photo = add_user_app.capture('Add as user', 178, 218)
	cv2.imwrite("test_photograph.jpg", photo)