import setuptools
from distutils.core import setup
setup(
  name = 'fluoride',
  packages = ['fluoride'],
  version = '0.0.0',
  license='MIT',
  description = 'A Modular and Extensible Logging Framework',
  author = 'Michael Pfaff',
  author_email = 'michael@pfaff.dev',
  url = 'https://github.com/NucleusDev/fluoride',
  download_url = 'https://github.com/NucleusDev/fluoride/archive/v0.0.0.tar.gz',
  keywords = ['log', 'logging', 'framework'],
  install_requires=[],
  setup_requires=['wheel'],
  classifiers=[
    'Development Status :: 3 - Alpha',      # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
    'Intended Audience :: Developers',      # Define that your audience are developers
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',   # Again, pick a license
    'Programming Language :: Python :: 3',      #Specify which pyhton versions that you want to support
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
  ],
)
