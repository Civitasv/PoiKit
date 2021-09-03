# -- coding: utf-8 --

# test: python -m unittest tests/test_sample.py

from .context import poikit
import unittest
import geopandas


class AdvancedTestSuite(unittest.TestCase):
    """Advanced test cases."""

    def test_thoughts(self):
        assert True

    def test_shape(self):
        test = geopandas.GeoDataFrame.from_file(
            'test.shp', encoding='utf-8')
        test.plot()


if __name__ == '__main__':
    unittest.main()
