import pandas as pd
import numpy as np

from generate_grid_washington_dc import generate_grid
from assign_trips_to_square2 import add_square_class, assign_trips_square
from calc_hhi import hhi
import seaborn as sns
# grid size in meters

grid_size = 400


x_max, y_max, df_square = generate_grid(grid_size).run_main()
dfs = add_square_class(df_square).run_main()



df_trip = pd.read_csv("all_trips_2020_0.csv")
df_trip = df_trip.dropna()
df_trip = df_trip.reset_index(drop = True)

dfs = assign_trips_square(df_trip, dfs).run_main()
print("assigned", np.sum(dfs['pickups'].values)/len(df_trip))

dfs = dfs.drop(columns = ['square_class'])


hhi1 = hhi(dfs = dfs, neighbors=1, x_max = x_max, y_max = y_max)
dfs = hhi1.run_main()

sns.distplot(dfs['hhi_ratio_1'].values)

dfs.to_excel("square_output.xlsx")