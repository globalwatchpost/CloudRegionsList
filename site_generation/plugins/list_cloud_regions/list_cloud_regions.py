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
            'generation_timestamp': self.formatDate( datetime.datetime.utcnow() ),
            'country_codes': {}
        }


        self._getAwsRegions(regionInfo['aws'])
        # Azure
        # GCloud

        #self._doCountryLookups()

        print( "leaving generate_context" )


    def _getAwsRegions(self, regionInfo):
        awsRegions = cloud_provider_aws.CloudProviderAws(self.formatDate)

        self.context['cloud_providers']['aws'] = awsRegions.getRegions(regionInfo)


    def _doCountryLookups(self):
        countryDisplayNames = []
        countryCodes = regionInfo['aws'][currRegionName]['iso_3166-1']
        for countryCode in countryCodes:
            if countryCode in countryLookups:
                countryLookup = countryLookups[countryCode]
            else:
                countryLookup = pycountry.countries.get(alpha_2=countryCode)
                countryLookups[countryCode] = countryLookup

            if countryLookup is not None:
                #print( "Country code {0} converted to {1}".format(countryCode, countryLookup.name))

                # If name has comma in it, such as "Korea, Republic of", strip everything to right of comma
                displayName = countryLookup.name
                if ',' in displayName:
                    displayName = displayName[:displayName.find(',')]
                countryDisplayNames.append(displayName)
                #print( "Full deets:\n{0}".format(pprint.pformat(countryLookup)))
            else:
                print( "Did not find entry for country code {0}".format(countryCode))

        countryDisplayNames.sort()


    def formatDate(self, datetimeField):
        return datetimeField.strftime("%Y-%m-%d %H:%M:%S")  



def getListCloudRegionsGenerator( pelicanHandle ):
    print( "List Cloud Regions plugin, requested to return an instance of a generator class" )
    return ListCloudRegions


def register():
    pelican.signals.get_generators.connect( getListCloudRegionsGenerator )
