import pandas as pd
import numpy as np

class generate_grid:

	def __init__(self, grid_size):

		# in meters
		self.grid_size 	   = grid_size

		self.lon_boundary1 = -77.13
		self.lon_boundary2 = -76.90
		self.lat_boundary1 =  39.00
		self.lat_boundary2 =  38.85

		self.theta = (self.grid_size)/(6371.01*1000)	# in radians
		self.value = np.cos(self.theta)


	def get_lon3(self, lon1, lat1):

		lat1 = np.radians(np.float64(lat1))
		lon1 = np.radians(np.float64(lon1))

		q1 = self.value
		q2 = np.sin(lat1)*np.sin(lat1)
		q3 = np.cos(lat1)*np.cos(lat1)

		Q = (q1 - q2)/(q3)

		lon3 = lon1 + np.arccos(Q)

		lon3 = np.degrees(lon3)

		return lon3 

	def get_lat3(self, lon1, lat1):

		lat1 = np.radians(np.float64(lat1))
		lon1 = np.radians(np.float64(lon1))

		lat3 = lat1 - np.arccos(self.value)
		lat3 = np.degrees(lat3)

		return lat3

	def modify_datastruct(self, square_array):
		lon1_series = []
		lat1_series = []

		lon3_series = []
		lat3_series = []

		for i in range(len(square_array)):
			temp_square = square_array[i]
			lon1_series.append(temp_square[0][0])
			lat1_series.append(temp_square[0][1])

			lon3_series.append(temp_square[1][0])
			lat3_series.append(temp_square[1][1])

		data = {'grid_id': [i for i in range(len(square_array))],
		'lon1': lon1_series, 'lat1': lat1_series, 'lon3': lon3_series, 
		'lat3': lat3_series}

		df_result = pd.DataFrame(data = data)

		return df_result


	def run_main(self, start_lon, start_lat):
		square_array = []


		lon1 = start_lon
		lat1 = start_lat

		while lat1 > self.lat_boundary2:
			lat3 = self.get_lat3 (lon1, lat1)

			while lon1 < self.lon_boundary2:
				lon3 = self.get_lon3(lon1, lat1)
				temp_square_coordinates = [(lon1, lat1), (lon3, lat3)]
				square_array.append(temp_square_coordinates)
				lon1 = lon3

			lon1 = start_lon
			lat1 = lat3

		df_result = self.modify_datastruct(square_array)

		return df_results





		

