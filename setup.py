#
# Basic setup file for pip install
#

import os
import sys
from setuptools import setup, find_packages

#example_files = ['examples/%s' %file for file in os.listdir('examples') if os.path.isfile('examples/%s' %file) ]

setup(
    name="htcondor-mkmaps",
    version='0.90',
    description='Python Libraries for handling condor job attributes.',
    long_description='''Python Libraries for handling condor job attributes.''',
    license='BSD',
    author='John Hover',
    author_email='jhover@bnl.gov',
    url='https://github.com/bnl-sdcc/htcondor-mkmaps',
    #python_requires='>=2.7',
    packages=[ 'mkmaps',
               ],
    install_requires=[],
    
    data_files=[ ('/etc/condor/', ['etc/condor/mkmaps.conf']),
                 ('/etc/cron.d/', ['etc/mkmaps.cron']),              
        ],
    )


