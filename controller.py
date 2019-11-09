"""
controller.py

Version 0.1

By: M.J. Camara

Class that contains constants that are frequently used throughout the program. Used by controllers as an abstract class.
"""

class Controller:
	"""
	Constants frequently used throughout the program
	"""
	IMAGE_WIDTH = 178
	IMAGE_HEIGHT = 178
	USER_DIR = "../users/"
	TRAINING_DIR = "../eigenface-training-images/"
	EIGENFACE_DIR = "../eigenfaces/"
	AVG_DIR = "../avg_face/"
	FACE_CLASS_THRESHOLD = 6 * (10 ** 3)
	# Still figuring out face space threshold
	FACE_SPACE_THRESHOLD = 8 * (10 ** 3)
