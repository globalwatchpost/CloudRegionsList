#!/usr/bin/python3

import logging
import json
import pprint
import sys
import cloudprovider
import subprocess


class CloudProviderAzure(cloudprovider.CloudProvider):

    def __init__(self, regionGeoInfo, dateFormatFunction):
        super().__init__( regionGeoInfo, dateFormatFunction )


    def getDataSources(self):
        logging.info( "Inside getDataSources" )

        

        if self._mostRecentUpdate is None:
            updatedTimestamp = "(N/A)"
        else:
            updatedTimestamp = self._dateFormatFunction( self._mostRecentUpdate )

        return [
            {
                'description'       : "Azure API info",
                'updated_timestamp' : updatedTimestamp
            },
        ]


    def getRegions(self):
        if self._regions is not None:
            return self._regions

        runHandle = subprocess.run( [ "az", "account", "list-locations" ], stdout=subprocess.PIPE )
        #print( "Azure getRegions CLI run:\n{0}".format(runHandle.stdout) )
        azureCliRegionList = json.loads( runHandle.stdout )

        #print( "Azure regions:\n{0}".format(json.dumps(regionInfo, indent=4, sort_keys=True)) )
        regionsInCliOutput = []

        self._regions = {}
        for cliRegionInfo in azureCliRegionList:
            regionName = cliRegionInfo['displayName']
            logging.debug( "Found region name: {0}".format(regionName) )

            if regionName in self._regionGeoInfo:
                self._regions[ regionName ] = self._regionGeoInfo[ regionName ]
            else:
                self._regions[ regionName ] = {
                    "city"          : "???",
                    "continent"     : "???",
                    "geo_region"    : "???",
                    "iso_3166-1"    : [ "???" ],
                    "iso_3166-2"    : [ "???" ]
                }

        # doublecheck against our JSON list, add any that our account can't see
        for providerRegionId in self._regionGeoInfo:
            if providerRegionId not in self._regions:
                self._regions[ providerRegionId ] = self._regionGeoInfo[ providerRegionId ]
                logging.info( "Added in region {0} from JSON, not found in CLI results".format(providerRegionId) )

        return self._regions
