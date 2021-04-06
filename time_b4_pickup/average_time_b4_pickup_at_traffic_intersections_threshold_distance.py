#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import numpy as np
from tqdm import tqdm


# In[2]:


def calc_distance(lon1, lat1, lon2, lat2):

    lon1 = np.radians(np.float64(lon1))
    lat1 = np.radians(np.float64(lat1))

    lon2 = np.radians(np.float64(lon2))
    lat2 = np.radians(np.float64(lat2))

    value = np.sin(lat1) * np.sin(lat2) + (np.cos(lat1) * np.cos(lat2) * np.cos(lon1 - lon2))

    if value > 1:
        value = 1
    dist = 6371.01 * 1000 * np.arccos(value)

    return dist


# In[3]:


df = pd.read_csv(r"D:\trip_datasets\dataset_modified" + "/" + "all_trips_2020_0_mod.csv")
df['start_time2'] = pd.to_datetime(df['start_time'])
df['end_time2'] = pd.to_datetime(df['end_time'])

df['hour'] = df['start_time2'].apply(lambda x: x.hour)
df = df[(df['hour'] >= 8) & (df['hour'] <= 20)]
df = df.sort_values(by = ['start_time2'])


# In[4]:


df.info()


# In[5]:


def function_calc_avg(ttdf, dict1, trip_utilized, threshold_distance = 20):
    ttdf = ttdf.sort_values(by = ['start_time2'], ascending = True)
    ttdf = ttdf.reset_index(drop = True)
    
    for k in range(1, len(ttdf)):
        lon1 = ttdf['start_lon'][k]
        lat1 = ttdf['start_lat'][k]
        
        lon2 = ttdf['end_lon'][k-1]
        lat2 = ttdf['end_lat'][k-1]
        
        
        if ttdf['start_nearest_intersection'][k] == ttdf['end_nearest_intersection'][k-1]:
            wait_time = np.round(((ttdf['start_time2'][k] - ttdf['end_time2'][k-1]).total_seconds())/60.0, 2)
            street = ttdf['start_nearest_intersection'][k]
            dict1[street] = dict1[street] + [wait_time]
            trip_utilized += 1
            
        elif calc_distance(lon1, lat1, lon2, lat2) <= threshold_distance:
            wait_time = np.round(((ttdf['start_time2'][k] - ttdf['end_time2'][k-1]).total_seconds())/60.0, 2)
            street = ttdf['end_nearest_intersection'][k-1]
            dict1[street] = dict1[street] + [wait_time]
            trip_utilized += 1
        
        else:    
            continue
    
    
    return dict1, trip_utilized


# In[6]:


from collections import defaultdict
dict_time = defaultdict(lambda : [0])
unique_bikes = df['vehicle_id'].unique()

trip_utilized = 0

for i in tqdm(range(len(unique_bikes))):
    #print('###########', unique_bikes[i],(trip_utilized*100)/len(df), '###########')
    temp_df = df[df['vehicle_id'] == unique_bikes[i]]
    temp_df = temp_df.reset_index(drop = True)
    temp_df = temp_df.sort_values(by = ['start_time2'], ascending = True)
    temp_df['date'] = temp_df['start_time2'].dt.date
    
    unique_dates = temp_df['date'].unique()
    for j in range(len(unique_dates)):
        temp_temp_df = temp_df[temp_df['date'] == unique_dates[j]]
        dict_time, trip_utilized = function_calc_avg(ttdf = temp_temp_df, dict1 = dict_time, trip_utilized = trip_utilized)
    
        


# In[7]:


(trip_utilized*100)/len(df)


# In[8]:


dict_avg_wait_time = defaultdict(lambda : 0.0)
dict_len_wait_time = defaultdict(lambda : 0)
for key, values in dict_time.items():
    dict_avg_wait_time[key] = np.mean(values)
    dict_len_wait_time[key] = len(values)


# In[9]:


street = [i+1 for i in range(8437)]
data = {'street': street}
df_out = pd.DataFrame(data = data)
df_out['avg_wait_time'] = df_out['street'].apply(lambda x: dict_avg_wait_time[x])
df_out['len_wait_time'] = df_out['street'].apply(lambda x: dict_len_wait_time[x])
df_out


# In[10]:


df_out.to_excel("Average_Wait_Time_Method2.xlsx")

