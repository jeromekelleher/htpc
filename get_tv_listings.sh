#!/bin/bash

# Script to be run daily by placing copy in /etc/cron.daily
SOCK_PATH=/home/hts/.hts/tvheadend/epggrab/xmltv.sock
# Delete the second line DOCTYPE as it causes problems
tv_grab_uk_atlas | sed -e 2d | socat - UNIX-CONNECT:$SOCK_PATH
