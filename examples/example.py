import digisondeindices as didbase
import datetime as dt

# timezone-unaware example
# 2012-01-01 05:00:00 UTC, even though datetime object created in timezone of machine at runtime
date = dt.datetime(2022, 1, 25, 5, 0, 0)
inds = didbase.get_indices(date, 'MHJ45')  # retrieve data from Ahmedabad station

print(inds)

# timezone-aware example
# 2012-01-01 10:00:00 UTC for US/Eastern (UTC-05:00) given execution machine time zone is set to US/Eastern
date = dt.datetime(2022, 1, 25, 5, 0, 0)
inds = didbase.get_indices(date, 'MHJ45', tzaware=True)  # retrieve data from Ahmedabad station

print(inds)

print('Press any key to exit...')
input()
