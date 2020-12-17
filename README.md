# PyPIOMAS

<!-- vim-markdown-toc GFM -->

* [Overview](#overview)
* [Installation](#installation)
* [Usage](#usage)
* [Contribution](#contribution)

<!-- vim-markdown-toc -->

## Overview

This package currently supports

1. downloading the [PIOMAS](http://psc.apl.uw.edu/research/projects/arctic-sea-ice-volume-anomaly/data/model_grid) dataset;
2. converting scalar fields with a 2-d grid type to an NetCDF format.

This package is written in Python 3 by [Weiming Hu](https://weiming-hu.github.io/). The implementation is inspired from the following similar projects:

1. [Zack Labe's tools](https://github.com/zmlabe/IceVarFigs/tree/master/Scripts/SeaIce)
2. [Robbie Mallet’s converters](https://github.com/robbiemallett/piomas_bin_reader)

## Installation

There are two ways to install the package:

1. From PyPi: `pip install PyPIOMAS`
2. From GitHub: `pip install git+git://github.com/Weiming-Hu/PyPIOMAS.git`

Installing from GitHub will guarantee the latest version.

## Usage

An example is provided in [Example.py](https://github.com/Weiming-Hu/PyPIOMAS/blob/main/Example.py).

In a nutshell, you start by defining a downloader.

```python
from PyPIOMAS.PyPIOMAS import PyPIOMAS

variables = ['area']
years = [2016, 2017, 2018]
out_dir = '~/Desktop/PIOMAS'

downloader = PyPIOMAS(out_dir, variables, years)
```

You can check your configuration by printing the downloader.

```shell
>>> print(downloader)
*************** PIOMAS Data Downloader ***************
Source: http://psc.apl.uw.edu/research/projects/arctic-sea-ice-volume-anomaly/data/model_grid
Save to directory: /Users/wuh20/Desktop/PIOMAS
Variables: area
Years: 2016, 2017, 2018
************************* End ************************
```

Then, you can download the data. If the data are compressed, you can also unzip them afterwards.

```python
downloader.download()
downloader.unzip()
```

`PyPIOMAS` also provides the functionality to convert the raw data to NetCDF.

```python
downloader.to_netcdf('PIOMAS.nc')
```

Finally, this is what you get.

```shell
% ncdump -h PIOMAS.nc 
netcdf PIOMAS {
dimensions:
	grid = 43200 ;
	year = 3 ;
	month = 12 ;
variables:
	double x(grid) ;
		x:_FillValue = NaN ;
	double y(grid) ;
		y:_FillValue = NaN ;
	int64 year(year) ;
	double area(year, month, grid) ;
		area:_FillValue = NaN ;
		area:long_name = "Monthly sea ice concentration" ;
		area:units = "" ;
		area:coordinates = "x y" ;
}
```

Enjoy your science!

## Contribution

Tickets and pull requests are always welcome!

```
# "`-''-/").___..--''"`-._
#  (`6_ 6  )   `-.  (     ).`-.__.`)   WE ARE ...
#  (_Y_.)'  ._   )  `._ `. ``-..-'    PENN STATE!
#    _ ..`--'_..-_/  /--'_.' ,'
#  (il),-''  (li),'  ((!.-'
# 
# Author: 
#     Weiming Hu <weiming@psu.edu>
#
# Geoinformatics and Earth Observation Laboratory (http://geolab.psu.edu)
# Department of Geography and Institute for Computational and Data Sciences
# The Pennsylvania State University
```

