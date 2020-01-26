#!/usr/bin/python3

import boto3
import botocore
import logging
import json
import pprint
import requests
import sys
import pelican


class AwsRegionsGenerator(pelican.generators.StaticGenerator):

    def __init__(self, *args, **kwargs):
        pass

    def generate_context(self):
        print( "generate_context invoked" )

    # Part of the context of a generator
    def generate_output(self, writer):
        print( "Generate_output invoked" )


def getAwsRegionsGenerator( pelicanHandle ):
    print( "AWS plugin, requested to return an instance of a generator class" )
    return AwsRegionsGenerator

def register():
    #pelican.signals.initialized.connect( pluginInitialized ) 
    pelican.signals.get_generators.connect( getAwsRegionsGenerator )


