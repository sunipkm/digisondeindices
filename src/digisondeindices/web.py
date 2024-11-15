from __future__ import annotations
from pathlib import Path
import ftplib
import requests
from urllib.parse import urlparse
from datetime import datetime
import socket
import requests.exceptions
import numpy as np
import importlib.resources
import os
from natsort import natsorted

from .io import convert_csv

TIMEOUT = 15  # seconds


def downloadfile(time: np.ndarray, station: str, force: bool, dmuf: int = 3000) -> list[Path]:

    with importlib.resources.path(__package__, "__init__.py") as fn:
        path = fn.parent / "data"
        if not path.exists():
            os.makedirs(path, mode=0o777, exist_ok=False)
        if not path.is_dir():
            raise NotADirectoryError(path)

    time = np.asarray(time)
    tnow = datetime.today()
    tmin: datetime = time.min()
    tmax: datetime = time.max()
    if tmin > tnow:
        raise RuntimeError(
            'DIDBase package does not allow prediction retrieval.')
    tmax: datetime = np.min([tmax, tnow])  # limit to current time
    min_year = tmin.year
    max_year = tmax.year
    years = np.arange(min_year, max_year + 1)
    min_mon = tmin.month
    max_mon = tmax.month
    flist = []
    lims = []
    for y in years:
        if y == min_year:
            min_mon = tmin.month
        else:
            min_mon = 1
        if y == max_year:
            max_mon = tmax.month
        else:
            max_mon = 12
        for m in range(min_mon, max_mon + 1):
            start = (y, m)
            if m == 12:
                end = (y + 1, 1)
            else:
                end = (y, m + 1)
            lims.append((start, end))
    for (start, end) in lims:
        y0, m0 = start
        y1, m1 = end
        url = f'https://lgdc.uml.edu/common/DIDBGetValues?' \
            f'ursiCode={station}&charName=hmE,foE,hmF1,foF1,hmF2,foF2,hF,hF2,yF1,yF2,B0,TEC,MUFD' '&' \
            f'DMUF={dmuf}' '&' \
            f'fromDate={y0:04d}.{m0:02d}.01+00:00:00' '&' \
            f'toDate={y1:04d}.{m1:02d}.01+00:00:00'
        # try to load the nc file
        fn = path / (f'{station}_{y0:04d}_{m0:02d}_{dmuf}.nc')

        # forced or file expired or file does not exist
        if force or not exist_ok(fn, tmax):
            try:
                fn_txt = fn.with_suffix('.txt')  # get text file name
                # if text file does not exist or redownload is forced
                if force or not exist_ok(fn, tmax):
                    download(url, fn_txt)  # download text file
                # convert text file to nc file
                flist.append(convert_csv(fn_txt, station, dmuf))  # append now existing nc file
            except ConnectionError:
                raise ConnectionError(url)
        else:
            flist.append(fn)  # append existing nc file
    return natsorted(list(set(flist)), key=lambda f: f.stem)  # dedupe


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
    if fn.exists():
        return

    has_tqdm = False
    try:
        from tqdm import tqdm
        has_tqdm = True
    except ImportError:
        pass

    try:
        if has_tqdm:
            response = requests.get(
                url, allow_redirects=True, stream=True, timeout=TIMEOUT)
            if response.status_code == 200:
                total = int(response.headers.get('content-length', 0))
                with fn.open('wb') as file, tqdm(
                        desc=fn.stem,
                        total=total,
                        unit='iB',
                        unit_scale=True,
                        unit_divisor=1024,
                        ncols=80
                ) as bar:
                    for data in response.iter_content(chunk_size=1024):
                        size = file.write(data)
                        bar.update(size)
            else:
                raise ConnectionError(
                    f"Could not download {url} to {fn}: Error {response.status_code}")
        else:
            R = requests.get(url, allow_redirects=True, timeout=TIMEOUT)
            if R.status_code == 200:
                fn.write_text(R.text)
            else:
                raise ConnectionError(
                    f"Could not download {url} to {fn}: Error {R.status_code}")
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
