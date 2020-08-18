import pandas as pd
from pathlib import Path
import pandas as pd
import sqlite3
import numpy as np
import os
import time
from tqdm import tqdm
from datetime import datetime, timedelta
import torch

# function to read .db files as data-frame

def func_load_dataset(file_path, table_name = "bikedata_tb"):
    con = sqlite3.connect(str(file_path))
    df = pd.read_sql_query("select bike_id, lon, lat, my_time_stamp from "+table_name, con)
    con.close()
    return df


# convert  DD/MM/YY HH/MM/SS to YY/MM/DD HH/MM/SS
def manipulate_datetime(datetime1):
    x = datetime1.split(" ")
    y = x[0].split("/")
    z = y[2]+"/"+y[1] + "/"+ y[0]
    z = z + " " + x[1]
    return z


# function to attribute intersection to a point based on inputted longitude and latitude values.

def func_attribute_intersection(lon_loc, lon_int, lat_loc, lat_int, threshold_radius=200):

    # lon_loc, lat_loc >>
    # (1, size1) matrix. Contains longitude/latitude of the points for which
    # the nearest intersection is to be calculated.

    # dim =0 is 1 in above size because time-step is processed at a time due to
    # GPU memory constraints.

    # lon_int, lat_int >>
    # (8437, ) Contains longitudes/latitudes of the unique intersections in
    # washington dc.

    # threshold_radius >> default value 200 meters.
    # A point withing 200 meters of an unique intersection is attributed that intersection.

    torch.cuda.empty_cache()

    t1 = lon_loc.shape[0]
    b1 = lon_loc.shape[1]

    intersection_shape = len(lon_int)

    if len(lon_loc) == 1:
        lon_loc = torch.from_numpy(np.asarray(np.radians(np.float64(lon_loc)))).cuda()
        lat_loc = torch.from_numpy(np.asarray(np.radians(np.float64(lat_loc)))).cuda()

    else:
        lon_loc = torch.from_numpy(np.radians(np.float64(lon_loc))).cuda()
        lat_loc = torch.from_numpy(np.radians(np.float64(lat_loc))).cuda()

    lon_int = torch.from_numpy(np.radians(np.float64(lon_int))).cuda()
    lat_int = torch.from_numpy(np.radians(np.float64(lat_int))).cuda()

    lat_loc = lat_loc.view(([1, t1, b1]))
    lon_loc = lon_loc.view(([1, t1, b1]))

    # print("lon_loc shape 3d ", lon_loc.shape)
    # shape (1, 1, size1)

    lon_int = lon_int.view(([intersection_shape, 1, 1]))
    lat_int = lat_int.view(([intersection_shape, 1, 1]))

    # print("lon int shape after transformation", lon_int.shape)
    # shape (8437, 1, 1)

    value = torch.sin(lat_loc) * torch.sin(lat_int) + (
                torch.cos(lat_loc) * torch.cos(lat_int) * torch.cos(lon_loc - lon_int))

    # print("value shape", value.shape)
    # shape (8437, 1, size1)

    # visualize the value matrix as a 3-dimensional matrix with depth = 8437 (dim = 0), row_size = 1
    # and column_size = size1

    # each column contains the values calculated for one specific point with 8437 intersection
    # locations along the dim 0.

    del lat_loc, lon_loc, lon_int, lat_int
    torch.cuda.empty_cache()

    # some values may be slightly greater than 1...due to approximations.
    # convert these values to 1

    value[value > 1] = 1

    # choose the index, distance values along the dim 0 where distance is minimum.
    # note that the "unique_intersection_id" is 1+indices along the dim 0.

    pool = torch.min(6371.01 * 1000 * torch.acos(value), dim=0)

    del value
    torch.cuda.empty_cache()

    # minimum distance.
    min_dist_mat = (pool.values.cpu()).numpy()

    # unique_intersection_id
    intersection_mat = (pool.indices.cpu()).numpy() + 1

    # unique_intersection_id values for the points when the bike is not in the system
    # and when the bike is not within 200 m of any intersection in dc.

    # please note that when the bike is not in the system, it has default values of
    # lon and lat equal to (-135, 90)

    intersection_mat[min_dist_mat >= 5670000] = -10
    intersection_mat[(min_dist_mat > threshold_radius) & (min_dist_mat < 5670000)] = -1800

    del pool
    torch.cuda.empty_cache()

    # print("min_dist_mat shape", min_dist_mat.shape)   shape (1, size1)
    # print("intersection_mat shape", intersection_mat.shape)  (1, size1)

    # print('-----')
    return min_dist_mat, intersection_mat


# data-frame consisting of "unique_intersection_id" (1 to 8437), longitude and latitude of
# all the intersections in washington dc.

df_intersection = pd.read_csv("C:/project_files/dc_intersection/intersection_points_unique.csv")

lat_int = df_intersection['LATITUDE'].values
lon_int = df_intersection['LONGITUDE'].values
street_val_array = df_intersection['unique_intersection_id'].values


company_array = ['jumpbikes', "bird", "lime"]

# note that one week of data is processed at one time (7 days) for one company.
# (hence the week_array)
# Increase or decrease this 7 day period based on GPU memory constraints, and
# density of raw datafiles.
# This is according to 2GB GPU memory.

week_folder_array = ["week1", "week2", "week3"]

for company_name in company_array:

    for dataset_folder in week_folder_array:
        file_number = 0

        # dir_id >> location where the raw files are located.
        # "organize the raw db data files" as company/week/file_name

        # dir_id2 >> attribute information of one week for one bike company is written
        # into one single CSV file. dir_id2 is the location where single CSV file
        # is stored.

        # note that one week of raw data files contains around ~ 28 .db files, which are
        # combined along with the intersection information and written into one single CSV
        # file.

        dir_id = "C:/project_files/data_files/0_db_files/"+ company_name + "/" + dataset_folder + "/"
        dir_id2 = "C:/project_files/data_files/11_attribute_matrix/"+company_name+"/"

        # sort raw data files order based on date and time modified.
        file_path_array = sorted(Path(dir_id).iterdir(), key=os.path.getmtime)

        out_file_created = False
        start1 = time.time()

        for file_path in tqdm(file_path_array):

            df = func_load_dataset(file_path)

            df['lon'] = df['lon'].apply(lambda x: round(float(x),4))
            df['lat'] = df['lat'].apply(lambda x: round(float(x),4))

            # string
            df['my_time_stamp'] = df['my_time_stamp'].apply(lambda x: manipulate_datetime(x))

            # datetime.
            df['my_time_stamp2'] = df['my_time_stamp'].astype(np.datetime64)
            df = df.sort_values(by = 'my_time_stamp2')

            total_unique_time_steps = df['my_time_stamp2'].unique()

            # only one time-step is processed at a time due to GPU memory constraints.
            # change it to k time-steps based on available GPU memory.
            for i in range(len(total_unique_time_steps)):

                temp_df = df[(df['my_time_stamp2'] == total_unique_time_steps[i])]

                unique_time_steps = temp_df['my_time_stamp'].unique()

                # dictionary dict[my_time_stamp] >> 0
                # this dictionary part can be skipped or replaced when only one time-step is processed
                # at a time.
                dict_index_time_steps = dict(zip(unique_time_steps, range(len(unique_time_steps))))

                # dictionary dict[unique_bike_ids] >> index
                unique_bike_ids = temp_df['bike_id'].unique()
                dict_index_bikes = dict(zip(unique_bike_ids, range(len(unique_bike_ids))))

                # add a column with unique_bike_id indexes and my_time stamp indexes in the data-frame.
                temp_df['bike_id_index'] = temp_df['bike_id'].apply(lambda x: dict_index_bikes[x])
                temp_df['my_time_step_index'] = temp_df['my_time_stamp'].apply(lambda x: dict_index_time_steps[x])

                # initialize a numpy matrix with default values.

                # NOTE
                # A unique bike may not be present in the database for every time-step.
                # When it is not present, the raw files simply don't have a row for it.
                # But the attribute files created from here would have a row for it with
                # lon and lat set to a default value and attributed intersection set equal to
                # -10. So, any row in the outputted file with attribute intersection = -10
                # denotes that the bike is not present in the database for that time stamp.

                # In other words, the outputted file from here would have row corresponding to
                # every time stamp for which data is extracted for every bike. If the bike is
                # present in the database it would be filled in with appropriate values, and if
                # is not present in the database it is filled with default values and intersection
                # value of -10.

                lon_loc = np.full((len(unique_time_steps), len(unique_bike_ids)), -135.0)
                lat_loc = np.full((len(unique_time_steps), len(unique_bike_ids)), 90.0)

                lon_loc[temp_df['my_time_step_index'], temp_df['bike_id_index']] = temp_df['lon']
                lat_loc[temp_df['my_time_step_index'], temp_df['bike_id_index']] = temp_df['lat']

                assert lon_loc.shape[0] == 1  # change 1 to the number of time-stamps one is processing at a time.
                assert lon_loc.shape[1] == len(unique_bike_ids)

                min_dist, att_mat = func_attribute_intersection(lon_loc, lon_int, lat_loc, lat_int, threshold_radius = 200)
                time_df = [unique_time_steps[0] for t in range(len(unique_bike_ids))]

                min_dist = min_dist.reshape(min_dist.shape[1])
                att_mat = att_mat.reshape(att_mat.shape[1])
                lon_loc = lon_loc.reshape(lon_loc.shape[1])
                lat_loc = lat_loc.reshape(lat_loc.shape[1])

                data = {'time':time_df, 'bike_id':unique_bike_ids,
                        'nearest street':att_mat, 'dist nearest street': min_dist,
                        'lon':lon_loc, 'lat':lat_loc}

                df_out = pd.DataFrame(data = data)

                if not out_file_created:
                    df_out.to_csv(dir_id2+company_name+"_"+dataset_folder+".csv")
                    out_file_created = True

                else:
                    df_out.to_csv(dir_id2+ company_name +"_"+dataset_folder+".csv", mode='a', header=False)