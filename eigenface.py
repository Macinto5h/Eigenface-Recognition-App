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

"""
Eigenface class that contains all of its functions, fields, etc.
"""
class Eigenface:

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
				image = tmp_image[20:tmp_image.shape[0] - 20, 0:self.IMAGE_DIM[1]]
			else:
				image = tmp_image
			# Removes null cases
			if image is not None:
				image_array.append(image)
		return image_array

	"""
	Initializer
	"""
	def __init__(self, test_dir, user_dir, eigenface_dir, avg_dir, image_dim):
		# "Constants"
		self.FACE_NUMBER = 35
		self.TEST_DIR = test_dir
		self.USER_DIR = user_dir
		self.EIGENFACE_DIR = eigenface_dir
		self.AVG_DIR = avg_dir
		self.IMAGE_DIM = image_dim
		self.image_num = 0
		self.avg_brightness = 0

		# Fields
		self.images = self.getImages(self.TEST_DIR)
		self.users = self.getImages(self.USER_DIR)
		self.avg_face = self.getImages(self.AVG_DIR)[0]
		self.eigenfaces = np.zeros((self.FACE_NUMBER, self.IMAGE_DIM[1] ** 2))
		self.eigenfaces_norm = np.zeros((self.FACE_NUMBER, self.IMAGE_DIM[1] ** 2))

	"""
	Builds/Rebuilds eigenfaces when called
	"""
	def build(self):
		# convert all of the loaded images into a matrix for the Eigenface algorithm to use
		# Create the image matrix where the image data can be manipulated
		image_matrix = np.zeros((len(self.images) + len(self.users), self.IMAGE_DIM[1] ** 2))
		# Add flattened image data into the image matrix
		im_index = 0
		for i in range(0, len(self.images)):
			image_matrix[im_index,:] = self.images[i].flatten()
			im_index += 1
		for i in range(0, len(self.users)):
			image_matrix[im_index,:] = self.users[i].flatten()
			im_index += 1
		# Calculate the mean image with the image matrix
		matrix_sum = np.zeros((self.IMAGE_DIM[1] ** 2))
		# matrix_sum = image_matrix[0,:]
		for i in range(len(image_matrix)):
			matrix_sum += image_matrix[i,:]
		mean = matrix_sum * (1 / len(image_matrix))
		# Create the average face
		self.avg_face = mean.reshape((self.IMAGE_DIM[1], self.IMAGE_DIM[1]))
		cv2.imwrite("{}avg_face.jpg".format(self.AVG_DIR), self.avg_face)
		# Subtract the mean from all of the original images
		mean_sub_images = np.zeros((len(image_matrix), self.IMAGE_DIM[1] ** 2))
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
		for i in range(len(self.eigenfaces)):
			eigenface = self.eigenfaces[i,:].reshape((self.IMAGE_DIM[1],self.IMAGE_DIM[1]))
			cv2.imwrite('{}{}.jpg'.format(self.EIGENFACE_DIR, i), eigenface)
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
			face_class = self.getWeightVectors(self.users[i])
			distance = np.linalg.norm(weight_vectors - face_class)

			if (distance < fc_dist):
				fc_dist = distance
		image_dif = read_image - self.avg_face
		# cv2.imwrite("subtract_avg_face_{}.jpg".format(self.image_num), image_dif)
		face_space_var = np.zeros(((self.IMAGE_DIM[1], self.IMAGE_DIM[1])))
		eigenface = self.eigenfaces[0,:].reshape((self.IMAGE_DIM[1], self.IMAGE_DIM[1]))
		normalized_face = self.normalize(eigenface)
		face_space_var = (weight_vectors[0] * normalized_face)
		for i in range(1,self.FACE_NUMBER):
			eigenface = self.eigenfaces[i,:].reshape((self.IMAGE_DIM[1], self.IMAGE_DIM[1]))
			normalized_face = self.normalize(eigenface)
			face_space_var += (weight_vectors[i] * normalized_face)
		# cv2.imwrite('face_space_proj_{}.jpg'.format(self.image_num), face_space_var)
		space_dif = image_dif - face_space_var
		# cv2.imwrite('face_space_dif_{}.jpg'.format(self.image_num), space_dif)
		fs_dist = np.linalg.norm(space_dif)
		self.image_num += 1
		return fc_dist, fs_dist

	def getFaceSpaceDistance(self, input_image):
		weight_vectors = self.getWeightVectors(input_image)
		image_dif = input_image - self.avg_face
		face_space_var = np.zeros(((self.IMAGE_DIM[1], self.IMAGE_DIM[1])))
		eigenface = self.eigenfaces_norm[0,:].reshape((self.IMAGE_DIM[1], self.IMAGE_DIM[1]))
		# normalized_face = self.normalize(eigenface)
		face_space_var = (weight_vectors[0] * eigenface)
		for i in range(1,self.FACE_NUMBER):
			eigenface = self.eigenfaces_norm[i,:].reshape((self.IMAGE_DIM[1], self.IMAGE_DIM[1]))
			# normalized_face = self.normalize(eigenface)
			face_space_var += (weight_vectors[i] * eigenface)
		space_dif = image_dif - face_space_var
		fs_dist = np.linalg.norm(space_dif)
		return fs_dist

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

	def normalize(self, matrix):
		distance = (1 / np.linalg.norm(matrix))
		temp_matrix = distance * matrix
		return temp_matrix
if __name__ == '__main__':
	# Initialize class
	eigenface = Eigenface("../eigenface-training-images/", "../users/", "./eigenfaces/", "./avg_face/", (218, 178))
	eigenface.build()
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
	print("Test 3: No face")
	photo = cv2.imread("test_photograph.jpg",0)
	fc_dist, fs_dist = eigenface.getDistances(photo)
	print("This is fc dist: {:.2e}, this is fs dist: {:.2e}".format(fc_dist, fs_dist))
	photo = cv2.imread("test_photograph_2.jpg",0)
	fc_dist, fs_dist = eigenface.getDistances(photo)
	print("This is fc dist: {:.2e}, this is fs dist: {:.2e}".format(fc_dist, fs_dist))
	photo = cv2.imread("test_photograph_3.jpg",0)
	fc_dist, fs_dist = eigenface.getDistances(photo)
	print("This is fc dist: {:.2e}, this is fs dist: {:.2e}".format(fc_dist, fs_dist))
	print("Test 4: Gaussian Blur on last unknown user")
	photo = cv2.imread("../eigenface-training-images/wlight-01.jpg",0)
	dst = cv2.GaussianBlur(photo, (5,5), cv2.BORDER_DEFAULT)
	fc_dist, fs_dist = eigenface.getDistances(dst)
	print("This is fc dist: {:.2e}, this is fs dist: {:.2e}".format(fc_dist, fs_dist))
	# print("Test 5: Gaussian Blur of known user")
	# photo = cv2.imread("../users/0.jpg",0)
	# dst = cv2.GaussianBlur(photo, (5,5), cv2.BORDER_DEFAULT)
	# fc_dist, fs_dist = eigenface.getDistances(dst)
	# print("This is fc dist: {:.2e}, this is fs dist: {:.2e}".format(fc_dist, fs_dist))
	print("Test 6: Gaussian Blur of no face")
	photo = cv2.imread("test_photograph_3.jpg",0)
	dst = cv2.GaussianBlur(photo, (5,5), cv2.BORDER_DEFAULT)
	fc_dist, fs_dist = eigenface.getDistances(dst)
	print("This is fc dist: {:.2e}, this is fs dist: {:.2e}".format(fc_dist, fs_dist))