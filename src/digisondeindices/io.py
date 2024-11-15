from __future__ import annotations
from pathlib import Path
import xarray
import pandas as pd


def load(flist: list[Path], station: str, dmuf: int) -> xarray.Dataset:
    """
    select data to load and collect into xarray Dataset by time
    """
    return xarray.open_mfdataset(flist, combine='by_coords')


def convert_csv(file: Path, station: str, dmuf: int) -> Path:
    file_nc = file.with_suffix('.nc')  # get the equivalent nc name
    if file_nc.exists():  # if nc exists send it
        return
    # static column names
    columns = ['time', 'CS', 'foF2', 'QD1', 'foF1',
               'QD2', 'MUFD', 'QD3', 'foE', 'QD4',
               'hF', 'QD5', 'hF2', 'QD6', 'hmE',
               'QD7', 'hmF', 'QD8', 'hmF1', 'QD9',
               'yF2', 'QD10', 'yF1', 'QD11', 'B0',
               'QD12', 'TEC', 'QD13']  # columns in file
    valid_columns = [0, 1, 2, 4, 6, 8, 10, 12, 14, 16,
                     18, 20, 22, 24, 26]  # valid column indices
    units = ['%'] + 4 * ['MHz'] + 8 * ['km'] + ['m^-2']  # units for columns
    descs = [
        'Autoscaling confidence score (from 0 to 100, 999 if manual scaling, -1 if unknown)',
        'F2 layer critical frequency',
        'F1 layer critical frequency',
        'Maximum usable frequency for ground distance %d km' % (dmuf),
        'E layer critical frequency',
        'Minimum virtual height of F trace',
        'Minimum virtual height of F2 trace',
        'Peak height of E-layer',
        'Peak height F2-layer',
        'Peak height F1-layer',
        'Half thickness of F2-layer, parabolic model',
        'Half thickness of F1-layer, parabolic model',
        'IRI thickness parameter',
        'Total electron content'
    ]
    df = pd.read_csv(file, delimiter=' +', names=columns, usecols=valid_columns, comment='#',
                     engine='python', index_col=0, parse_dates=True, na_values='---')  # read data into pandas dataframe
    valid_names = df.columns.values.tolist()  # get valid column names
    # assert units and names are same length
    assert (len(valid_names) == len(units))
    assert (len(valid_names) == len(descs))
    ds = df.to_xarray()  # convert dataframe to dataset
    # pandas datetimeindex to datetime64
    ds['time'] = pd.DatetimeIndex(ds['time'].values)
    ds['TEC'] *= 1e16  # fix units of TEC
    _ = list(map(lambda x, y, z: ds[x].attrs.update(
        {'units': y, 'description': z}), valid_names, units, descs))  # apply unit attributes
    attrs = {}  # file attribute
    attrs['Info'] = f'Units of measurements can be accessed using the "units" attribute.\nDescription of measurements can be accessed using the "description" attribute.\nDistance D for MUF calculations: {
        dmuf} km'
    attrs['Station'] = station
    attrs['DMUF'] = f'{dmuf} km'
    attrs['Acknowledgement'] = f"All GIRO measurements are released under CC-BY-NC-SA 4.0 license\nPlease follow the Lowell GIRO Data Center RULES OF THE ROAD\nhttps://ulcar.uml.edu/DIDBase/RulesOfTheRoadForDIDBase.htm\nRequires acknowledgement of {
        station} data provider"
    attrs['Source'] = ''
    with open(file, 'r') as fstream:
        for idx, line in enumerate(fstream):
            line = line.strip()
            if idx < 3:
                attrs['Source'] = attrs['Source'] + line.strip('# ') + '\n'
            if len(line) == 0:
                continue
            if line[0] != '#':
                break
            line = line.split('#')[-1].strip()
            if 'Location' in line:
                attrs['Location'] = line.split(':', 1)[-1].strip()
            elif 'Instrument' in line:
                attrs['Instrument'] = line.split(':', 1)[-1].strip()
    ds.attrs.update(attrs)  # update the attributes
    ds.to_netcdf(file_nc)
    with xarray.load_dataset(file_nc) as ds2:
        if not ds.equals(ds2):
            file_nc.unlink()
            raise RuntimeError('NC file mismatch on readback, FATAL error!')
        else:
            file.unlink()  # at this point, unlink the text file
    return file_nc
