from __future__ import annotations
import typing
import xarray
import numpy as np
from dateutil.parser import parse
from datetime import datetime, date, timedelta

from .web import downloadfile
from .io import load

def get_indices(time: str | datetime | date, station: str, forcedownload: bool = False) -> xarray.Dataset:
    """Get digisonde measurements from specified station at the specified time.

    Args:
        time (str | datetime | date): Timestamp (UTC)
        station (str): 5-letter station code
        forcedownload (bool, optional): Force down. Defaults to False.

    Returns:
        xarray.Dataset: xarray dataset containing the measurements from the station.
    """
    dtime = todatetime(time)
    fn = downloadfile(dtime, station, forcedownload)
    dat: xarray.Dataset = load(fn)
    if len(dat['time']) == 0:
        return dat
    return dat.sel(time=dtime, method='nearest')


def todatetime(time: str | date | datetime | np.datetime64) -> typing.Any:
    if isinstance(time, str):
        d = todatetime(parse(time))
    elif isinstance(time, datetime):
        d = time
    elif isinstance(time, np.datetime64):
        d = time.astype(date)
    elif isinstance(time, date):
        d = datetime(time.year, time.month, time.day)
    elif isinstance(time, (tuple, list, np.ndarray)):
        d = np.atleast_1d([todatetime(t) for t in time]).squeeze()
    else:
        raise TypeError(f"{time} must be representable as datetime.date")

    dates = np.atleast_1d(d).ravel()

    return dates
