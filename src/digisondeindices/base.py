from __future__ import annotations
from typing import List, Any
import xarray
import numpy as np
from dateutil.parser import parse
from datetime import datetime, date
import pytz
import pandas

from .web import downloadfile
from .io import load


def get_indices(time: str | datetime | List[np.datetime64] | np.ndarray, station: str, forcedownload: bool = False, *, dmuf: int = 3000, tzaware: bool = False) -> xarray.Dataset:
    """Get digisonde measurements from specified station at the specified time.

    Args:
        time (str | datetime | List[np.datetime64] | np.ndarray): Date and time. Must be in UTC unless `tzaware` flag is set.
        station (str): 5-letter Digisonde station code.
        forcedownload (bool, optional): Force download of data. Defaults to False.
        dmuf (int, optional): Distance for MUF calculations (in km). Defaults to 3000.
        tzaware (bool, optional): Consider `time` as timezone aware. datetime() objects carry the timezone of the machine at runtime. Defaults to False.

    Returns:
        xarray.Dataset: xarray dataset containing the measurements from the station.
    """
    dtime = todatetime(time, tzaware)
    fn = downloadfile(dtime, station, forcedownload, dmuf)
    dat: xarray.Dataset = load(fn, station, dmuf)
    if len(dat['time']) == 0:
        return dat
    return dat.sel(time=dtime, method='nearest')


def todatetime(time: str | date | datetime | np.datetime64, tzaware: bool = True) -> Any:
    if isinstance(time, str):
        d = todatetime(parse(time), tzaware)
    elif isinstance(time, datetime):
        if tzaware:
            # convert to UTC and strip timezone
            d = time.astimezone(pytz.utc).replace(tzinfo=None)
        else:
            # simply strip timezone info, old behavior
            d = time.replace(tzinfo=None)
    elif isinstance(time, np.datetime64):
        d = todatetime(time.astype(datetime), tzaware)
    elif isinstance(time, date):
        d = todatetime(datetime(time.year, time.month, time.day), tzaware)
    elif isinstance(time, (tuple, list, np.ndarray)):
        d = np.atleast_1d([todatetime(t, tzaware) for t in time]).squeeze()
    elif isinstance(time, pandas.DatetimeIndex):
        d = todatetime(time.to_pydatetime(), tzaware)
    else:
        raise TypeError(f"{time} must be representable as datetime.datetime")

    dates = np.atleast_1d(d).ravel()

    return dates

def cli():
    """
    simple demo of retrieving DIDBase indices by date
    """
    from argparse import ArgumentParser

    p = ArgumentParser()
    p.add_argument("date", help="time of observation yyyy-mm-ddTHH:MM:ss")
    p.add_argument("-s", "--station", help='Observation station code e.g. AH223', type=str)
    a = p.parse_args()

    inds = get_indices(a.date, p.station)

    print(inds)


if __name__ == "__main__":
    cli()