import pandas as pd

from boundary_type_class import square_boundary, circular_boundary, nearest_neighbor
from hhi_class import hhi

class hhi_main1:

    # top_intersections : TOP intersections for which calculation
    #                     is to be done (2000).

    def __init__(self, top_intersections, boundary_type, additional_params):
        self.top_intersections = top_intersections
        self.boundary_type = boundary_type

        # additional params is radius for circular boundary,
        # side for square boundary and nearest neighbors for nearest neighbor.

        self.additional_params = additional_params

    def load_dataset(self):
        df = pd.read_csv("pickup_dropoff_intersections.csv")
        df = df.sort_values(by=['all_pickups'], ascending=False)
        df = df.reset_index(drop=True)
        df = df.iloc[0: self.top_intersections]
        return df

    def main(self):

        df = self.load_dataset()
        df['hhi_ratio'] = -99.0

        if self.boundary_type == "square":
            side = self.additional_params
            temp_class = square_boundary(side)

        elif self.boundary_type == "circle":
            radius = self.additional_params
            temp_class = circular_boundary(radius)

        elif self.boundary_type == "nearest_neighbor":
            total_neighbor_points = self.additional_params
            temp_class = nearest_neighbor(total_neighbor_points)

        else:
            raise Exception("Enter correct boundary type !")

        for i in range(len(df)):
            lon_ref = df['LONGITUDE'][i]
            lat_ref = df['LATITUDE'][i]

            lon_loc = df['LONGITUDE'].values
            lat_loc = df['LATITUDE'].values

            present_mask = temp_class.inside_points(lon_loc, lat_loc, lon_ref, lat_ref)

            pickup_arr = df['all_pickups'].values[present_mask]
            dropoff_arr = df['all_dropoffs'].values[present_mask]

            hhi_ratio = hhi(pickup_arr, dropoff_arr).calc_hhi_ratio()
            df.loc[i, 'hhi_ratio'] = hhi_ratio
            df.loc[i, 'total_intersections'] = len(pickup_arr)

        return df
