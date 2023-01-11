import digisondeindices as didbase
import datetime as dt

# timezone-unaware example
date = dt.datetime(2012, 1, 1, 5, 0, 0) # 2012-01-01 05:00:00 UTC, even though datetime object created in timezone of machine at runtime
inds = didbase.get_indices(date, 'AH223') # retrieve data from Ahmedabad station

# timezone-aware example
date = dt.datetime(2012, 1, 1, 5, 0, 0) # 2012-01-01 10:00:00 UTC for US/Eastern (UTC-05:00) given execution machine time zone is set to US/Eastern
inds = didbase.get_indices(date, 'AH223', tzaware=True) # retrieve data from Ahmedabad station

print(inds)