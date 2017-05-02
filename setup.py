import os
from setuptools import Extension, setup, find_packages

def read(fname):
        return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(name='SNAKIS',
      packages=['snakis'],
      classifiers=[
          'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
          'Topic :: Games/Entertainment'
      ],
      long_description=read('README.md')
)
