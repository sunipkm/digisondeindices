# Digisonde Indices
Digisonde Indices is a downloader and parser that retrieves F2 layer data (height, critical frequency, total electron content, B0) from the [DIDBase](https://giro.uml.edu/didbase/). Output datatype is [xarray.DataSet](https://docs.xarray.dev/en/latest/generated/xarray.Dataset.html). Missing data is returned as an empty dataset. 

### Example
Use from other scripts like:

```py
    import digisondeindices as didbase
    import datetime as dt

    date = dt.datetime(2012, 1, 1, 5, 0, 0) # 2012-01-01 05:00:00 UTC
    inds = didbase.get_indices(date, 'AH223') # retrieve data from Ahmedabad station
```
A list of available stations is provided by the [Global Ionosphere Radio Observatory](https://giro.uml.edu/index.html):
[DIDBase stations list](https://lgdc.uml.edu/common/DIDBFastStationList)