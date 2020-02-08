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

https://mister-gold.pro/posts/en/pelican-custom-page-using-jinja2/

Trying to get something that will take jinja variables, then circle back to populating them


Oi.  Templates go under themes, which are in :~/.local/lib/python3.6/site-packages/pelican/themes/notmyidea/templates

How the fuck is that a good idea?  Ugh.


--- 2020-02-08 ---

* Going to use generator to create one hardcode template variable that is inserted into a page
* cd git/CloudRegionsList/site_generation
* make html will build site
** You can see how it invokes both methods of our generator
* Believe we need to populate our hardcoded template variable in generate_context
* Our plugin didn't get invoked by magic. We modified pelicanconf.py to add 'cloud_region_list_aws' into PLUGINS= [ ] 

* Alright, now we're turning the corner
* AWsRegionsGenerator now inherits from pelican.generators.PagesGenerator
* Once we do that, inside generate context we can access self.context, and that has a lot of goodness
* Let's put something in self.context, then try to access it from our aws.md page in a template
