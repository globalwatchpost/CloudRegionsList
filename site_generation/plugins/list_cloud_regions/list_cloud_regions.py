#!/usr/bin/python3

import logging
import json
import pprint
import sys
import pelican
import pycountry
import datetime
import cloudprovider_aws
import cloudprovider_azure
import cloudprovider_google
import itertools
import copy


class ListCloudRegions(pelican.generators.PagesGenerator):

    def generate_context(self):
        print( "generate_context invoked" )

        with open("../cloud_geographic_locations.json") as inputFile:
            regionInfo = json.load(inputFile)

        #print( "Region info:\n{0}".format(json.dumps(regionInfo, indent=4, sort_keys=True)))

        self.context['cloud_providers'] = {
            'generation_timestamp'  : formatDate( datetime.datetime.utcnow() ),
            'data_sources'          : [],
            'regions_by_provider'   : {},
            'sorted_display_lists'  : {}
        }

        self._providerObjects = {
            'AWS'           : cloudprovider_aws.CloudProviderAws( regionInfo['AWS'], formatDate),
            'Azure'         : cloudprovider_azure.CloudProviderAzure( regionInfo['Azure'], formatDate),
            'Google_Cloud'  : cloudprovider_google.CloudProviderGoogle( regionInfo[ 'Google_Cloud' ], formatDate ),
        }

        self._populateProviderRegionContext()

        self._doCountryLookups()

        # Finally, create the context entry that is the big JSON string that will be injected directly
        #       into the JSON
        self._createJson()

        #self._createSortingLists()

        print( "leaving generate_context" )


    def _populateProviderRegionContext(self):
        for currProviderId in self._providerObjects:
            logging.info("Creating region context for provider {0}".format(currProviderId) )
            currProvider = self._providerObjects[ currProviderId ]

            self.context['cloud_providers']['data_sources'].extend( currProvider.getDataSources() )
            self.context['cloud_providers']['regions_by_provider'][ currProviderId ] = currProvider.getRegions()


    def _doCountryLookups( self ):
        masterListDisplayNames = {}

        for currProvider in self.context['cloud_providers']['regions_by_provider']:
            for currRegionName in self.context['cloud_providers']['regions_by_provider'][ currProvider ]:
                regionCountryCodes = self.context['cloud_providers']['regions_by_provider']\
                    [currProvider][currRegionName]['iso_3166-1']

                self.context['cloud_providers']['regions_by_provider'][ currProvider ][ currRegionName ]\
                    [ 'display_countries' ] = []

                regionDisplayCountries = self.context['cloud_providers']['regions_by_provider'][ currProvider ]\
                    [ currRegionName ][ 'display_countries' ]

                for regionCountryCode in regionCountryCodes:
                    displayName = None 
                    if regionCountryCode in masterListDisplayNames:
                        displayName = masterListDisplayNames[ regionCountryCode ] 
                    else:
                        countryLookup = pycountry.countries.get(alpha_2=regionCountryCode)

                        if countryLookup is not None:
                            #print( "Country code {0} converted to {1}".format(regionCountryCode, countryLookup.name))

                            # If name has comma in it, such as "Korea, Republic of", strip everything to right of comma
                            displayName = countryLookup.name
                            if ',' in displayName:
                                displayName = displayName[:displayName.find(',')]
                            #print( "Full deets:\n{0}".format(pprint.pformat(countryLookup)))
                        else:
                            print( "Did not find entry for country code {0}".format(regionCountryCode))

                    # Store human-readable, sorted list of display country names for easy lookup
                    if displayName is not None:
                        masterListDisplayNames[ regionCountryCode ] = displayName
                        regionDisplayCountries.append( displayName )

                # sort the display list of countries for this region 
                regionDisplayCountries.sort()

    def _createJson(self):
        outputRows = []
        for currProvider in self.context['cloud_providers']['regions_by_provider']:
            for currRegion in self.context['cloud_providers']['regions_by_provider'][currProvider]:
                self.context['cloud_providers']['regions_by_provider'][currProvider][currRegion]['provider'] = currProvider
                self.context['cloud_providers']['regions_by_provider'][currProvider][currRegion]['region_name'] = currRegion

                outputRows.append( self.context['cloud_providers']['regions_by_provider'][currProvider][ currRegion ] )

        #print( "Output rows:\n{0}".format(json.dumps(outputRows, indent=4, sort_keys=True)) )
        self.context[ 'json_table_rows' ] = json.dumps( outputRows ) 


def formatDate(datetimeField):
    return datetimeField.strftime("%Y-%m-%d %H:%M:%S")  


def getListCloudRegionsGenerator( pelicanHandle ):
    print( "List Cloud Regions plugin, requested to return an instance of a generator class" )
    return ListCloudRegions


def register():
    pelican.signals.get_generators.connect( getListCloudRegionsGenerator )
