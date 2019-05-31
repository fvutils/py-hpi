
import os
from setuptools import setup

setup(
  name = "hpi",
  packages=['hpi'],
  package_dir = {'' : 'src'},
  author = "Matthew Ballance",
  author_email = "matt.ballance@gmail.com",
  description = ("pyHPI is an procedural interface between Python and HDL environments."),
  license = "Apache 2.0",
  keywords = ["SystemVerilog", "Verilog", "RTL", "VHDL"],
  url = "https://github.com/fvutils/py-hpi",
  entry_points={
    'console_scripts': [
      'hpi = hpi.__main__:main'
    ]
  },
  setup_requires=[
    'setuptools_scm',
  ],
  install_requires=[
  ],
)

