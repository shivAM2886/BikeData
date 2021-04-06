import numpy as np
import pandas as pd
from tqdm import tqdm
from generate_grid_washington_dc import generate_grid
from collections import Counter

class hhi:

    def __init__(self, dfs, neighbors, x_max, y_max):
        self.dfs = dfs
        self.neighbors = neighbors
        self.x_max = x_max
        self.y_max = y_max

    def generate_neighbor_ids(self, x, y):
        x0 = max(x - self.neighbors, 0)
        x1 = min(x + self.neighbors, self.x_max)

        y0 = max(y - self.neighbors, 0)
        y1 = min(y + self.neighbors, self.y_max)

        neighbor_square_ids = []
        for x in range(x0, x1):
            for y in range(y0, y1):
                str1 = str(x) + str(y)
                neighbor_square_ids.append(str1)

        return neighbor_square_ids

    def calc_hhi_val(self, arr):
        arr = np.asarray(arr)
        if len(arr) > 0:
            sum1 = np.sum(arr)
            if sum1 > 0:
                arr1 = (100.0 * arr) / sum1
                arr2 = arr1 * arr1
                hhi_val = np.sum(arr2)
                return hhi_val
        else:
            return 0

    def run_main(self):
        dict_pickups = dict(zip(self.dfs['square_id'].values, self.dfs['pickups'].values))
        dict_dropoffs = dict(zip(self.dfs['square_id'].values, self.dfs['dropoffs'].values))

        df1 = self.dfs
        df1 = df1[(df1['pickups'] > 0) & (df1['dropoffs'] > 0)]
        df1 = df1.reset_index(drop = True)
        df1['phhi'+'_'+str(self.neighbors)] = 0.0
        df1['dhhi'+"_"+str(self.neighbors)] = 0.0
        df1['hhi_ratio'+"_" + str(self.neighbors)] = 0.0
        for i in range(len(df1)):
            x = df1['x'][i]
            y = df1['y'][i]
            neighbor_square_ids = self.generate_neighbor_ids(x, y)
            pickup_arr = [dict_pickups[id1] for id1 in neighbor_square_ids]
            dropoff_arr = [dict_dropoffs[id1] for id1 in neighbor_square_ids]


            phhi = self.calc_hhi_val(pickup_arr)
            dhhi = self.calc_hhi_val(dropoff_arr)

            hhi_ratio = phhi/dhhi

            df1.loc[i, 'phhi' + '_' + str(self.neighbors)] = phhi
            df1.loc[i, 'dhhi' + "_" + str(self.neighbors)] = dhhi
            df1.loc[i, 'hhi_ratio' + "_" + str(self.neighbors)] = hhi_ratio

        return df1






