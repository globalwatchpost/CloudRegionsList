#ws
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


        self._getAwsRegions(regionInfo['AWS'])
        # Azure
        # GCloud

        self._doCountryLookups( regionInfo )

        print( "leaving generate_context" )


    def _getAwsRegions(self, regionInfo):
        awsProvider = cloud_provider_aws.CloudProviderAws(regionInfo, formatDate)

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


def formatDate(datetimeField):
    return datetimeField.strftime("%Y-%m-%d %H:%M:%S")  


def getListCloudRegionsGenerator( pelicanHandle ):
    print( "List Cloud Regions plugin, requested to return an instance of a generator class" )
    return ListCloudRegions


def register():
    pelican.signals.get_generators.connect( getListCloudRegionsGenerator )
