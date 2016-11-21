
import os
import sys
import math
import numpy as np
from bisect import bisect_left

class B10:
    configurations = {}

    def __init__(self, parent=None):
        self.configurations = {'10B4C 2.24g/cm3': {
            'alpha06': np.loadtxt(fname=os.path.dirname(os.path.abspath(__file__)) + "/../data/B10/IONIZ_Linkoping_Alpha06.txt",unpack=True, skiprows=27),
            'alpha94': np.loadtxt(fname=os.path.dirname(os.path.abspath(__file__)) + "/../data/B10/IONIZ_Linkoping_Alpha94.txt",unpack=True, skiprows=27),
            'Li06': np.loadtxt(fname=os.path.dirname(os.path.abspath(__file__)) + "/../data/B10/IONIZ_Linkoping_Li06.txt",unpack=True, skiprows=27),
            'Li94': np.loadtxt(fname=os.path.dirname(os.path.abspath(__file__)) + "/../data/B10/IONIZ_Linkoping_Li94.txt",unpack=True, skiprows=27),
        }, '10B4C 2.4g/cm3': {

        }
        }

    #
    def ranges(self, threshold, name):
        """calculates range of 4 particles given a threshold and configuration of B10.

        Args:
            threshold (int):  Threshold in KeV.
            name (String):  Name of the configuration of B10. Example: '10B4C 2.24g/cm3'
        Returns:
            r[1,4]: r(1,1)=ralpha_94;
                 r(1,2)=rLi_94;
                 r(1,3)=ralpha_06;
                 r(1,4)=rLi_06;

            ranges in um

        ..  Original source in Matlab: https: // bitbucket.org / europeanspallationsource / dg_matlabborontools / src / bcbac538ad10d074c5150a228847efc2e0269e0d / B10tools / rangesMAT.m?at = default & fileviewer = file - view - default

        """
        if threshold < 2:
            threshold = 2
            print 'Threshold set to 2 keV, no lower Th. accepted!'

        if threshold > 779:
            threshold = 779
            print('Threshold set to 779 keV, no higher Th. accepted!')

        r = [0,0,0,0]
        threshold *= 1000
        config = self.configurations.get(name)
        Ra94 = findTh(config.get('alpha94'), threshold)
        r[0] = Ra94/10000
        #Esta lista no es la que deberia
        Rli94 = findTh(config.get('Li94'), threshold)
        r[1] = Rli94/10000
        Ralpha06 = findTh(config.get('alpha06'), threshold)
        r[2] = Ralpha06/10000
        Rli06 = findTh(config.get('Li06'), threshold)
        r[3] = Rli06/10000
        return r

def findTh(array, threshold):
    """calculates integral and x value for a y in the integral data matrix

    Args:
        threshold (int):  y point in the integral to find an x.
        array (array[2]):  Array of 2 arrays, [0]contains array of x values, [1] contains array of y values
    Returns:
        thValue: point where y in the integral have the closest value to threshold



    ..  Original source in Matlab: https: // bitbucket.org / europeanspallationsource / dg_matlabborontools / src / bcbac538ad10d074c5150a228847efc2e0269e0d / B10tools / rangesMAT.m?at = default & fileviewer = file - view - default

    """
    x= array[0]
    E1= array[1]
    E3 = []
    c1 = 0
    i = 0
    w = x[1] - x[0]
    c0 = 0
    thValue=0
    thFound= False
    #Total integral value 'i' calculation
    for y in E1:
        if c0 != 0:
            # interpolation of distance from previous point
            # all points seem to be at the same distance!
            w = x[c0] - x[c0 - 1]
        i = i + y * w
        c0 += 1

    for a in x:
        area = 0
        c2 = 0
        c0 = 0
        w = x[1] - x[0]
        for s in range(0, c1):
            if c0 != 0:
                # interpolation of distance from previous point
                w = x[c0] - x[c0 - 1]
            area = area + E1[c2] * w
            c2 += 1
            c0 += 1
        localArea = i - area
        if thFound == False:
            if localArea <= threshold:
                thFound = True
                thValue = x[c2]
        # check if this is the threshold point
        E3.append(localArea)
        c1 += 1
    return thValue



if __name__ == '__main__':
    b = B10()
    b.ranges(200, '10B4C 2.24g/cm3')
