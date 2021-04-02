from generate_grid_washington_dc import generate_grid

# grid size in meters

grid_size = 400


df_result = generate_grid(grid_size).run_main()
df_result.to_excel("output9.xlsx")
