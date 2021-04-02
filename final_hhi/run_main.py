from main1_class import hhi_main1


# select "circle" for circular boundary and put the required radius as additional_params.
# select "square" for square boundary and put the required square length as additional_params.
# (center of circle and square is the reference intersection)

# select "nearest_neighbor" to get the hhi_ratio using the nearest intersections and add
# total number of nearest neighbor as additional_params.


top_intersections = 2000
boundary_type = "square"
additional_params = 500

class1 = hhi_main1(top_intersections, boundary_type, additional_params)
df = class1.main()
for i in range(len(df)):
    print(df['hhi_ratio'][i], df['total_intersections'][i])

