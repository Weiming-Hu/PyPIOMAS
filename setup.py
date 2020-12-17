import setuptools

setuptools.setup(
    name='PyPIOMAS',
    version='0.1.2',
    author='Weiming Hu',
    author_email='weiming@psu.edu',
    url='https://github.com/Weiming-Hu/PyPIOMAS',
    packages=['PyPIOMAS'],
    license='LICENSE',
    description='A package for downloading and converting the PIOMAS dataset',
    install_requires=[
        'numpy',
        'xarray',
    ],
)

