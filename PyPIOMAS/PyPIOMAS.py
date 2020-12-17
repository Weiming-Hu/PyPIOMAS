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

import gzip
import glob
import shutil

from PyPIOMAS.Functions import *


class PyPIOMAS:
    """
    PyPIOMAS makes downloading and converting PIOMAS dataset easier. It currently supports downloading of all
    available variables and converting scalar variables with a 2D grid type to NetCDF format.

    This class relies heavily on the functions from `Functions`. Feel free to check out the functions and call
    these function directly. PyPIOMAS simply makes it easier to call those functions.
    """

    ############################
    # Updated on Dec. 13, 2020 #
    ############################

    # The supported variables for downloading
    supported_variables = (
        'heff', 'hiday', 'aiday', 'area', 'advect', 'alb', 'gice', 'giceday', 'iceprod', 'icevel',
        'oflux', 'osali', 'osali1_10', 'otemp', 'otemp1_10', 'snow', 'snowday', 'ssh', 'tice0',
    )

    # The folder name for each supported variables
    variables_folder = (
        'heff', 'hiday', 'area', 'area', 'other', 'other', 'other', 'other', 'other', 'other',
        'other', 'other', 'other', 'other', 'other', 'other', 'other', 'other', 'other',
    )

    variable_long_names = (
        'Monthly sea ice thickness', 'Daily sea ice thickness', 'Daily sea ice concentration',
        'Monthly sea ice concentration', 'Sea ice advection', 'Albedo',
        'Monthly 12-category ice thickness distribution',
        'Daily 12-category ice thickness distribution',
        'Sea ice growth or melt rate', 'Sea ice velocity',
        'Ocean heat flux used to melt ice', 'Ocean surface salinity',
        'Ocean salinity of upper 10 levels', 'Ocean surface temperature',
        'Ocean temperature of upper 10 levels', 'Monthly snow depth',
        'Daily snow depth', 'Sea surface height', 'Surface temperature',
    )

    variable_units = (
        '$m$', '$m$', '', '', '$m/2$', '', '', '', '$m/s$', '$m/2$',
        '$m/2$', '$psu$', '$psu$', '$K$', '$psu$', '$m$', '$m$', '$cm$', '$C$',
    )

    def __init__(self, dest_dir, variables, years, verbose=True):
        """
        Initialize a downloader

        :param dest_dir: The folder to store data
        :param variables: The variables to download. Check `PyPIOMAS.supported_variables` for supported variables.
        :param years: The years to download. Make sure the years are present from the downloading page.
        :param verbose: Whether to be verbose
        """

        # Check whether all variables are needed
        if variables == 'all':
            variables = PyPIOMAS.supported_variables

        # Sanity check
        assert isinstance(years, list) or isinstance(years, tuple)
        assert isinstance(variables, list) or isinstance(variables, tuple)

        # Check whether variables are supported
        for variable in variables:
            if variable not in PyPIOMAS.supported_variables:
                err_msg = f"{variable} is not supported. Use PyPIOMAS.supported_variables to check options."
                raise RuntimeError(err_msg)

        # Initialization
        self.years = years
        self.verbose = verbose
        self.variables = variables
        self.dest_dir = os.path.expanduser(dest_dir)

        # This is where the data are actually stored
        self.base_url = 'https://pscfiles.apl.washington.edu/zhang/PIOMAS/data/v2.1'

    def download(self, skip_existing=True):
        """
        Download data

        :param skip_existing: Whether to skip downloading a file if the name already exists.
        """

        if not os.path.isdir(self.dest_dir):
            os.mkdir(self.dest_dir)

            if self.verbose:
                print('Created a directory at {}'.format(self.dest_dir))

        # Download raw files
        for variable in self.variables:
            for year in self.years:

                # Determine the file name to download
                url = determine_downloadable_file_url(
                    base_url=self.base_url,
                    folder=PyPIOMAS.variables_folder[PyPIOMAS.supported_variables.index(variable)],
                    variable=variable,
                    year=year,
                    ignore_warnings=False)

                if url is None:
                    print('Skip {} of year {}. See warnings.'.format(variable, year))
                    continue

                # Download the data file
                dest_file = os.path.join(self.dest_dir, os.path.basename(url))

                if os.path.exists(dest_file) and skip_existing:
                    if self.verbose:
                        print('{} already exists. Skipped.'.format(dest_file))

                else:
                    if self.verbose:
                        print('Downloading {} ...'.format(dest_file))

                    download_file_url(url=url, dest_file=dest_file)

        if self.verbose:
            print('File transfer completes! Output has been saved to {}'.format(self.dest_dir))

    def unzip(self, ext='.gz', skip_existing=True):
        """
        Unzip data files

        :param ext: The expected extension
        :param skip_existing: Whether to skip unzipping if the file name exists
        """

        assert ext == '.gz', 'Currently only supports gz files'

        # Get all files to unzip
        files_to_unzip = []

        for variable in self.variables:
            for year in self.years:
                expected_name = '{}.H{}{}'.format(variable, year, ext)
                files_to_unzip.extend(glob.glob(os.path.join(self.dest_dir, expected_name)))

        for file in files_to_unzip:

            # Strip the extension
            file_out = file.rstrip(ext)

            if os.path.isfile(file_out) and skip_existing:
                if self.verbose:
                    print('{} already exists. Skipped!'.format(file_out))

            else:
                if self.verbose:
                    print('Unzipping {} ...'.format(file))

                with gzip.open(file, 'rb') as f_in:
                    with open(file_out.rstrip(ext), 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)

        if self.verbose:
            print('Unzipped all {} files.'.format(ext))

    def to_netcdf(self, file_out, overwrite=True, stack_years=True):
        """
        Convert unzipped and raw PIOMAS data files to NetCDF

        :param file_out: An NetCDF file name to write to
        :param overwrite: Whether to overwrite
        :param stack_years: Whether to also stack variables based on the year information
        """

        file_out = os.path.expanduser(file_out)

        if os.path.exists(file_out) and overwrite:
            os.remove(file_out)

        # Find files to convert to NetCDF
        files_to_convert = []

        for variable in self.variables:
            for year in self.years:
                expected_name = '{}.H{}'.format(variable, year)
                files_to_convert.extend(glob.glob(os.path.join(self.dest_dir, expected_name)))

        # Determine meta information for each file
        short_names, years, long_names, units = [], [], [], []

        for file in files_to_convert:
            base_name = os.path.basename(file)

            name, year = base_name.split('.H')
            index = PyPIOMAS.supported_variables.index(name)
            long_name = PyPIOMAS.variable_long_names[index]
            unit = PyPIOMAS.variable_units[index]

            short_names.append(name)
            years.append(year)
            long_names.append(long_name)
            units.append(unit)

        # Convert
        convert_to_netcdf_batch(files_in=files_to_convert, short_names=short_names, years=years,
                                long_names=long_names, units=units, file_out=file_out, verbose=self.verbose)

        if stack_years:
            file_tmp = '{}.tmp'.format(file_out)

            if self.verbose:
                print('Stacking multiple years ...')

            for variable in self.variables:
                stack_variables_by_years(file_out, file_tmp, variable, self.verbose)

            os.remove(file_out)
            os.rename(file_tmp, file_out)

        if self.verbose:
            print('An NetCDF file has been generated at {}!'.format(file_out))

    def __str__(self):
        msg = "*************** PIOMAS Data Downloader ***************\n" + \
              "Source: http://psc.apl.uw.edu/research/projects/arctic-sea-ice-volume-anomaly/data/model_grid\n" + \
              'Save to directory: ' + self.dest_dir + '\n' + \
              'Variables: ' + ', '.join(self.variables) + '\n' + \
              'Years: ' + ', '.join([str(year) for year in self.years]) + '\n' + \
              '************************* End ************************'

        return msg

