from __future__ import annotations
from pathlib import Path
import xarray
import numpy as np
from datetime import datetime, timedelta
from dateutil.parser import parse

def load(flist: Path | list[Path]) -> xarray.Dataset:
    """
    select data to load and collect into xarray Dataset by time
    """

    if isinstance(flist, Path):
        flist = [flist]

    inds = []
    for fn in flist:
        inds.append(fload(fn))

    dat = xarray.concat(inds, dim='time')

    return dat

def fload(file: Path) -> xarray.Dataset:
    # columns: date-time, 
    # hmF2 (km), 
    # foF2 (MHz), 
    # TEC (1e16 m^-2), 
    # MUFD (MHz) - Maximum usable frequency for ground distance 3000 km, 
    # B0 (km) - IRI thickness parameter, 
    # autoscale confidence % - 999 indicates manual
    data = []
    dates = []
    with open(file, 'r') as f:
        station = ''
        # get all the lines
        for line in f:
            if len(line) == 0: # empty, continue
                continue
            if line.lstrip()[0] == '#': # comment, get station ID
                lwords = line.rstrip().split('URSI-Code')
                lwords = list(filter(('').__ne__, lwords))
                if len(lwords) == 2: # valid
                    station = lwords[1].lstrip().split(' ')[0]
                else:
                    continue
            words = line.rstrip().split(' ')
            words = list(filter(('').__ne__, words))
            if len(words) != 12:
                continue
            _data = None
            try:
                hmf = float(words[6])
                fof = float(words[2])
                tec = float(words[8])
                muf = float(words[4])
                b0 = float(words[10])
                cs = float(words[1])
                _data = [hmf, fof, tec, muf, b0, cs]
            except Exception as e:
                continue
            if _data is not None:
                try:
                    dates.append(parse(words[0]))
                except Exception as e:
                    continue
                data.append(_data)
    data = np.asarray(data, dtype = float).transpose()
    if len(data) == 0:
        data = [[], [], [], [], [], []]
    for i in range(len(dates)):
        dates[i] = dates[i].replace(tzinfo=None)
    df = xarray.Dataset(data_vars=dict(
                                        hmF2=(['time'], data[0], {'units': 'km'}),
                                        foF2=(['time'], data[1], {'units': 'MHz'}),
                                        TEC=(['time'], data[2], {'units': 'm^-2'}),
                                        MUFD=(['time'], data[3], {'units': 'MHz'}),
                                        B0=(['time'], data[4], {'units': 'km'}),
                                        CS=(['time'], data[5], {'units': '%'}),
                                    ),
                        coords=dict(time=dates),
                        attrs={'station': station}
        )
    df['TEC'] *= 1e16
    return df