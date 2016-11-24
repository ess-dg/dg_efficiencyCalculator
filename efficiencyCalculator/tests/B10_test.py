
from efficiencyCalculator.Models import B10
import numpy


class B10_test:

    def __init__(self):
        self.b = B10.B10()

    def configurations_test(self):
        assert len(self.b.configurations) == 1
        conf = self.b.configurations.get('10B4C 2.24g/cm3')
        assert len(conf) == 4

    def ranges_test(self):
        r1 = self.b.ranges(200, '10B4C 2.24g/cm3')
        r2 = self.b.ranges(100, '10B4C 2.24g/cm3')
        assert r1[0] == 2.8
        assert r1[1] == 1.1
        assert r1[2] == 3.7
        assert r1[3] == 1.3

        assert r2[0] == 3.1
        assert r2[1] == 1.35
        assert r2[2] == 4.0
        assert r2[3] == 1.6

    def get_th_test(self):
        config = self.b.configurations.get('10B4C 2.24g/cm3')
        assert B10.find_th(config.get('alpha94'), 200000) == 28000.0
        assert B10.find_th(config.get('Li94'), 200000) == 11000.0
        assert B10.find_th(config.get('alpha06'), 200000) == 37000.0
        assert B10.find_th(config.get('Li06'), 200000) == 13000.0

    def read_cross_section_test(self):
        # to test floats I need an aproximation given by numpy :/
        assert numpy.isclose(self.b.read_cross_section([1.8])[0], [3844.3852472], rtol=1e-05, atol=1e-08, equal_nan=False)

    def macro_sigma_test(self):
        assert numpy.isclose(self.b.macro_sigma(3844.3852472), [0.0398457257908], rtol=1e-05, atol=1e-08, equal_nan=False)

    def sigma_eq_test(self):
        sigmaeq = self.b.sigma_eq(0.0398457257908, 90)
        assert numpy.isclose([sigmaeq],  [0.0398457257908], rtol=1e-05, atol=1e-08, equal_nan=False)
        sigmaeq = self.b.sigma_eq(0.0398457257908, 5)
        assert numpy.isclose([sigmaeq], [0.457178431789], rtol=1e-05, atol=1e-08, equal_nan=False)

    def full_sigma_calculation_test(self):
        sigma = self.b.full_sigma_calculation([1.8], 90)
        assert numpy.isclose([sigma], [0.0398457257908], rtol=1e-05, atol=1e-08, equal_nan=False)
        sigma = self.b.full_sigma_calculation([2], 3)
        assert numpy.isclose([sigma], [0.845952315849], rtol=1e-05, atol=1e-08, equal_nan=False)