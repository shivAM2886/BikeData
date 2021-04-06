import numpy as np
import pandas as pd
from tqdm import tqdm
from generate_grid_washington_dc import generate_grid
from collections import Counter

class square:

    def __init__(self, lon1, lat1, lon2, lat2, lon3, lat3, lon4, lat4):
        self.lon1 = lon1
        self.lat1 = lat1
        self.lon2 = lon2
        self.lat2 = lat2
        self.lon3 = lon3
        self.lat3 = lat3
        self.lon4 = lon4
        self.lat4 = lat4


    class line_function:
        def __init__(self, lon0, lat0, lon1, lat1):
            self.lon0 = lon0
            self.lat0 = lat0
            self.lon1 = lon1
            self.lat1 = lat1

        def calc_func_value(self, lon, lat):
            f1 = (self.lon1 - self.lon0) * (lat - self.lat0)
            f2 = (lon - self.lon0) * (self.lat1 - self.lat0)
            f = f1 - f2
            f[(f > 0)] = 1
            f[(f < 0)] = -1
            f[(f == 0)] = 0

            return f

        def calc_func_value_cent(self, lon, lat):
            f1 = (self.lon1 - self.lon0) * (lat - self.lat0)
            f2 = (lon - self.lon0) * (self.lat1 - self.lat0)
            f = f1 - f2
            if f > 0:
                f = 1
            elif f < 0:
                f = -1
            elif f == 0:
                f = 0

            return f


    def check_inside(self, lon, lat):

        inside_val = np.zeros(len(lon))

        lf12 = self.line_function(self.lon1, self.lat1, self.lon2, self.lat2)
        lf23 = self.line_function(self.lon2, self.lat2, self.lon3, self.lat3)
        lf34 = self.line_function(self.lon3, self.lat3, self.lon4, self.lat4)
        lf41 = self.line_function(self.lon4, self.lat4, self.lon1, self.lat1)

        lf_val12 = lf12.calc_func_value(lon, lat)
        lf_val23 = lf23.calc_func_value(lon, lat)
        lf_val34 = lf34.calc_func_value(lon, lat)
        lf_val41 = lf41.calc_func_value(lon, lat)


        l_val = lf_val12 *lf_val23 *lf_val34 *lf_val41
        #print("l_val shape", l_val.shape)

        lonc = (self.lon1 + self.lon2 + self.lon3 + self.lon4)/4
        latc = (self.lat1 + self.lat2 + self.lat3 + self.lat4)/4

        lf_val12c = lf12.calc_func_value_cent(lonc, latc)
        lf_val23c = lf23.calc_func_value_cent(lonc, latc)
        lf_val34c = lf34.calc_func_value_cent(lonc, latc)
        lf_val41c = lf41.calc_func_value_cent(lonc, latc)



        cond1 = ((lf_val12 * lf_val12c) > 0)
        cond2 = ((lf_val23 * lf_val23c) > 0)
        cond3 = ((lf_val34 * lf_val34c) > 0)
        cond4 = ((lf_val41 * lf_val41c) > 0)

        cond = cond1*cond2*cond3*cond4
        #print(cond.shape)
        #print(Counter(cond))

        #print(lf_val12c, lf_val23c, lf_val34c, lf_val41c)

        inside_val[cond] += 1
        return inside_val


class add_square_class:

    def __init__(self, df_square):
        self.df_square = df_square


    def run_main(self):
        dfs = self.df_square

        dfs['square_class'] = -99
        for i in tqdm(range(len(dfs))):

            lon1 = dfs['lon_cor1'][i]
            lon2 = dfs['lon_cor2'][i]
            lon3 = dfs['lon_cor3'][i]
            lon4 = dfs['lon_cor4'][i]

            lat1 = dfs['lat_cor1'][i]
            lat2 = dfs['lat_cor2'][i]
            lat3 = dfs['lat_cor3'][i]
            lat4 = dfs['lat_cor4'][i]

            dfs.loc[i, 'square_class'] = square(lon1, lat1, lon2, lat2, lon3, lat3, lon4, lat4)

        return dfs

class assign_trips_square:

    def __init__(self, df_trips, dfs):
        self.df_trips = df_trips
        self.dfs = dfs


    def run_main(self):
        dfs = self.dfs
        dfs['pickups'] = 0.0
        dfs['dropoffs'] = 0.0
        for i in range(len(dfs)):
            temp_class = dfs['square_class'][i]

            lon_trip1 = self.df_trips['start_lon'].values
            lat_trip1 = self.df_trips['start_lat'].values

            inside_val1 = temp_class.check_inside(lon_trip1, lat_trip1)

            lon_trip2 = self.df_trips['end_lon'].values
            lat_trip2 = self.df_trips['end_lat'].values

            inside_val2 = temp_class.check_inside(lon_trip2, lat_trip2)


            print(i, "pickups = " + str(np.sum(inside_val1)), "dropoffs = " + str(np.sum(inside_val2)))

            dfs.loc[i, 'pickups'] = dfs.loc[i, 'pickups'] + np.sum(inside_val1)
            dfs.loc[i, 'dropoffs'] = dfs.loc[i, 'dropoffs'] + np.sum(inside_val2)



        return dfs

