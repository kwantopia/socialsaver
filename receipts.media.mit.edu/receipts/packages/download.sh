#!/bin/sh

# http://github.com/flashingpumpkin/django-socialregistration
git clone git://github.com/flashingpumpkin/django-socialregistration.git
    
svn checkout http://django-facebookconnect.googlecode.com/svn/trunk/django-facebookconnect/ django-facebookconnect

git clone git://github.com/sciyoshi/pyfacebook.git

hg clone http://bitbucket.org/andrewgodwin/south/
cd south
hg update -C 0.6.1

cd ..
hg clone https://sorl-thumbnail.googlecode.com/hg/ sorl-thumbnail
