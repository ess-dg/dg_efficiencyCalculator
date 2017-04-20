"""
This is a setup.py script generated by py2applet

Usage:
    python setup.py py2app
"""

from setuptools import setup

APP = ['launch.py']
DATA_FILES = []
OPTIONS = {'argv_emulation': True, 'includes': ['sip', 'PyQt4._qt']}

setup(
    name='Neutron detector efficiency calculator',
    version="0.0.1",
    app=APP,
    author='Alvaro Carmona',
    author_email='acarmona@opendeusto.es',
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    license="BSD",
    setup_requires=['py2app'],
    packages=['efficiencyCalculator',],
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: BSD License",
    ],

)

0