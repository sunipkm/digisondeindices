# Digisonde Indices
Digisonde Indices is a downloader and parser that retrieves Digisonde data from [DIDBase](https://giro.uml.edu/didbase/). Output datatype is [xarray.DataSet](https://docs.xarray.dev/en/latest/generated/xarray.Dataset.html). Missing data is returned as an empty dataset. 

### Data Selection:
1. CS is Autoscaling Confidence Score (from 0 to 100, 999 if manual scaling, -1 if unknown)
2. foF2 (MHz) - F2 layer critical frequency
3. foF1 (MHz) - F1 layer critical frequency
4. MUFD (MHz) - Maximum usable frequency for ground distance D
5. foE (MHz) - E layer critical frequency
6. hF (km) - Minimum virtual height of F trace
7. hF2 (km) - Minimum virtual height of F2 trace
8. hmE (km) - Peak height of E-layer
9. hmF2 (km) - Peak height F2-layer
10. hmF1 (km) - Peak height F1-layer
11. yF2 (km) - Half thickness of F2-layer, parabolic model
12. yF1 (km) - Half thickness of F1-layer, parabolic model
13. B0 (km) - IRI thickness parameter
14. TEC (m^-2) - Total electron content

### Example
Use from other scripts like:

```py
import digisondeindices as didbase
import datetime as dt

# timezone-unaware example
date = dt.datetime(2012, 1, 1, 5, 0, 0) # 2012-01-01 05:00:00 UTC, even though datetime object created in timezone of machine at runtime
inds = didbase.get_indices(date, 'AH223') # retrieve data from Ahmedabad station

# timezone-aware example
date = dt.datetime(2012, 1, 1, 5, 0, 0) # 2012-01-01 10:00:00 UTC for US/Eastern (UTC-05:00) given execution machine time zone is set to US/Eastern
inds = didbase.get_indices(date, 'AH223', tzaware=True) # retrieve data from Ahmedabad station
```
Returned indices are always in UTC (as `numpy.datetime64`).

A list of available stations is provided by the [Global Ionosphere Radio Observatory](https://giro.uml.edu/index.html):
[DIDBase stations list](https://lgdc.uml.edu/common/DIDBFastStationList)

## Data License
All GIRO measurements are released under CC-BY-NC-SA 4.0 license.
Please follow the [Lowell GIRO Data Center RULES OF THE ROAD](https://ulcar.uml.edu/DIDBase/RulesOfTheRoadForDIDBase.htm).
Requires acknowledgement of station data provider.