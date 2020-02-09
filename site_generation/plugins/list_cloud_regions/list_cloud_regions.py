#!/usr/bin/python3

import boto3
import botocore
import logging
import json
import pprint
import requests
import sys
import pelican
import pycountry
import datetime


class AwsRegionsGenerator(pelican.generators.PagesGenerator):

    def generate_context(self):
        #print( "generate_context invoked" )

        with open("../cloud_geographic_locations.json") as inputFile:
            regionInfo = json.load(inputFile)

        #print( "Region info:\n{0}".format(json.dumps(regionInfo, indent=4, sort_keys=True)))

        awsRegion = self._getEc2Region()
        try:
            awsSsmClient = boto3.client( 'ssm', region_name=awsRegion )
        except e:
            logging.critical( "Exception thrown when trying to establish SSM client connection, error: {0}".format(e) )
            sys.exit(1)

        try:
            regionQueryPath = "/aws/service/global-infrastructure/regions"

            moreResults = True
            queryToken = None
            regionList = []
            mostRecentUpdate = None

            while moreResults is True:
                if queryToken is None:
                    #logging.debug("Getting params with no token")
                    ssmResults = awsSsmClient.get_parameters_by_path( Path=regionQueryPath )
                else:
                    #logging.debug( "Getting params with token {0}".format(queryToken) )
                    ssmResults = awsSsmClient.get_parameters_by_path( Path=regionQueryPath, NextToken=queryToken )

                resultParams = ssmResults['Parameters']

                for currParam in resultParams:
                    regionList.append( currParam['Value'] )
                    #print( "Param data for {0}:\n{1}".format(currParam['Value'], pprint.pformat(currParam, indent=4)))
                    if mostRecentUpdate is None:
                        mostRecentUpdate = currParam['LastModifiedDate']
                    else:
                        if currParam['LastModifiedDate'] > mostRecentUpdate:
                            mostRecentUpdate = currParam['LastModifiedDate']

                if 'NextToken' in ssmResults and len(ssmResults['NextToken']) > 0:
                    moreResults = True
                    queryToken = ssmResults['NextToken']
                else:
                    moreResults = False
                    queryToken = None

        except botocore.exceptions.ClientError as e:
            logging.error("Error when requesting regions list: {0}".format(e) )
            sys.exit(1)

 
        regionList.sort()

        self.context['cloud_providers'] = {
            'aws': {
                'data_source': '<a href="https://aws.amazon.com/blogs/aws/new-query-for-aws-regions-endpoints-and-more-using-aws-systems-manager-parameter-store/">AWS Systems Manager Parameter Store</a>',
                'regions': { }
            }
        }

        self.context['generation_timestamp'] = self._formatDate( datetime.datetime.utcnow() )
        self.context['data_last_updated_timestamp'] = self._formatDate( mostRecentUpdate )
            

        countryLookups = {}

        for currRegionName in regionList:
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
            regionInfo['aws'][currRegionName]['country_display_names'] = countryDisplayNames
            self.context['cloud_providers']['aws']['regions'][ currRegionName] = regionInfo['aws'][currRegionName]



        #pprint.pprint(self.context['cloud_providers'])


    def _formatDate(self, datetimeField):
        return datetimeField.strftime("%Y-%m-%d %H:%M:%S")  


    def _getEc2Region(self):
        requestResult = requests.get( 'http://169.254.169.254/latest/dynamic/instance-identity/document' )
        #logger.debug( "Back from requests.get" )
        jsonDocument = requestResult.json()
        awsRegion = jsonDocument['region']
        logging.info( "Script running in AWS region {0}".format(awsRegion) )

        return awsRegion



def getAwsRegionsGenerator( pelicanHandle ):
    print( "AWS plugin, requested to return an instance of a generator class" )
    return AwsRegionsGenerator

def register():
    #pelican.signals.initialized.connect( pluginInitialized ) 
    pelican.signals.get_generators.connect( getAwsRegionsGenerator )


