#!/usr/bin/python3

import logging
import json
import pprint
import sys
import pelican
import pycountry
import datetime
import cloud_provider_aws


class ListCloudRegions(pelican.generators.PagesGenerator):

    def generate_context(self):
        print( "generate_context invoked" )

        with open("../cloud_geographic_locations.json") as inputFile:
            regionInfo = json.load(inputFile)

        #print( "Region info:\n{0}".format(json.dumps(regionInfo, indent=4, sort_keys=True)))

        self.context['cloud_providers'] = {
            'generation_timestamp': formatDate( datetime.datetime.utcnow() ),
            'data_sources': [],
            'regions_by_provider': {}
        }

        self._providerObjects = {
            'AWS': cloud_provider_aws.CloudProviderAws(regionInfo['AWS'], formatDate),
        }

        self._getAwsRegions(regionInfo['AWS'])
        # Azure
        # GCloud

        self._doCountryLookups( regionInfo )

        self._createSortingLists()

        print( "leaving generate_context" )


    def _getAwsRegions(self, regionInfo):
        awsProvider = self._providerObjects['AWS']

        self.context['cloud_providers']['data_sources'].extend( awsProvider.getDataSources() )
        self.context['cloud_providers']['regions_by_provider']['AWS'] = awsProvider.getRegions()


    def _doCountryLookups(self, regionGeoInfo ):
        masterListDisplayNames = {}

        for currProvider in regionGeoInfo:
            for currRegionName in regionGeoInfo[ currProvider ]:
                regionCountryCodes = regionGeoInfo[currProvider][currRegionName]['iso_3166-1']

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

        sortFields = []

        sortingLists = {}
        self._finalizedSortedLists = { 'AWS': {} }

        for currProviderId in self._providerObjects:
            providerObject = self._providerObjects[ currProviderId ]
            sortingLists[ currProviderId ] = providerObject.getSortingOrderings()
            for currSortField in sortingLists[ currProviderId ]:
                if currSortField not in sortFields:
                    sortFields.append( currSortField )


        for currSortField in sortFields:
            self._finalizedSortedLists[ 'AWS' ][ currSortField ] = { 'asc': [], 'desc': [] }

            for sortDirection in ( 'asc', 'desc' ):
                providerLists = {}
                providerListIndexes = {}
                for currProviderId in self._providerObjects:
                    providerLists[ currProviderId ] = sortingLists[ currProviderId ][ currSortField ][ sortDirection ] 
                    providerListIndexes[ currProviderId ] = 0

                print( "Sort field: {0}, sort direction: {1}".format(currSortField, sortDirection) )

                doneWithAllLists = False

                while doneWithAllLists is False:

                    currCandidateEntries = []

                    for currProviderId in self._providerObjects:
                        if providerListIndexes[ currProviderId ] < len(  providerLists[ currProviderId ] ):
                            currCandidateEntries.append( 
                                providerLists[ currProviderId ][ providerListIndexes[ currProviderId ] ][ 'sort_key' ] )

                    # Find min or max value of the candidates based on sort order
                    #print( "\tCandidate values:\n{0}".format(pprint.pformat(currCandidateEntries, indent=4)) )

                    if sortDirection == 'asc':
                        nextSortKey = min( currCandidateEntries )
                    else:
                        nextSortKey = max( currCandidateEntries )

                    print( "Next sort key for combined list: {0}".format( nextSortKey ) )

                    # Find it in the candidate list
                    print( "before find in candidate list" )
                    for currProviderId in self._providerObjects:
                        if providerListIndexes[ currProviderId ] < len( providerLists[ currProviderId ] ):
                            potentialMatch = providerLists[ currProviderId ][ providerListIndexes[ currProviderId ] ]
                            print( "Potential match {0}, looking for one with sort key {1}".format(
                                pprint.pformat(potentialMatch, indent=4), nextSortKey))

                            if potentialMatch['sort_key'] == nextSortKey:
                                self._finalizedSortedLists[ currProviderId ][ currSortField ][ sortDirection ].append(
                                    potentialMatch )
                                providerListIndexes[ currProviderId ] += 1

                    # See if we're done
                    doneWithAllLists = True
                    for currProviderId in self._providerObjects:
                        if providerListIndexes[ currProviderId ] < len(  providerLists[ currProviderId ] ):
                            doneWithAllLists = False
                            break

        print( "Done building finalized lists" )
        print( "Finalized lists:\n{0}".format(json.dumps(self._finalizedSortedLists, indent=4, sort_keys=True) ) )


def formatDate(datetimeField):
    return datetimeField.strftime("%Y-%m-%d %H:%M:%S")  


def getListCloudRegionsGenerator( pelicanHandle ):
    print( "List Cloud Regions plugin, requested to return an instance of a generator class" )
    return ListCloudRegions


def register():
    pelican.signals.get_generators.connect( getListCloudRegionsGenerator )
