#!/usr/bin/env python
# coding: utf-8

# In[8]:


import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.feature_selection import f_regression
from yellowbrick.regressor import ResidualsPlot
from sklearn.metrics import mean_squared_error
import statsmodels.formula.api as smf


# In[9]:


class run_regression:
    
    def __init__(self, part_of_day):
        self.part_of_day = part_of_day
        
    
    def load_dataset(self, part_of_day):
        df = pd.read_excel("regression_1_final_data1.xlsx")
        df = df[df['part_of_day'] == part_of_day]
        df = df[df['avail'] > 1]
        df = df[df['pickups'] > 1]
        df['ln_avail'] = np.log(df['avail'].values)
        df['ln_pickups'] = np.log(df['pickups'].values)
        df = df.drop(columns = ['avail', 'pickups'])
        df = df.reset_index(drop = True)
        
        return df
    
    def change_poi_col_names(self, df):
        col_poi = df.drop(columns = ['Unnamed: 0', 'street_p', 'ln_pickups', 
                                     'street_a', 'ln_avail', 'part_of_day',
                                    'cluster_id']).columns
        
        dict1 = {}
        
        count = 0
        for col in col_poi:
            dict1[col] = 'poi_'+str(count)
            count += 1
            
        df = df.rename(columns = dict1)
        
        return df
    
    def get_dummies1(self, df):
        unique_cluster = df['cluster_id'].unique()
        df = pd.get_dummies(columns = ['cluster_id'], data = df)
        
        col_cluster_id_dummies = []
        for i in range(len(unique_cluster)):
            col_cluster_id_dummies.append('cluster_id_'+
                                          str(unique_cluster[i]))
        
        return df, col_cluster_id_dummies
    
    def transform(self, df, col_name1, dummy_col_name_array):
        dict1 = {}
        for x in dummy_col_name_array:
            temp_df = df[df[x] == 1]
            dict1[x] = np.mean(temp_df[col_name1].values)
        
        dict_keys = list(dict1.keys())
        X = df[dict_keys].values
        
        T = np.asarray(list(dict1.values()))
        T = T.reshape(len(T), 1)
        
        transformed_values = np.matmul(X, T)
        
        return transformed_values
    
    def func_col_to_be_transformed(self):
        col_to_be_transformed = ['ln_avail', 'ln_pickups']
        for i in range(31):
            temp_col_name = 'poi_' + str(i)
            col_to_be_transformed.append(temp_col_name)
        
        return col_to_be_transformed
        
    
    def func_transformed_column_names(self, col_to_be_transformed, dummy_col_name_array, df):
        transformed_column_names = []
        
        for col_name1 in col_to_be_transformed:
            temp_col_name1 = 'diff_' + col_name1

            transformed_values = self.transform(df, col_name1, dummy_col_name_array)

            df[temp_col_name1] = transformed_values
            transformed_column_names.append(temp_col_name1)
        
        return df, transformed_column_names
        
    
    def modify_dataset(self, df, transformed_column_names):
        df1 = df[transformed_column_names]
        return df1
    
    def regression1(self, df1):
        col_remain = df1.drop(columns = ['diff_ln_avail', 'diff_ln_pickups']).columns
        eq_string = col_remain[0]
        
        for i in range(1, len(col_remain)):
            eq_string = eq_string + "+" + col_remain[i]
            
        formula = 'diff_ln_pickups ~ diff_ln_avail' + '+' + eq_string
        mod = smf.ols(formula= formula, data=df1)
        res = mod.fit()
        results_summary = res.summary()
        
        return results_summary
    
    def drop_func_p_value(self, results_summary, df1):
        results_as_html = results_summary.tables[1].as_html()
        
        df_results1 = pd.read_html(results_as_html, 
                                   header = 0, index_col = 0)[0]
        df_results1 = df_results1.reset_index()
        
        dict_p = dict(zip(df_results1['index'].values, 
                          df_results1['P>|t|'].values))
        
        col_drop1 = []
        for key, value in dict_p.items():
            if value > 0.005:
                col_drop1.append(key)
        
        df2 = df1.drop(columns = col_drop1)
        return df2
    
    
    def main(self):
        
        df = self.load_dataset(part_of_day)
        df = self.change_poi_col_names(df)
        df, dummy_col_name_array = self.get_dummies1(df)
        
        col_to_be_transformed = self.func_col_to_be_transformed()
        
        df, transformed_column_names = self.func_transformed_column_names(col_to_be_transformed, dummy_col_name_array, df)
        
        df1 = self.modify_dataset(df, transformed_column_names)
        results_summary = self.regression1(df1)
        
        df2 = self.drop_func_p_value(results_summary, df1)
        results_summary2 = self.regression1(df2)
        
        df3 = self.drop_func_p_value(results_summary2, df2)
        results_summary3 = self.regression1(df3)
        
        print(results_summary3)
            


# In[10]:


part_of_day_array = ['morning', 'late_morning',
                    'mid_day', 'evening',
                    'late_evening']


# In[11]:


for part_of_day in part_of_day_array:
    
    temp_class = run_regression(part_of_day)
    temp_class.main()
    
    

