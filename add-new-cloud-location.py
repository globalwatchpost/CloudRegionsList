#!/usr/bin/python3

import json
import logging
import pprint
import argparse
import os
import sys



def _readRegionFile( regionFile, logger):
    with open( regionFile ) as inputJson:
        jsonContents = json.load(inputJson)

    return jsonContents


def _appendOrCreateJson(args, logger):
    if os.path.exists( args.location_json_file ):
        logger.debug( "JSON file {0} exists, read existing".format(args.location_json_file) )
        cloudRegions = _readRegionFile(args.location_json_file, logger)
    else:
        logger.debug( "JSON file {0} does not exist, create new".format(args.location_json_file) ) 
        cloudRegions = {}

    #logger.debug( "Starting contents:\n{0}".format(json.dumps(cloudRegions, indent=4, sort_keys=True)) )

    if args.cloud_provider not in cloudRegions:
        cloudRegions[args.cloud_provider] = {} 

    if args.provider_cloud_region_name in cloudRegions[args.cloud_provider]:
        logger.critical( "Cloud {0} already has an entry for region name {1}, aborting".format(
            args.cloud_provider, args.provider_cloud_region_name) )
        sys.exit(1)

    logger.debug( "Country code string: {0}".format(args.country_code_list) )

    cloudRegions[args.cloud_provider][args.provider_cloud_region_name] = {
        'city'          : args.city,
        'continent'     : args.continent,
        'geo_region'    : args.geo_region,
        'iso_3166-1'    : json.loads( args.country_code_list ),
        'iso_3166-2'    : json.loads( args.subdivision_code_list )
    }

    if args.notes is not None:
        cloudRegions[args.cloud_provider][args.provider_cloud_region_name][ 'notes' ] = args.notes

    #logger.debug("Updated cloud region contents:\n{0}".format(
    #    json.dumps(cloudRegions, indent=4, sort_keys=True)) )

    with open( args.location_json_file, "w" ) as outputFileHandle:
        json.dump( cloudRegions, outputFileHandle, indent=4, sort_keys=True )


def _getArguments(logger):
    argParser = argparse.ArgumentParser(description="Add new cloud region")
    argParser.add_argument("location_json_file", help="Filename of JSON file to create/add locations to" )
    argParser.add_argument("cloud_provider", choices=[ "AWS", "Azure", "Google_Cloud" ] )
    argParser.add_argument( "provider_cloud_region_name", help='Provider region string, e.g., "me-south-1"' )
    argParser.add_argument( "continent",
        choices=[
            'Africa',
            'Asia',
            'Europe',
            'North America',
            'South America',
            'Antarctica',
            'Australia'
        ],
    )

    argParser.add_argument(
        "geo_region", 
        choices=[ 
            "America-North",
            "America-South",
            "Europe",
            "Africa",
            "Middle_East",
            "Asia-South",
            "Asia-Southeast",
            "Asia-Northeast",
            "Asia-East",
            "Oceania",
        ],
    ),
    argParser.add_argument( "country_code_list",        help='ISO 3166-1 alpha 2 code list, e.g. "[ \"KE\" ]"' )
    argParser.add_argument( "subdivision_code_list",    help='ISO 3166-2 code list, e.g., "[ \"UK-EN\" ]"' )
    argParser.add_argument( "city",                     help='City name, e.g., "Mumbai"' )
    argParser.add_argument( "notes",                    help="Additional info (optional)", nargs='?' )

    return argParser.parse_args()


def _main(logger):
    args = _getArguments(logger)
    _appendOrCreateJson(args, logger)
    print( "Provider {0} region {1} added to {2}".format(
        args.cloud_provider, args.provider_cloud_region_name, args.location_json_file) )


if __name__ == "__main__":
    logging.basicConfig( level = logging.INFO)
    logger = logging.getLogger()
    _main(logger)
