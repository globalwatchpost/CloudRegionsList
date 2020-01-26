#!/usr/bin/python3

import boto3
import botocore
import logging
import json
import pprint
import requests
import sys


def _main():
    logger = logging.getLogger("cloudlist") 
    _quietDownLoggers()
    cloudLocations = _getCloudLocations(logger)


def _quietDownLoggers():
    overlyChattyLoggers = ( 'urllib3', 'botocore' )

    for currLogger in overlyChattyLoggers:
        logging.getLogger(currLogger).setLevel(logging.WARN)


def _getCloudLocations(logger):
    locations = {
        'aws': _getAwsLocations(logger)
    }


def _getAwsLocations(logger):
    awsRegions = _getAwsRegions(logger)

def _getAwsRegions(logger):
    awsRegion = _getEc2Region(logger)
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

        while moreResults is True:
            if queryToken is None:
                #logger.debug("Getting params with no token")
                ssmResults = awsSsmClient.get_parameters_by_path( Path=regionQueryPath )
            else:
                #logger.debug( "Getting params with token {0}".format(queryToken) )
                ssmResults = awsSsmClient.get_parameters_by_path( Path=regionQueryPath, NextToken=queryToken )

            resultParams = ssmResults['Parameters']

            for currParam in resultParams:
                regionList.append( currParam['Value'] )

            if 'NextToken' in ssmResults and len(ssmResults['NextToken']) > 0:
                moreResults = True
                queryToken = ssmResults['NextToken']
            else:
                moreResults = False
                queryToken = None

            #logger.debug( "Region list now: {0}".format(pprint.pformat(regionList)))
            #logger.debug( "More results: {0}".format(moreResults))
            #logger.debug( "Token: {0}".format(queryToken) )


    except botocore.exceptions.ClientError as e:
        logger.error("Error when requesting regions list: {0}".format(e) )
        sys.exit(1)

    regionList.sort()
    
    #logger.debug("Full region list ({0} entries): {1}".format(len(regionList), pprint.pformat(regionList)))

    return regionList


def _getEc2Region(logger):
    requestResult = requests.get( 'http://169.254.169.254/latest/dynamic/instance-identity/document' )
    #logger.debug( "Back from requests.get" )
    jsonDocument = requestResult.json()
    awsRegion = jsonDocument['region']
    logger.info( "Script running in AWS region {0}".format(awsRegion) )

    return awsRegion
 

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    _main()
