from __future__ import annotations
from pathlib import Path
import ftplib
import requests
from urllib.parse import urlparse
from datetime import datetime, timedelta
import subprocess
import socket
import requests.exceptions
import numpy as np
import importlib.resources
import os

TIMEOUT = 15  # seconds

def downloadfile(time: np.ndarray, station: str, force: bool) -> list[Path]:

    with importlib.resources.path(__package__, "__init__.py") as fn:
        path = fn.parent / "data"
        if not path.is_dir():
            os.makedirs(path, mode=0o777, exist_ok=False)

    time = np.asarray(time)
    tnow = datetime.today()
    tmin = time.min()
    tmax = time.max()
    if tmin > tnow:
        raise RuntimeError('DIDBase package does not allow prediction retrieval.')

    flist = []
    for t in time:
        if t < tnow:  # past
            url = 'https://lgdc.uml.edu/common/DIDBGetValues?ursiCode=%s&charName=foF2,MUFD,hmF2,B0,TEC&DMUF=3000&fromDate=%d.01.01+00:00:00&toDate=%d.01.01+00:00:00'%(station, t.year, t.year + 1)
            fn = path / ('%s_%d.txt'%(station, t.year))
            if force or not exist_ok(fn, tmax):
                try:
                    download(url, fn)
                    flist.append(fn)
                except ConnectionError:  
                    raise ConnectionError(url)
            else:
                flist.append(fn)

        else:
            raise RuntimeError('DIDBase package does not allow prediction retrieval.')

    return list(set(flist))  # dedupe


def download(url: str, fn: Path):

    if url.startswith("http"):
        http_download(url, fn)
    elif url.startswith("ftp"):
        ftp_download(url, fn)
    else:
        raise ValueError(f"not sure how to download {url}")


def http_download(url: str, fn: Path):
    if not fn.parent.is_dir():
        raise NotADirectoryError(fn.parent)

    try:
        R = requests.get(url, allow_redirects=True, timeout=TIMEOUT)
        if R.status_code == 200:
            fn.write_text(R.text)
        else:
            raise ConnectionError(f"Could not download {url} to {fn}")
    except requests.exceptions.ConnectionError:
        raise ConnectionError(f"Could not download {url} to {fn}")


def ftp_download(url: str, fn: Path):

    p = urlparse(url)

    host = p[1]
    path = "/".join(p[2].split("/")[:-1])

    if not fn.parent.is_dir():
        raise NotADirectoryError(fn.parent)

    try:
        with ftplib.FTP(host, "anonymous", "guest", timeout=TIMEOUT) as F, fn.open("wb") as f:
            F.cwd(path)
            F.retrbinary(f"RETR {fn.name}", f.write)
    except (socket.timeout, ftplib.error_perm, socket.gaierror):
        if fn.is_file():  # error while downloading
            fn.unlink()
        raise ConnectionError(f"Could not download {url} to {fn}")


def exist_ok(fn: Path, tmax: datetime = None) -> bool:
    if not fn.is_file():
        return False

    ok = True
    finf = fn.stat()
    ok &= finf.st_size > 1000
    if tmax is not None:
        ok &= tmax < datetime.utcfromtimestamp(finf.st_mtime)

    return ok

