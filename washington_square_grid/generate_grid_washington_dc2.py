import pandas as pd
import numpy as np
from form_squares import form_squares


class generate_grid:

	def __init__(self, grid_size):

		# in meters
		self.grid_size = grid_size

		self.grid_modified = (400.0/9)*self.grid_size

		self.lat_corner1 = 38.995418
		self.lon_corner1 = -77.041078

		self.lat_corner2 = 38.892845
		self.lon_corner2 = -76.909496

		self.lat_corner3 = 38.828800
		self.lon_corner3 = -76.9992657

		self.lat_corner4 = 38.934471
		self.lon_corner4 = -77.119045

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


	def run_main(self):

		t_lon12, t_lat12, s12 = self.compute_parameter(self.lon_corner1, self.lat_corner1, self.lon_corner2, self.lat_corner2)

		t_lon14, t_lat14, s14 = self.compute_parameter(self.lon_corner1, self.lat_corner1, self.lon_corner4, self.lat_corner4)

		lon0 = self.lon_corner1
		lat0 = self.lat_corner1

		lon1 = self.lon_corner2
		lat1 = self.lat_corner2


		lon_t_series = []
		lat_t_series = []
		line12_id = []
		line14_id = []

		for i in range(s14+5):

			for j in range(s12):
				lat_t = (1-(j*t_lon12))*lat0 + (j*t_lon12)*lat1
				lon_t = (1-(j*t_lat12))*lon0 + (j*t_lat12)*lon1

				lat_t_series.append(lat_t)
				lon_t_series.append(lon_t)
				line12_id.append(j)
				line14_id.append(i)



			lon0 = (1- (i*t_lon14))*self.lon_corner1 + (i*t_lon14)*self.lon_corner4
			lat0 = (1- (i*t_lat14))*self.lat_corner1 + (i*t_lat14)*self.lat_corner4

			lon1 = (1- (i*t_lon14))*self.lon_corner2 + (i*t_lon14)*self.lon_corner3
			lat1 = (1- (i*t_lat14))*self.lat_corner2 + (i*t_lat14)*self.lat_corner3



		data = {'line12':line12_id, 'line14':line14_id, 'lon':lon_t_series, 'lat':lat_t_series}
		df_result = pd.DataFrame(data=data)

		x_max, y_max, df_square = form_squares(df_result).run_square()

		return x_max, y_max, df_square





		

