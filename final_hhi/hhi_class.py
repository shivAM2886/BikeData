import numpy as np

class hhi:

    def __init__(self, pickup_arr, dropoff_arr):
        self.pickup_arr = pickup_arr
        self.dropoff_arr = dropoff_arr

    def calc_hhi(self, arr):
        sum1 = np.sum(arr)
        arr1 = (100.0 * arr) / sum1
        arr2 = arr1 * arr1
        hhi = np.sum(arr2)
        return hhi

    def calc_hhi_ratio(self):
        phhi = self.calc_hhi(self.pickup_arr)
        dhhi = self.calc_hhi(self.dropoff_arr)

        if dhhi == 0:
            hhi_ratio = -10
        else:
            hhi_ratio = phhi / dhhi

        return hhi_ratio