import numpy as np
import pandas as pd

class form_squares:

    def __init__(self, df_result):
        self.df_result = df_result

    def run_square(self):
        lon_dict = {}
        lat_dict = {}
        x_max = np.max(self.df_result['line12'])
        y_max = np.max(self.df_result['line14'])
        print("x_max", x_max, "y_max", y_max)
        for i in range(len(self.df_result)):
            x = self.df_result['line12'][i]
            y = self.df_result['line14'][i]
            lon_dict[(x, y)] = self.df_result['lon'][i]
            lat_dict[(x, y)] = self.df_result['lat'][i]

        cor1_lon_series = []
        cor1_lat_series = []

        cor2_lon_series = []
        cor2_lat_series = []

        cor3_lon_series = []
        cor3_lat_series = []

        cor4_lon_series = []
        cor4_lat_series = []

        square_id_series = []
        x_series = []
        y_series = []
        count = 0
        for i in range(y_max):

            for j in range(x_max):
                square_id_series.append(str(j) + str(i))

                cor1_lon_series.append(lon_dict[j, i])
                cor1_lat_series.append(lat_dict[j, i])

                cor2_lon_series.append(lon_dict[j+1, i])
                cor2_lat_series.append(lat_dict[j+1, i])

                cor3_lon_series.append(lon_dict[j+1, i+1])
                cor3_lat_series.append(lat_dict[j+1, i+1])

                cor4_lon_series.append(lon_dict[j, i+1])
                cor4_lat_series.append(lat_dict[j, i+1])

                count += 1
                x_series.append(j)
                y_series.append(i)

        print("total squares percentage ", count/len(self.df_result))


        data = {'square_id': square_id_series, 'x':x_series, 'y':y_series,
                'lon_cor1': cor1_lon_series, 'lat_cor1': cor1_lat_series,
                'lon_cor2': cor2_lon_series, 'lat_cor2': cor2_lat_series,
                'lon_cor3': cor3_lon_series, 'lat_cor3': cor3_lat_series,
                'lon_cor4': cor4_lon_series, 'lat_cor4': cor4_lat_series}

        df_square = pd.DataFrame(data = data)
        return x_max, y_max, df_square