#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# JHunt

# The MIT License
#
# Copyright (c) 2015-2018 Jeremie DECOCK (http://www.jdhp.org)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

# Here is the procedure to submit updates to PyPI
# ===============================================
#
# 1. Register to PyPI:
#
#    $ python3 setup.py register
#
# 2. Upload the source distribution:
#
#    $ python3 setup.py sdist upload

try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup


# SETUP VARIABLES #############################################################

from jhunt import get_version

VERSION = get_version()

AUTHOR_NAME = 'Jeremie DECOCK'
AUTHOR_EMAIL = 'jd.jdhp@gmail.com'

PYPI_PACKAGE_NAME = 'jhunt'
PROJECT_SHORT_DESC = 'A tool to manage job adverts for job seekers'
PROJECT_WEB_SITE_URL = 'https://github.com/jeremiedecock/jhunt'

# See :  http://pypi.python.org/pypi?%3Aaction=list_classifiers
CLASSIFIERS = ['Development Status :: 4 - Beta',
               'License :: OSI Approved :: MIT License',
               'Natural Language :: English',
               'Operating System :: OS Independent',
               'Programming Language :: Python :: 3',
               'Topic :: Documentation']

KEYWORDS = 'job hunter'

# You can either specify manually the list of packages to include in the
# distribution or use "setuptools.find_packages()" to include them
# automatically with a recursive search (from the root directory of the
# project).
PACKAGES = find_packages()
#PACKAGES = ['jhunt']


# The following list contains all dependencies that Python will try to
# install with this project
# E.g. INSTALL_REQUIRES = ['pyserial >= 2.6']
INSTALL_REQUIRES = ['numpy >= 1.13.0',
                    'pandas >= 0.22.0',
                    'matplotlib >= 2.1.2']


# E.g. SCRIPTS = ["examples/pyax12demo"]
SCRIPTS = []


# Entry point can be used to create plugins or to automatically generate
# system commands to call specific functions.
# Syntax: "name_of_the_command_to_make = package.module:function".
# E.g.:
#   ENTRY_POINTS = {
#     'console_scripts': [
#         'pyax12gui = pyax12.gui:run',
#     ],
#   }
ENTRY_POINTS = {
  'gui_scripts': [
      'jhunt = jhunt.qt.main:main',
  ],
}


README_FILE = 'README.rst'

def get_long_description():
    with open(README_FILE, 'r') as fd:
        desc = fd.read()
    return desc


###############################################################################

setup(author=AUTHOR_NAME,
      author_email=AUTHOR_EMAIL,
      maintainer=AUTHOR_NAME,
      maintainer_email=AUTHOR_EMAIL,

      name=PYPI_PACKAGE_NAME,
      description=PROJECT_SHORT_DESC,
      long_description=get_long_description(),
      url=PROJECT_WEB_SITE_URL,
      download_url=PROJECT_WEB_SITE_URL, # Where the package can be downloaded

      classifiers=CLASSIFIERS,
      #license='MIT',            # Useless if license is already in CLASSIFIERS
      keywords=KEYWORDS,

      packages=PACKAGES,
      include_package_data=True, # Use the MANIFEST.in file

      install_requires=INSTALL_REQUIRES,
      #platforms=['Linux'],
      #requires=[],

      scripts=SCRIPTS,
      entry_points=ENTRY_POINTS,

      version=VERSION)
