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
            #'Google Cloud' : None
        }

        self._populateProviderRegionContext()

        self._doCountryLookups()

        self._createSortingLists()

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


    def _createSortingLists(self):
        print( "Starting sorting lists" )

        providerCombinations = []

        # Create combinations for all lengths of all cloud providers
        for currProviderCombinationLength in range( 1, len(self._providerObjects) + 1 ):
            providerCombinations.extend( itertools.combinations(self._providerObjects, currProviderCombinationLength) )


        #print( "Provider combinations:\n{0}".format(pprint.pformat(providerCombinations, indent=4)) )

        for currProviderFilter in providerCombinations:
            for currSortField in self._getSortFields():
                for currSortDirection in ( 'asc', 'desc' ):
                    tempWorkingList = []

                    for currProvider in currProviderFilter:
                        providerRegions = self._providerObjects[currProvider].getRegions()
                        for currProviderRegionId in providerRegions:
                            tempWorkingList.append( 
                                { 
                                    'sort_key'      : self._getSortKey( currSortField, currProvider, currProviderRegionId,
                                        providerRegions[ currProviderRegionId ] ),
                                    'provider'      : currProvider,
                                    'region_name'   : currProviderRegionId
                                }
                            )

                    tempWorkingList = self._sortTempWorkingList( tempWorkingList, currSortDirection )
                    #print( "Working list:\n{0}".format(json.dumps(tempWorkingList, indent=4, sort_keys=True)))


                    # Add values to master sorted list
                    masterSortedListKey = "{0}/{1}/{2}".format(
                        '-'.join(currProviderFilter),
                        currSortField,
                        currSortDirection) 
                    self.context['cloud_providers']['sorted_display_lists'][ masterSortedListKey ] = []

                    for currEntry in tempWorkingList:
                        masterListEntry = copy.deepcopy( self.context['cloud_providers']['regions_by_provider' ]\
                            [ currEntry[ 'provider'] ][ currEntry[ 'region_name' ] ] )
                        masterListEntry[ 'cloud_provider' ] = currEntry[ 'provider' ]
                        masterListEntry[ 'cloud_region' ] = currEntry[ 'region_name' ]

                        self.context['cloud_providers']['sorted_display_lists'][ masterSortedListKey ].append( 
                            masterListEntry )


                    #print( "Master sorted list: {0}, entries:\n{1}".format(
                    #    masterSortedListKey, json.dumps(
                    #        self.context['cloud_providers']['sorted_display_lists'][ masterSortedListKey ],
                    #        indent=4, sort_keys=True)) )


    def _getSortFields(self):
        return (
            'cloud_region',
            'geo_region',
            'continent',
            'display_countries',
            'city'
        )
        

    def _getSortKey( self, sortField, provider, providerRegionId, regionObject ):
        if sortField == 'display_countries':
            if 'display_countries' not in regionObject:
                print( "Could not find display_countries in {0}/{1}".format(provider, providerRegionId) )
                sortValue = "???"
            else:
                sortValue = ', '.join( regionObject[ sortField ] )
        elif sortField == 'cloud_region':
            sortValue = providerRegionId
        else:
            sortValue = regionObject[ sortField ]

        return "sort_field:{0}:sort_value:{1}:provider:{2}:region:{3}".format(
            sortField, sortValue, provider, providerRegionId).lower()


    def _sortTempWorkingList( self, tempWorkingList, currSortDirection ):
        if currSortDirection == 'desc':
            sortReverse = True
        else:
            sortReverse = False
        #print( "Sort reverse: {0}".format(sortReverse) )
        return sorted( tempWorkingList, key = lambda i: i[ 'sort_key' ], reverse=sortReverse ) 



def formatDate(datetimeField):
    return datetimeField.strftime("%Y-%m-%d %H:%M:%S")  


def getListCloudRegionsGenerator( pelicanHandle ):
    print( "List Cloud Regions plugin, requested to return an instance of a generator class" )
    return ListCloudRegions


def register():
    pelican.signals.get_generators.connect( getListCloudRegionsGenerator )
