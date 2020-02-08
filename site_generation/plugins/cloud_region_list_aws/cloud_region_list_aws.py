#!/usr/bin/python3

import boto3
import botocore
import logging
import json
import pprint
import requests
import sys
import pelican


class AwsRegionsGenerator(pelican.generators.PagesGenerator):
#class AwsRegionsGenerator():

    #def __init__(self, *args, **kwargs):
    #    super().__init__(*args, **kwargs)

    def generate_context(self):
        print( "generate_context invoked" )

        # http://adamcot.com/posts/2018/02/building-pelican-plugins-i/
        # Apparently context isn't passed in, it's a global called "context"
        # when you do {% for a in articles %} in a template, that's pulling
        # the content from context['articles'] behind the scenes

        # Other way is to make data an attribute of an object visible in template. 
        # This is most often seen in the case of articles or pages 

        # If you set article.foo = 'bar' in the generator, {{ article.foo }} is available
        # in the template

        
        #pprint.pprint(self.context)
        self.context['cloud_providers'] = {
            'aws': {
                'regions': {
                    'us-east-1': {
                        'country': 'US'

                    }
                }
            }
        }

        pprint.pprint(self.context['cloud_providers'])


    # Part of the context of a generator
    #def generate_output(self, writer):
    #    print( "Generate_output invoked" )


def getAwsRegionsGenerator( pelicanHandle ):
    print( "AWS plugin, requested to return an instance of a generator class" )
    return AwsRegionsGenerator

def register():
    #pelican.signals.initialized.connect( pluginInitialized ) 
    pelican.signals.get_generators.connect( getAwsRegionsGenerator )


