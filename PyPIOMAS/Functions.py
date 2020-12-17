# "`-''-/").___..--''"`-._
#  (`6_ 6  )   `-.  (     ).`-.__.`)   WE ARE ...
#  (_Y_.)'  ._   )  `._ `. ``-..-'    PENN STATE!
#    _ ..`--'_..-_/  /--'_.' ,'
#  (il),-''  (li),'  ((!.-'
#
# Author: Weiming Hu <weiming@psu.edu, https://weiming-hu.github.io/>
#         Geoinformatics and Earth Observation Laboratory (http://geolab.psu.edu)
#         Department of Geography and Institute for Computational and Data Sciences
#         The Pennsylvania State University
#

import os
import re
import struct
import urllib3
import requests
import datetime
import warnings

import numpy as np
import xarray as xr

# Disable HTML warnings
urllib3.disable_warnings()


def determine_downloadable_file_url(base_url, folder, variable, year, ignore_warnings=False):
    """
    PIOMAS data files can have two types of files names, `area.H2019.gz` and `area.H2020`. Usually the latter is
    uncompressed and it is because it has just been generated. This function determines the actual file name to
    download by probing the data repository and check whether the uncompressed or the compressed file exists.

    :param base_url: The source URL, usually `https://pscfiles.apl.washington.edu/zhang/PIOMAS/data/v2.1`
    :param folder: The folder name following the base url
    :param variable: The variable name at the beginning of the file name
    :param year: The year at the end of the file name
    :param ignore_warnings: Whether to ignore warning
    :return: A downloadable URL
    """

    # Define the regular expression to identify the file name to download
    regex = f'>({variable}.H{year}.*?)<'

    # Download the index page
    index_url = '/'.join([base_url, folder])
    index_page = requests.get(index_url, verify=False)

    if index_page.status_code != 200:
        if not ignore_warnings:
            warnings.warn('Failed to reach {}. Skipped.'.format(index_url))

        return None

    # Find the file name
    match = re.findall(regex, index_page.text)

    if len(match) == 0:
        if not ignore_warnings:
            warnings.warn("No files found for '{}' on {}".format(regex, index_url))

        return None

    elif len(match) > 1:
        if not ignore_warnings:
            warnings.warn("Multiple files found for '{}' on {}".format(regex, index_url))

        return None

    return '/'.join([index_url, match[0]])


def get_grid_2d():
    """
    Download the 2D grid
    :return: a tuple with x and y
    """
    url = 'https://pscfiles.apl.washington.edu/zhang/PIOMAS/utilities/grid.dat'

    # Get the coordinates
    coords = requests.get(url, verify=False).text.split()

    # Get the count
    count = len(coords) // 2

    # Parse x and y
    x = [float(e) for e in coords[:count]]
    y = [float(e) for e in coords[count:]]
    assert len(x) == len(y)

    return x, y


def download_file_url(url, dest_file):
    """
    Download a file. This is usually called after getting a downloadable URL from `determine_downloadable_file_url`.
    :param url: A downloadable URL
    :param dest_file: A file name for saving
    """

    r = requests.get(url, verify=False)

    with open(os.path.expanduser(dest_file), 'wb') as f:
        f.write(r.content)


def convert_to_netcdf_batch(files_in, short_names, years, long_names, units, file_out, verbose=True):
    """
    Convert and merge unzipped and raw PIOMAS data files to a single NetCDF file. This function will combine all
    variables into a single NetCDF file by calling `convert_to_netcdf` and writing to the same file. Variable names
    will include the variable short names and the corresponding years.

    :param files_in: The raw data files to convert
    :param short_names: The corresponding short names
    :param years: The corresponding years
    :param long_names: The corresponding long names
    :param units: The corresponding units. Use an empty string if a variable is unitless.
    :param file_out: The output NetCDF file
    :param verbose: Whether to be verbose
    """

    # Sanity check
    assert len(files_in) == len(short_names) == len(long_names) == len(units) == len(years), \
        'Inputs should have the same length!'

    # Determine the grid
    xs, ys = get_grid_2d()

    # Initialize an NetCDF dataset
    ds = xr.Dataset(coords={'x': ('grid', xs), 'y': ('grid', ys)})
    ds.to_netcdf(os.path.expanduser(file_out), mode='w', format='NETCDF4')

    for file_in, short_name, year, long_name, unit in zip(files_in, short_names, years, long_names, units):
        convert_to_netcdf(file_in, short_name, year, long_name, unit, file_out, ds.grid.size, verbose)


def convert_to_netcdf(file_in, short_name, year, long_name, unit, file_out, num_grids, verbose=True):
    """
    Convert an unzipped and raw PIOMAS data file to an NetCDF file. Currently it only supports

    1. scalar fields
    2. the 2D grid type

    :param file_in: The data file to convert
    :param short_name: The corresponding short name
    :param year: The corresponding year
    :param long_name: The corresponding long name
    :param unit: The corresponding unit
    :param file_out: The output NetCDF file. If exists, variables will be appended into the file.
    :param num_grids: Number of grids. This is for reshaping the PIOMAS data. It is usually 360 x 120 = 43200, as
    denoted from http://psc.apl.uw.edu/research/projects/arctic-sea-ice-volume-anomaly/data/model_grid
    :param verbose: Whether to be verbose
    """

    file_in = os.path.expanduser(file_in)
    file_out = os.path.expanduser(file_out)

    # Excluding the following variables due to various reasons
    if short_name in (
            'icevel',                 # U and V components need to be parsed. Can't find documentation of the data.
            'gice', 'giceday',        # A sub-grid is used but I did not implement the method for that
            'otemp1_10', 'osali1_10'  # A 3D grid is used but currently I have only dealt with the 2D grid.
    ):
        if verbose:
            warnings.warn('Currently not supporting conversion of {}'.format(short_name))

        return

    if verbose:
        print('Adding {} ({}) from year {} ...'.format(long_name, short_name, year))

    # Read the raw data
    with open(file_in, mode='rb') as con:
        file_content = con.read()

    # Calculate the count of floating-point numbers
    count = len(file_content) // 4

    # Unpack data
    data = struct.unpack('f' * count, file_content)

    # Reshape data
    data = np.array(data).reshape((-1, num_grids))

    # Determine variable name
    var_name = '{}_{}'.format(short_name, year)

    if data.shape[0] == 12:
        # Data are monthly averages
        data = xr.DataArray(data, dims=('month', 'grid'), name=var_name)

    elif data.shape[0] == 365:
        # Data are daily averages
        data = xr.DataArray(data, dims=('day', 'grid'), name=var_name)

    elif int(year) == datetime.date.today().year:
        # Data for current year could be incomplete but should be allowed
        data = xr.DataArray(data, dims=('dim_0_{}'.format(var_name), 'grid'), name=var_name)

    else:
        warnings.warn('{} data have shape {}. This is currently not supported.'.format(short_name, data.shape))
        return

    # Assign attributes
    data = data.assign_attrs(long_name=long_name, units=unit)

    data.to_netcdf(file_out, mode='a' if os.path.exists(file_out) else 'w')


def stack_variables_by_years(file_in, file_out, variable, verbose=True):
    """
    Stack multiple NetCDF variables along a new dimension, `year`. The variable names are expected to follow the
    convention `<short name>_<year>`.

    :param file_in: An NetCDF file to read data from
    :param file_out: An NetCDF file to write
    :param variable: The variable to stack
    :param verbose: Whether to be verbose
    """

    file_in = os.path.expanduser(file_in)
    file_out = os.path.expanduser(file_out)

    # Read the NetCDF file
    ds = xr.open_dataset(file_in)

    # Get variables to stack
    variables_to_stack = [var for var in ds.data_vars if variable in var]
    variables_to_stack.sort()

    if len(variables_to_stack) == 0:
        ds.close()
        return

    # Make sure dimensions match
    variables_to_stack = [var for var in variables_to_stack if ds[var].shape == ds[variables_to_stack[0]].shape]

    if verbose:
        print('Stacking [{}] to be {} ...'.format(', '.join(variables_to_stack), variable))

    # Stack
    years = [int(var.split('_')[1]) for var in variables_to_stack]
    da = xr.concat([ds[var] for var in variables_to_stack], dim='year', coords='minimal')

    # Fix meta information
    da.coords['year'] = years
    da.name = variable

    # Write to files
    da.to_netcdf(file_out, mode='a' if os.path.exists(file_out) else 'w')
    ds.close()

