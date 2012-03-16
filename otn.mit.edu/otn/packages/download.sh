#!/bin/sh

git clone git://github.com/joshuaclayton/blueprint-css.git
# http://github.com/flashingpumpkin/django-socialregistration
git clone git://github.com/flashingpumpkin/django-socialregistration.git
    
git clone git://github.com/sciyoshi/pyfacebook.git
hg clone https://python-twitter.googlecode.com/hg/ python-twitter
hg clone http://bitbucket.org/andrewgodwin/south/
#cd south
#hg update -C 0.6.2

#cd ..
hg clone https://sorl-thumbnail.googlecode.com/hg/ sorl-thumbnail

hg clone https://django-polymorphic-models.googlecode.com/hg/ django-polymorphic-models
