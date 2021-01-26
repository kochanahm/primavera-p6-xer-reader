# this is a global dict to store each table in XER. In case multiple projects this is raw df
my_dataframes = {}

# this is filtered version for selected proj_id. Instead of putting condsition for proj_id in all queries, we fill
# filter in the beginning and use these data frames
my_filt_dataframes = {}
