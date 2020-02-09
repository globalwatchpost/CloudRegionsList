#!/usr/bin/python3

import boto3
import botocore
import logging
import json
import pprint
import requests
import sys


class CloudProviderAws:

    def __init__(self, dateFormatFunction):
        self._ec2Region             = self._getEc2Region()
        self._dateFormatFunction    = dateFormatFunction


    def getRegions(self, regionInfo):
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

        retVal = {
            'data_source': {
                'description': '<a href="https://aws.amazon.com/blogs/aws/new-query-for-aws-regions-endpoints-and-more-using-aws-systems-manager-parameter-store/">AWS Systems Manager Parameter Store</a>',
                'updated_timestamp': self._dateFormatFunction( mostRecentUpdate )
            },
            'regions': { }
        }

        for currRegionName in regionList:
            retVal['regions'][ currRegionName] = regionInfo[currRegionName]

        return retVal


    def _getEc2Region(self):
        requestResult = requests.get( 'http://169.254.169.254/latest/dynamic/instance-identity/document' )
        #logger.debug( "Back from requests.get" )
        jsonDocument = requestResult.json()
        awsRegion = jsonDocument['region']
        logging.info( "Script running in AWS region {0}".format(awsRegion) )

        return awsRegion
