import pandas as pd
import numpy as np


class generate_grid:

	def __init__(self, grid_size):

		# in meters
		self.grid_size = grid_size

		self.grid_modified = (400.0/9)*self.grid_size

		self.lat_corner1 = 38.995494
		self.lon_corner1 = -77.041041

		self.lat_corner2 = 38.89287
		self.lon_corner2 = -76.90939

		self.lat_corner3 = 38.841817
		self.lon_corner3 = -76.983018

		self.lat_corner4 = 38.936229
		self.lon_corner4 = -77.113567

	def compute_parameter(self, lon0, lat0, lon1, lat1):

		lon_loc = np.radians(np.float64(lon0))
		lat_loc = np.radians(np.float64(lat0))

		lon_ref1 = np.radians(np.float64(lon1))
		lat_ref1 = np.radians(np.float64(lat1))

		value = np.sin(lat0) * np.sin(lat1) + (np.cos(lat0) * np.cos(lat1) * np.cos(lon0 - lon1))

		dist = 6371.01 * 1000 * np.arccos(value)


		steps = int(dist/self.grid_modified)
		t = self.grid_modified/dist
		t_lon = t
		t_lat = t

		return t_lon, t_lat, steps


	def check_lat_side(self, lon, lat):
		# must be positive
		lat1 = self.lat_corner4
		lat2 = self.lat_corner3

		lon1 = self.lon_corner4
		lon2 = self.lat_corner3

		m = (lat1 - lat2)/(lon1 - lon2)
		value = (lat - lat1) + m*(lon - lon1)
		return value

	def check_lon_side(self, lon, lat):
		# must be positive
		lat1 = self.lat_corner2
		lat2 = self.lat_corner3

		lon1 = self.lon_corner2
		lon2 = self.lon_corner3

		m = (lat1 - lat2)/(lon1 - lon2)
		value = (lat - lat1) + m * (lon - lon1)
		return value


	def run_main(self):

		t_lon12, t_lat12, s12 = self.compute_parameter(self.lon_corner1, self.lat_corner1, self.lon_corner2, self.lat_corner2)

		t_lon14, t_lat14, s14 = self.compute_parameter(self.lon_corner1, self.lat_corner1, self.lon_corner4, self.lat_corner4)

		lon0 = self.lon_corner1
		lat0 = self.lat_corner1

		lon1 = self.lon_corner2
		lat1 = self.lat_corner2

		lon_t = lon0
		lat_t = lat0

		lon_t_series = [lon0]
		lat_t_series = [lat0]


		for i in range(1, s14):

			print(lon0, lat0, lon1, lat1)
			for j in range(1, s12):
				lat_t = (1-(j*t_lon12))*lat0 + (j*t_lon12)*lat1
				lon_t = (1-(j*t_lat12))*lon0 + (j*t_lat12)*lon1

				lat_t_series.append(lat_t)
				lon_t_series.append(lon_t)



			lon0 = (1- (i*t_lon14))*self.lon_corner1 + (i*t_lon14)*self.lon_corner4
			lat0 = (1- (i*t_lat14))*self.lat_corner1 + (i*t_lat14)*self.lat_corner4

			lon1 = (1- (i*t_lon14))*self.lon_corner2 + (i*t_lon14)*self.lon_corner3
			lat1 = (1- (i*t_lat14))*self.lat_corner2 + (i*t_lat14)*self.lat_corner3

			print(lon0, lat0, lon1, lat1)
			print("---------")




		data = {'lon':lon_t_series, 'lat':lat_t_series}
		df_result = pd.DataFrame(data=data)


		return df_result





		

