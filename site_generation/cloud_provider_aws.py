#!/usr/bin/python3

import boto3
import botocore
import logging
import json
import pprint
import requests
import sys


class CloudProviderAws:

    def __init__(self, regionGeoInfo, dateFormatFunction):
        self._ec2Region             = self._getEc2Region()
        self._dateFormatFunction    = dateFormatFunction
        self._regionGeoInfo         = regionGeoInfo
        self._mostRecentUpdate      = None
        self._regions               = None
        self._sortingOrderings      = None


    def getDataSources(self):
        logging.info( "Inside getDataSources" )
        if self._mostRecentUpdate is None:
            self.getRegions()

        return [
            {
                'description': '<a href="https://aws.amazon.com/blogs/aws/new-query-for-aws-regions-endpoints-and-more-using-aws-systems-manager-parameter-store/">AWS Systems Manager Parameter Store</a>',
                'updated_timestamp': self._dateFormatFunction( self._mostRecentUpdate )
            },
        ]


    def getRegions(self):
        logging.info( "Inside getRegions" )
        if self._regions is not None:
            return self._regions
            
        try:
            awsSsmClient = boto3.client( 'ssm', region_name=self._ec2Region )
        except e:
            logging.critical( "Exception thrown when trying to establish SSM client connection, error: {0}".format(e) )
            sys.exit(1)

        try:
            regionQueryPath = "/aws/service/global-infrastructure/regions"

            moreResults = True
            queryToken = None
            regionList = []

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
                    if self._mostRecentUpdate is None:
                        self._mostRecentUpdate = currParam['LastModifiedDate']
                    else:
                        if currParam['LastModifiedDate'] > self._mostRecentUpdate:
                            self._mostRecentUpdate = currParam['LastModifiedDate']

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

        self._regions = {}

        for currRegionName in regionList:
            #logging.info("working {0}".format(currRegionName))
            #print("region Geo info:\n{0}".format(self._regionGeoInfo))
            self._regions[ currRegionName ] = self._regionGeoInfo[currRegionName]


        logging.info( "Leaving getRegions" )

        return self._regions


    def getSortingOrderings(self):
        print( "Inside getSortingOrderings" )

        # Populate data if needed
        if self._sortingOrderings is not None:
            return self._sortingOrderings

        if self._regions is None:
            self.getRegions()

        sortingKeyArrays = {}
        for currRegionId in self._regions:
            for sortKeyField in ( 'cloud_region', 'geo_region', 'continent', 'country', 'city' ):
                currRegionDetails = self._regions[ currRegionId ]

                if sortKeyField not in sortingKeyArrays:
                    sortingKeyArrays[sortKeyField] = {}

                currSortingKeyArray = sortingKeyArrays[sortKeyField]

                if sortKeyField == 'cloud_region':
                    sortKey = "AWS:{0}".format(currRegionId)
                elif sortKeyField == 'geo_region':
                    sortKey = "{0}-AWS:{1}".format(currRegionDetails['geo_region'], currRegionId)
                elif sortKeyField == 'continent':
                    sortKey = "{0}-AWS:{1}".format(currRegionDetails['continent'], currRegionId)
                elif sortKeyField == 'country':
                    sortKey = "{0}-AWS:{1}".format(','.join(currRegionDetails[ 'display_countries' ]), currRegionId)
                elif sortKeyField == 'city':
                    sortKey = "{0}-AWS:{1}".format(currRegionDetails[ 'city' ], currRegionId)
                else:
                    raise Exception("Unknown sort key field: {0}".format(sortKeyField))

                currSortingKeyArray[ sortKey ] = currRegionId

        

        print( "Sorting key arrays:\n{0}".format(pprint.pformat(sortingKeyArrays, indent=4)))

        self._sortingOrderings = {}

        for currField in ('cloud_region', 'geo_region', 'continent', 'country', 'city' ):
            for sortDirection in ( 'asc', 'desc' ):
                if currField not in self._sortingOrderings:
                    self._sortingOrderings[ currField ] = {
                        'asc': [],
                        'desc': []
                    }

                for currSortKey in sorted( sortingKeyArrays[ currField ].keys() ):
                    self._sortingOrderings[ currField ][ sortDirection ].append( 
                        { 
                            'sort_key'          : currSortKey,
                            'cloud_provider'    : 'AWS',
                            'region_name'       : sortingKeyArrays[ currField ][ currSortKey ] 
                        }
                    )


            self._sortingOrderings[ currField ][ 'desc' ].reverse()

        print( "Sorting orderings:\n{0}".format(json.dumps(self._sortingOrderings, indent=4, sort_keys=True)))

        return self._sortingOrderings


    def _getEc2Region(self):
        requestResult = requests.get( 'http://169.254.169.254/latest/dynamic/instance-identity/document' )
        #logger.debug( "Back from requests.get" )
        jsonDocument = requestResult.json()
        awsRegion = jsonDocument['region']
        logging.info( "Script running in AWS region {0}".format(awsRegion) )

        return awsRegion
