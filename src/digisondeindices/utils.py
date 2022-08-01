from __future__ import annotations
from datetime import datetime, timedelta
import numpy as np
from pathlib import Path
import importlib.resources
from dateutil.parser import parse
import os

def checkIfExists(time: np.ndarray, station: str) -> list[Path]:
    with importlib.resources.path(__package__, "__init__.py") as fn:
        path = fn.parent / "data"
        if not path.exists():
            os.mkdir(path, 0o777)
        if not path.is_dir():
            raise NotADirectoryError(path)
    
    time = np.asarray(time)
    tnow = datetime.today()
    tmin = time.min()
    tmax = time.max()

    dfiles = list(path.glob('%s*.txt'%(station)))
    if len(dfiles) == 0:
        return []
    
    for fpath in dfiles:
        fname = os.path.basename(fpath)
        fmin = get_min(fname)
        fmax = get_max(fname)
        if fmin <= tmin and tmax <= fmax:
            return [fpath]
    
    return []


def get_min(fname: str) -> datetime:
    words = fname.split('.txt')[0].split('_')
    if len(words[0]) != 5 or not words[0].isalnum() or len(words) != 3 or len(words[1]) != 8 or len(words[2]) != 8:
        raise RuntimeError('Invalid file base name %s'%(fname))
    
    dt = words[1][0:4] + '-' + words[1][4:6] + '-' + words[1][6:8] + ' 00:00:00Z'
    return parse(dt)

def get_max(fname: str) -> datetime:
    words = fname.split('.txt')[0].split('_')
    if len(words[0]) != 5 or not words[0].isalnum() or len(words) != 3 or len(words[1]) != 8 or len(words[2]) != 8:
        raise RuntimeError('Invalid file base name %s'%(fname))
    
    dt = words[2][0:4] + '-' + words[2][4:6] + '-' + words[2][6:8] + ' 00:00:00Z'
    return parse(dt)
