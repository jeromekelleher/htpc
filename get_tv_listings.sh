#!/bin/bash
# Script to be run daily to collect tv listings and 
# send them to tvheadend.

# Become the hts user so we can get the correct config.
# We need to delete the second line in the output xml 
# as it causes problems with tvheadend (DOCTYPE).

# Get one days worth of listings for 1 days in the future
sudo -u hts -H sh -c \
    'tv_grab_uk_atlas --days=1 --offset=1 | sed -e 2d | socat - UNIX-CONNECT:/home/hts/.hts/tvheadend/epggrab/xmltv.sock'
