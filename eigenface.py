"""
eigenface.py

Version 0.1

By: M.J. Camara

Implements the Eigenface algorithm in its own class with functions
"""

# import opencv
import cv2
import os
import sys
import numpy as np
# from Crypto.Hash import SHA256
import Crypto.Hash.SHA256 

"""
Eigenface class that contains all of its functions, fields, etc.
"""
class Eigenface:

	"""
	Initializer
	"""
	def __init__(self, image_dim, user, face_number):
		# Establish cwd as dir that file is located in
		abspath = os.path.abspath(__file__)
		dname = os.path.dirname(abspath)
		os.chdir(dname)
		# "Constants"
		self.FACE_NUMBER = face_number
		self.IMAGE_DIM = image_dim
		self.current_user = user

		# Define fields by loading pre-existing files, otherwise set to none.
		# images used as training set
		try:
			self.images = np.load("./npy/images.npy")
		except IOError:
			self.images = []

		# set of images that pertain to users
		try:
			hash = Crypto.Hash.SHA256.new()
			hash.update(self.current_user.encode('utf-8'))
			self.users = np.load("./npy/{}.npy".format(hash.hexdigest()))
			self.user_photo_count = self.users.shape[0]
		except IOError:
			self.users = np.zeros((1, self.IMAGE_DIM ** 2))
			self.user_photo_count = 0

		# Average face in the system
		try:
			self.avg_face = np.load("./npy/avg_face.npy")
		except IOError:
			self.avg_face = np.zeros((self.IMAGE_DIM, self.IMAGE_DIM))

		# Eigenfaces
		try: 
			self.eigenfaces = np.load("./npy/eigenfaces.npy")
		except IOError:
			self.eigenfaces = np.zeros((self.FACE_NUMBER, self.IMAGE_DIM ** 2))

		# Eigenfaces normalized into unit vectors
		try:
			self.eigenfaces_norm = np.load("./npy/eigenfaces_norm.npy")
		except IOError:
			self.eigenfaces_norm = np.zeros((self.FACE_NUMBER, self.IMAGE_DIM ** 2))

	# ----- METHODS -----

	def addUserImage(self, image):
		tmp_array = np.zeros((self.user_photo_count + 1, self.IMAGE_DIM ** 2))
		for i in range (self.user_photo_count):
			tmp_array[i,:] = self.users[i,:]
		tmp_array[self.user_photo_count,:] = image.flatten()
		self.users = tmp_array
		self.user_photo_count += 1
		self.update()

	"""
	Builds eigenface algorithm based on directory of images given
	"""
	def build(self, directory):
		self.images = self.getImages(directory)
		self.users = np.zeros((1, self.IMAGE_DIM ** 2))
		self.eigenfaces = np.zeros((self.FACE_NUMBER, self.IMAGE_DIM ** 2))
		self.eigenfaces_norm = np.zeros((self.FACE_NUMBER, self.IMAGE_DIM ** 2))
		self.update()

	"""
	Returns the distances of a given input image
	"""
	def getDistances(self, input_image):
		if (input_image.shape[0] != input_image.shape[1]):
			read_image = input_image[20:input_image.shape[0]-20, 0:input_image.shape[1]]
		else:
			read_image = input_image

		weight_vectors = self.getWeightVectors(read_image.copy())

		fc_dist = sys.maxsize
		for i in range(len(self.users)):
			face_class = self.getWeightVectors(self.users[i,:].reshape(self.IMAGE_DIM, self.IMAGE_DIM))
			distance = np.linalg.norm(weight_vectors - face_class)

			if (distance < fc_dist):
				fc_dist = distance
		image_dif = read_image - self.avg_face
		face_space_var = np.zeros(((self.IMAGE_DIM, self.IMAGE_DIM)))
		eigenface = self.eigenfaces[0,:].reshape((self.IMAGE_DIM, self.IMAGE_DIM))
		normalized_face = self.normalize(eigenface)
		face_space_var = (weight_vectors[0] * normalized_face)
		for i in range(1,self.FACE_NUMBER):
			eigenface = self.eigenfaces[i,:].reshape((self.IMAGE_DIM, self.IMAGE_DIM))
			normalized_face = self.normalize(eigenface)
			face_space_var += (weight_vectors[i] * normalized_face)
		space_dif = image_dif - face_space_var
		fs_dist = np.linalg.norm(space_dif)
		return fc_dist, fs_dist

	"""
	Returns the distance of face class distance only
	"""
	def getFaceClassDist(self, input_image):
		if (input_image.shape[0] != input_image.shape[1]):
			read_image = input_image[20:input_image.shape[0]-20, 0:input_image.shape[1]]
		else:
			read_image = input_image

		weight_vectors = self.getWeightVectors(read_image.copy())

		fc_dist = sys.maxsize
		for i in range(len(self.users)):
			face_class = self.getWeightVectors(self.users[i,:].reshape(self.IMAGE_DIM, self.IMAGE_DIM))
			distance = np.linalg.norm(weight_vectors - face_class)

			if (distance < fc_dist):
				fc_dist = distance
		return fc_dist

	"""
	Returns the distance of the face space only
	"""
	def getFaceSpaceDist(self, input_image):
		if (input_image.shape[0] != input_image.shape[1]):
			read_image = input_image[20:input_image.shape[0]-20, 0:input_image.shape[1]]
		else:
			read_image = input_image
		weight_vectors = self.getWeightVectors(read_image.copy())
		image_dif = read_image - self.avg_face
		face_space_var = np.zeros(((self.IMAGE_DIM, self.IMAGE_DIM)))
		eigenface = self.eigenfaces[0,:].reshape((self.IMAGE_DIM, self.IMAGE_DIM))
		normalized_face = self.normalize(eigenface)
		face_space_var = (weight_vectors[0] * normalized_face)
		for i in range(1,self.FACE_NUMBER):
			eigenface = self.eigenfaces[i,:].reshape((self.IMAGE_DIM, self.IMAGE_DIM))
			normalized_face = self.normalize(eigenface)
			face_space_var += (weight_vectors[i] * normalized_face)
		space_dif = image_dif - face_space_var
		fs_dist = np.linalg.norm(space_dif)
		return fs_dist

	"""
	Loads images from a given directory, and returns them as an array
	"""
	def getImages(self, directory):
		# Initialize empty array for images
		image_array = []
		# Load each image from the directory
		for file in os.listdir(directory):
			# read the image as a matrix
			load_image = cv2.imread("{}{}".format(directory,file), 0)
			tmp_image = cv2.GaussianBlur(load_image, (5,5), cv2.BORDER_DEFAULT)
			if (tmp_image.shape[0] != tmp_image.shape[1]):
				image = tmp_image[20:tmp_image.shape[0] - 20, 0:self.IMAGE_DIM]
			else:
				image = tmp_image
			# Removes null cases
			if image is not None:
				image_array.append(image)
		return image_array

	"""
	Returns the weight vectors of a given image
	"""
	def getWeightVectors(self, input_image):
		# Initialize local weight vector
		weight_vectors = np.zeros((len(self.eigenfaces)))
		# Add entries into weight vector
		for i in range(len(self.eigenfaces)):
			# vector = self.normalize(self.eigenfaces[i,:]).flatten()
			vector = self.eigenfaces_norm[i,:]
			img_dif = (input_image - self.avg_face).flatten()
			w_vector = (np.transpose(vector)).dot(img_dif)
			weight_vectors[i] = w_vector
		return weight_vectors

	"""
	Takes the given matrix and mathematically normalizes it
	"""
	def normalize(self, matrix):
		distance = (1 / np.linalg.norm(matrix))
		temp_matrix = distance * matrix
		return temp_matrix

	"""
	Updates the eigenface algorithm based on user or base image changes
	"""
	def update(self):
		# convert all of the loaded images into a matrix for the Eigenface algorithm to use
		# Create the image matrix where the image data can be manipulated
		image_matrix = np.zeros((len(self.images) + len(self.users), self.IMAGE_DIM ** 2))
		# Add flattened image data into the image matrix
		im_index = 0
		for i in range(0, len(self.images)):
			image_matrix[im_index,:] = self.images[i].flatten()
			im_index += 1
		for i in range(0, len(self.users)):
			image_matrix[im_index,:] = self.users[i].flatten()
			im_index += 1
		# Calculate the mean image with the image matrix
		matrix_sum = np.zeros((self.IMAGE_DIM ** 2))
		for i in range(len(image_matrix)):
			matrix_sum += image_matrix[i,:]
		mean = matrix_sum * (1 / len(image_matrix))
		# Create the average face
		self.avg_face = mean.reshape((self.IMAGE_DIM, self.IMAGE_DIM))
		np.save("./npy/avg_face.npy", self.avg_face);
		# Subtract the mean from all of the original images
		mean_sub_images = np.zeros((len(image_matrix), self.IMAGE_DIM ** 2))
		for i in range(0, len(image_matrix)):
			mean_sub_images[i,:] = image_matrix[i,:] - mean
		# Create a matrix with equivalent eigenvectors with the covariance
		transpose_mean_img = np.transpose(mean_sub_images)
		square_matrix = mean_sub_images.dot(transpose_mean_img)
		# retrieve the vectors and the values
		eigenvalues, eigenvectors = np.linalg.eig(square_matrix)
		start_index = 2
		end_index = self.FACE_NUMBER + 2
		eigenface_index = 0
		for i in range(start_index, end_index):
			eigenface = (eigenvectors[0,i] * mean_sub_images[i,:])
			for j in range(1, len(mean_sub_images)):
				eigenface += (eigenvectors[j,i] * mean_sub_images[j,:])
			self.eigenfaces[eigenface_index,:] = eigenface
			self.eigenfaces_norm[eigenface_index,:] = self.normalize(eigenface)
			eigenface_index += 1
		np.save("./npy/images.npy", self.images);
		hash = SHA256.new()
		hash.update(self.current_user.encode('utf-8'))
		np.save("./npy/{}.npy".format(hash.hexdigest()), self.users)
		np.save("./npy/eigenfaces.npy", self.eigenfaces)
		np.save("./npy/eigenfaces_norm.npy", self.eigenfaces_norm)

if __name__ == '__main__':
	# Initialize class
	eigenface = Eigenface(178, "mac", 35)
	# eigenface.build("../eigenface-training-images/")
	# eigenface.build()
	load_image = cv2.imread("../users/6.jpg", 0)
	tmp_image = cv2.GaussianBlur(load_image, (5,5), cv2.BORDER_DEFAULT)
	eigenface.add_user_image(tmp_image)

	print("Test 1: Unknown Users")
	photo = cv2.imread("../eigenface-training-images/mdark-01.jpg",0)
	fc_dist, fs_dist = eigenface.getDistances(photo)
	print("This is fc dist: {:.2e}, this is fs dist: {:.2e}".format(fc_dist, fs_dist))
	photo = cv2.imread("../eigenface-training-images/mlight-01.jpg",0)
	fc_dist, fs_dist = eigenface.getDistances(photo)
	print("This is fc dist: {:.2e}, this is fs dist: {:.2e}".format(fc_dist, fs_dist))
	photo = cv2.imread("../eigenface-training-images/wdark-01.jpg",0)
	fc_dist, fs_dist = eigenface.getDistances(photo)
	print("This is fc dist: {:.2e}, this is fs dist: {:.2e}".format(fc_dist, fs_dist))
	photo = cv2.imread("../eigenface-training-images/wlight-01.jpg",0)
	fc_dist, fs_dist = eigenface.getDistances(photo)
	print("This is fc dist: {:.2e}, this is fs dist: {:.2e}".format(fc_dist, fs_dist))
	# print("Test 2: Known User")
	# photo = cv2.imread("../users/0.jpg",0)
	# fc_dist, fs_dist = eigenface.getDistances(photo)
	# print("This is fc dist: {:.2e}, this is fs dist: {:.2e}".format(fc_dist, fs_dist))
	# print("Test 3: No face")
	# photo = cv2.imread("test_photograph.jpg",0)
	# fc_dist, fs_dist = eigenface.getDistances(photo)
	# print("This is fc dist: {:.2e}, this is fs dist: {:.2e}".format(fc_dist, fs_dist))
	# photo = cv2.imread("test_photograph_2.jpg",0)
	# fc_dist, fs_dist = eigenface.getDistances(photo)
	# print("This is fc dist: {:.2e}, this is fs dist: {:.2e}".format(fc_dist, fs_dist))
	# photo = cv2.imread("test_photograph_3.jpg",0)
	# fc_dist, fs_dist = eigenface.getDistances(photo)
	# print("This is fc dist: {:.2e}, this is fs dist: {:.2e}".format(fc_dist, fs_dist))
	# print("Test 4: Gaussian Blur on last unknown user")
	# photo = cv2.imread("../eigenface-training-images/wlight-01.jpg",0)
	# dst = cv2.GaussianBlur(photo, (5,5), cv2.BORDER_DEFAULT)
	# fc_dist, fs_dist = eigenface.getDistances(dst)
	# print("This is fc dist: {:.2e}, this is fs dist: {:.2e}".format(fc_dist, fs_dist))
	# print("Test 5: Gaussian Blur of known user")
	# photo = cv2.imread("../users/0.jpg",0)
	# dst = cv2.GaussianBlur(photo, (5,5), cv2.BORDER_DEFAULT)
	# fc_dist, fs_dist = eigenface.getDistances(dst)
	# print("This is fc dist: {:.2e}, this is fs dist: {:.2e}".format(fc_dist, fs_dist))
	# print("Test 6: Gaussian Blur of no face")
	# photo = cv2.imread("test_photograph_3.jpg",0)
	# dst = cv2.GaussianBlur(photo, (5,5), cv2.BORDER_DEFAULT)
	# fc_dist, fs_dist = eigenface.getDistances(dst)
	# print("This is fc dist: {:.2e}, this is fs dist: {:.2e}".format(fc_dist, fs_dist))