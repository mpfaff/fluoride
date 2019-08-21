import setuptools
from distutils.core import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
  name = 'fluoride',
  packages = ['fluoride'],
  version = '0.1.0',
  license='MIT',
  description = 'A Modular and Extensible Logging Framework',
  long_description=long_description,
  long_description_content_type="text/markdown",
  author = 'Michael Pfaff',
  author_email = 'michael@pfaff.dev',
  url = 'https://github.com/NucleusDev/fluoride',
  download_url = 'https://github.com/NucleusDev/fluoride/archive/v0.1.0.tar.gz',
  keywords = ['log', 'logging', 'framework'],
  install_requires=['aenum<3', 'logdna<2'],
  setup_requires=['wheel'],
  classifiers=[
    'Development Status :: 4 - Beta',      # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
    'Intended Audience :: Developers',      # Define that your audience are developers
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',   # Again, pick a license
    'Programming Language :: Python :: 3',      #Specify which pyhton versions that you want to support
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
  ],
)
