#!/bin/sh

git clone git://github.com/joshuaclayton/blueprint-css.git
# http://github.com/flashingpumpkin/django-socialregistration
git clone git://github.com/flashingpumpkin/django-socialregistration.git
git clone git://github.com/jaz303/tipsy.git
git clone git://github.com/defunkt/facebox.git
git clone git://github.com/draganbabic/uni-form.git
    
git clone git://github.com/sciyoshi/pyfacebook.git
hg clone https://python-twitter.googlecode.com/hg/ python-twitter
hg clone http://bitbucket.org/andrewgodwin/south/
#cd south
#hg update -C 0.6.2

hg clone https://sorl-thumbnail.googlecode.com/hg/ sorl-thumbnail

# premix BestBuy python api
hg clone http://bitbucket.org/gumptioncom/premix/
git clone https://github.com/valums/ajax-upload.git
