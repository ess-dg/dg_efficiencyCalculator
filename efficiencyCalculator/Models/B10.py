
import os
import sys

import numpy


class B10:
    configurations = [2]

    def __init__(self, parent=None):
        self.configurations[0] = {
            'name': '10B4C 2.24g/cm3',
            'alpha06': numpy.loadtxt(fname=os.path.dirname(os.path.abspath(__file__)) + "/../data/B10/IONIZ_Linkoping_Alpha06.txt",unpack=True, skiprows=27),
            'alpha94': numpy.loadtxt(fname=os.path.dirname(os.path.abspath(__file__)) + "/../data/B10/IONIZ_Linkoping_Alpha94.txt",unpack=True, skiprows=27),
            'Li06': numpy.loadtxt(fname=os.path.dirname(os.path.abspath(__file__)) + "/../data/B10/IONIZ_Linkoping_Li06.txt",unpack=True, skiprows=27),
            'Li94': numpy.loadtxt(fname=os.path.dirname(os.path.abspath(__file__)) + "/../data/B10/IONIZ_Linkoping_Alpha06.txt",unpack=True, skiprows=27),
        }



if __name__ == '__main__':
    b = B10()
