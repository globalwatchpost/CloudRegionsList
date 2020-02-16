#!/usr/bin/python3

import itertools
import datetime
import pprint

def _main():
    providerCombinations = _getProviderCombinations()       

    sortFieldMap = _getSortFields()



    for currProviderCombo in providerCombinations:
        #print( "Combination: {0}".format( ",".join(currProviderCombo)) )
        for sortfieldKey in sortFieldMap:
            for sortDirection in ( 'asc', 'desc' ):

                columnImageMetadata = []
                columnLinkMetadata = []

                for columnName in sortFieldMap:
                    if columnName == sortfieldKey:
                        columnImageMetadata.append( "Column_image_{0}: sort_icon_{1}.svg".format(
                            columnName, sortDirection) )

                        if sortDirection == "asc":
                            columnLinkMetadata.append( "Column_link_{0}: /{1}/{2}/desc.html".format(
                                columnName,
                                "-".join(currProviderCombo).replace( " ", "_" ),
                                sortFieldMap[ columnName ][ 'url' ]) )
                        else:
                            columnLinkMetadata.append( "Column_link_{0}: /{1}/{2}/asc.html".format(
                                columnName,
                                "-".join(currProviderCombo).replace( " ", "_" ),
                                sortFieldMap[ columnName ][ 'url' ]) )
                    else:
                        columnImageMetadata.append( "Column_image_{0}: sort_icon_none.svg".format(columnName) )
                        columnLinkMetadata.append( "Column_link_{0}: /{1}/{2}/asc.html".format(
                            columnName,
                            "-".join(currProviderCombo).replace( " ", "_" ),
                            sortFieldMap[ columnName ][ 'url' ]) )

                url = "{0}/{1}/{2}.html".format(
                    "-".join(currProviderCombo).replace( " ", "_" ),
                    sortFieldMap[ sortfieldKey ][ 'url' ],
                    sortDirection )

                markdownContentArray = [
                    "Title: {0} - {1} {2}".format( "+".join(currProviderCombo), sortFieldMap[sortfieldKey]['title'],
                    sortDirection.capitalize()),
                    "Date: {0}".format( datetime.datetime.utcnow().strftime(
                        "%Y-%m-%d %H:%M:%S") ),
                    "Modified: {0}".format( datetime.datetime.utcnow().strftime(
                        "%Y-%m-%d %H:%M:%S") ),
                    "Save_as: {0}".format(url),
                    "url: {0}".format(url),
                    "Template: cloud-list-template"
                ]

                markdownContentArray.extend( columnImageMetadata )
                markdownContentArray.extend( columnLinkMetadata )

                markdownContentString = "\n".join( markdownContentArray )

                markdownFilename = "content/pages/{0}_{1}_{2}.md".format(
                    "-".join( currProviderCombo).replace( " ", "" ).lower(),
                    sortfieldKey,
                    sortDirection) 

                print( "Filename: {0}".format(markdownFilename) )

                with open( markdownFilename, "w" ) as fileHandle:
                    fileHandle.write( markdownContentString )

                

def _getProviderCombinations():
    providerCombinations = []
    cloudProviders = (
        "AWS",           
        "Azure",         
        "Google Cloud"  
    )

    for combinationLength in range( 1, len(cloudProviders) + 1 ):
        providerCombinations.extend( itertools.combinations( cloudProviders, combinationLength ) )

    return providerCombinations


def _getSortFields():
    return { 
        'cloudprovider'   : {
            'url'           : 'cloud_provider',
            'title'         : 'Cloud Providers'
        },
        'georegion'     : {
            'url'           : 'geo_region',
            'title'         : 'Geo Regions'
        },
        'continent'     : {
            'url'           : 'continent',
            'title'         : 'Continents'
        },
        'country'       : {
            'url'           : 'display_countries',
            'title'         : 'Countries'
        }
    }


if __name__ == "__main__":
    _main()
