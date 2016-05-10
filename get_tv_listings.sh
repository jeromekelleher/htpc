#!/bin/bash
# Script to be run daily to collect tv listings and 
# send them to tvheadend.

SOCK_PATH=/home/hts/.hts/tvheadend/epggrab/xmltv.sock
# Become the hts user so we can get the correct config.
# We need to delete the second line in the output xml 
# as it causes problems with tvheadend (DOCTYPE).

su hts -c tv_grab_uk_atlas | sed -e 2d | socat - UNIX-CONNECT:$SOCK_PATH
