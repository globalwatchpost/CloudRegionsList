#!/usr/bin/python3

import logging
import json
import pprint
import sys
import cloudprovider
import subprocess


class CloudProviderGoogle(cloudprovider.CloudProvider):

    def __init__(self, regionGeoInfo, dateFormatFunction):
        super().__init__( regionGeoInfo, dateFormatFunction )


    def getDataSources(self):
        #logging.info( "Inside getDataSources" )

        if self._mostRecentUpdate is None:
            updatedTimestamp = "(N/A)"
        else:
            updatedTimestamp = self._dateFormatFunction( self._mostRecentUpdate )

        return [
            {
                'description'       : "Google Cloud API info",
                'updated_timestamp' : updatedTimestamp
            },
        ]


    def getRegions(self):
        if self._regions is not None:
            return self._regions

        self._regions = {}

        # doublecheck against our JSON list, add any that our account can't see
        for providerRegionId in self._regionGeoInfo:
            if providerRegionId not in self._regions:
                self._regions[ providerRegionId ] = self._regionGeoInfo[ providerRegionId ]
                logging.info( "Added in region {0} from JSON, not found in CLI results".format(providerRegionId) )

        return self._regions
