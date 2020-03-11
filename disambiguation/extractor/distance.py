# Author: Arjun Menon <amm8987@psu.edu>

"""
This script contains the definition for a function that calculates
the distance between a pair of long|lat datapoints.
"""

from math import radians, sin, cos, asin, sqrt


class DistanceMeasure:
    def __init__(self, long_lat1, long_lat2):
        self.long_lat1 = long_lat1
        self.long_lat2 = long_lat2

    def haversine(self):
        long1, lat1 = map(float, self.long_lat1.split('|'))
        long2, lat2 = map(float, self.long_lat2.split('|'))
        long1, lat1, lon2, lat2 = map(radians, [long1, lat1, long2, lat2])
        dlon = lon2 - long1
        dlat = lat2 - lat1
        a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
        return 2 * 6371 * asin(sqrt(a))
