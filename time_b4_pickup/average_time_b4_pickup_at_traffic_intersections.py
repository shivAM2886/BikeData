#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import numpy as np
from tqdm import tqdm

df = pd.read_csv(r"D:\trip_datasets\dataset_modified" + "/" + "all_trips_2020_0_mod.csv")
df['start_time2'] = pd.to_datetime(df['start_time'])
df['end_time2'] = pd.to_datetime(df['end_time'])

df['hour'] = df['start_time2'].apply(lambda x: x.hour)
df = df[(df['hour'] >= 8) & (df['hour'] <= 20)]
df = df.sort_values(by = ['start_time2'])


# In[2]:


def function_calc_avg(ttdf, dict1, trip_utilized):
    ttdf = ttdf.sort_values(by = ['start_time2'], ascending = True)
    ttdf = ttdf.reset_index(drop = True)
    #print("=========================", ttdf['date'][0], "=========================")
    for k in range(1, len(ttdf)):
        #print(ttdf['start_nearest_intersection'][k-1], ttdf['end_nearest_intersection'][k-1])
        #print(ttdf['start_nearest_intersection'][k], ttdf['end_nearest_intersection'][k])
        
        if ttdf['start_nearest_intersection'][k] == ttdf['end_nearest_intersection'][k-1]:
            wait_time = np.round(((ttdf['start_time2'][k] - ttdf['end_time2'][k-1]).total_seconds())/60.0, 2)
            street = ttdf['start_nearest_intersection'][k]
            dict1[street] = dict1[street] + [wait_time]
            trip_utilized += 1
            #print((street, wait_time))
        else:
            #print("----")
            continue
    
    
    return dict1, trip_utilized


# In[3]:


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
    

    
    
        
        


# In[4]:


(trip_utilized*100)/len(df)


# In[7]:


dict_avg_wait_time = defaultdict(lambda : 0.0)
dict_len_wait_time = defaultdict(lambda : 0)
for key, values in dict_time.items():
    dict_avg_wait_time[key] = np.mean(values)
    dict_len_wait_time[key] = len(values)


# In[8]:


street = [i+1 for i in range(8437)]
data = {'street': street}
df_out = pd.DataFrame(data = data)
df_out['avg_wait_time'] = df_out['street'].apply(lambda x: dict_avg_wait_time[x])
df_out['len_wait_time'] = df_out['street'].apply(lambda x: dict_len_wait_time[x])
df_out


# In[9]:


df_out.to_excel("Average_Wait_Time_Method1.xlsx")

