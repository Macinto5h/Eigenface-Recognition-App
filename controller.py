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
	IMAGE_HEIGHT = 218
	USER_DIR = "../users/"
	TRAINING_DIR = "../eigenface-training-images/"
	EIGENFACE_DIR = "./eigenfaces/"
	AVG_DIR = "./avg_face/"
	FACE_CLASS_THRESHOLD = 7.5 * (10 ** 7)
	# Still figuring out face space threshold
	FACE_SPACE_THRESHOLD = 5 * (10 ** 12)
