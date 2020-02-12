#!/usr/bin/python3

import logging
import json
import pprint
import requests
import sys
import abc


class CloudProvider(abc.ABC):

    def __init__(self, regionGeoInfo, dateFormatFunction):
        self._dateFormatFunction    = dateFormatFunction
        self._regionGeoInfo         = regionGeoInfo
        self._mostRecentUpdate      = None
        self._regions               = None


    @abc.abstractmethod
    def getDataSources(self):
        pass


    @abc.abstractmethod
    def getRegions(self):
        pass
