# CloudRegionsList
Generate static website with useful location of locations of public cloud regions.

pip3 install awscli boto3 requests pelican[Markdown]

# Add new cloud region

`$ ./add-new-cloud-location.py cloud_geographic_locations.json aws eu-west-3 "Europe" "europe" "[ \"SE\" ]" "[ \"SE-D\", \"SE-C\" ]" "Stockholm"`

# Create pelican project for site

mkdir site_generation
cd site_generation

make html
make s3_upload


# Plugins

Looks like we may want to do a Pelican plugin to generate our dynamic content.

http://docs.getpelican.com/en/3.6.3/plugins.html

Plugins work on concept of signals.

Plugins subscribe to signals. 

So we'd want to listen for "Hey, about to generate AWS page"

Do something, return content so that it can be rendered into the template

http://docs.getpelican.com/en/3.6.3/internals.html

maybe we just need a generator?  Wait for a ping that says "do your thing" 

http://adamcot.com/posts/2018/02/building-pelican-plugins-i/

No, we want a plugin. Generator plugins provide content for templates. Exactly what we're doing

# How to do that

cd site_generation
vi pelicanconf.py

pelican content now invokes our plugin
