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

from PyPIOMAS import PyPIOMAS

if __name__ == '__main__':

    # Define variables and years to download
    variables = ['aiday', 'hiday']
    years = [2016, 2017, 2018]
    out_dir = '~/Desktop/PIOMAS'

    # Define a downloader
    downloader = PyPIOMAS(out_dir, variables, years)

    # You can view the downloader like this
    print(downloader)

    # Download data
    downloader.download()

    # Unzip data
    downloader.unzip()

    # Convert to NetCDF
    downloader.to_netcdf('/Users/wuh20/Desktop/PIOMAS/PIOMAS.nc')

