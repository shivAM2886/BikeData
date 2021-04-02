import numpy as np
from scipy.stats import rankdata


class square_boundary:
    
    # (lon_c, lat_c) > square center lon and lat
    # side >> side of the square (in meters)

    def __init__(self, side):
        self.side = side
        self.theta = (0.5 * self.side) / (6371.01 * 1000)  # in radians
        self.value = np.cos(self.theta)

    def get_boundary_latitudes(self, lon_ref, lat_ref):
        lat_ref1 = np.radians(np.float64(lat_ref))
        lon_ref1 = np.radians(np.float64(lon_ref))

        lat1 = lat_ref1 - np.arccos(self.value)
        lat2 = lat_ref1 + np.arccos(self.value)

        return lat1, lat2

    def get_boundary_longitudes(self, lon_ref, lat_ref):
        lat_ref1 = np.radians(np.float64(lat_ref))
        lon_ref1 = np.radians(np.float64(lon_ref))

        k1 = np.sin(lat_ref1) * np.sin(lat_ref1)
        k2 = np.cos(lat_ref1) * np.cos(lat_ref1)

        value2 = (self.value - k1) / k2

        lon1 = lon_ref1 - np.arccos(value2)
        lon2 = lon_ref1 + np.arccos(value2)

        return lon1, lon2

    def inside_points(self, lon_loc, lat_loc, lon_ref, lat_ref):
        lat_loc = np.radians(np.float64(lat_loc))
        lon_loc = np.radians(np.float64(lon_loc))

        lat1, lat2 = self.get_boundary_latitudes(lon_ref, lat_ref)
        lon1, lon2 = self.get_boundary_longitudes(lon_ref, lat_ref)

        present = 0

        # Note on the boundary is counted as present inside.
        lat_true = ((lat2 >= lat_loc) & (lat_loc >= lat1))
        lon_true = ((lon2 >= lon_loc) & (lon_loc >= lon1))

        present = lat_true * lon_true

        return present


class circular_boundary:

    def __init__(self, radius):
        self.radius = radius

    def calc_distance(self, lon_loc, lat_loc, lon_ref, lat_ref):
        # (lon_ref, lat_ref) : Reference Intersection Location
        # (lon_loc, lat_loc) : Array containing location of all the intersections.

        lon_loc = np.radians(np.float64(lon_loc))
        lat_loc = np.radians(np.float64(lat_loc))

        lon_ref1 = np.radians(np.float64(lon_ref))
        lat_ref1 = np.radians(np.float64(lat_ref))

        value = np.sin(lat_loc) * np.sin(lat_ref1) + (np.cos(lat_loc) * np.cos(lat_ref1) * np.cos(lon_loc - lon_ref1))

        value[value > 1] = 1
        dist = 6371.01 * 1000 * np.arccos(value)

        return dist

    def inside_points(self, lon_loc, lat_loc, lon_ref, lat_ref):
        dist = self.calc_distance(lon_loc, lat_loc, lon_ref, lat_ref)
        present = (dist <= self.radius)

        return present


class nearest_neighbor:
    def __init__(self, total_neighbor_points):
        self.total_neighbor_points = total_neighbor_points

    def calc_distance(self, lon_loc, lat_loc, lon_ref, lat_ref):

        # (lon_ref, lat_ref) : Reference Intersection Location
        # (lon_loc, lat_loc) : Array containing location of all the intersections.

        lon_loc = np.radians(np.float64(lon_loc))
        lat_loc = np.radians(np.float64(lat_loc))

        lon_ref1 = np.radians(np.float64(lon_ref))
        lat_ref1 = np.radians(np.float64(lat_ref))

        value = np.sin(lat_loc) * np.sin(lat_ref1) + (np.cos(lat_loc) * np.cos(lat_ref1) * np.cos(lon_loc - lon_ref1))

        value[value > 1] = 1
        dist = 6371.01 * 1000 * np.arccos(value)

        return dist

    def inside_points(self, lon_loc, lat_loc, lon_ref, lat_ref):
        dist = self.calc_distance(lon_loc, lat_loc, lon_ref, lat_ref)
        dist_rank = rankdata(dist)
        present = (dist_rank <= self.total_neighbor_points + 1)
        return present
