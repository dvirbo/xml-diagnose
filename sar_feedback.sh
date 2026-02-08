#!/bin/bash

date '+%m/%d/%y %H:%M:%S Start running processes..'

. /opt/actimize/ControlM/process_config.sh

#######################################################################################################################################################################

date '+%m/%d/%y %H:%M:%S Start - SAR_Feedback'

# Check if date parameter is provided for SAR_Feedback
# Expected format: dd/mm/yyyy (e.g., 01/01/2025)
if [ -z "$1" ]; then
    date '+%m/%d/%y %H:%M:%S Error: Date parameter is required for SAR_Feedback (format: dd/mm/yyyy)'
    exit 1
fi

DATE_PARAM="$1"

# Run SAR_Feedback with provided date parameter
date '+%m/%d/%y %H:%M:%S Running SAR_Feedback reports with date: '"$DATE_PARAM"
python3 $SAR_RESPONSE "$DATE_PARAM"
SAR_Feedback_code=$?

if [ $SAR_Feedback_code != 0 ]; then 
    date '+%m/%d/%y %H:%M:%S Error in SAR_Feedback run'
    exit 1
fi

# Run second process (only if first succeeded)
# Define SEND_XML_DATA in process_config.sh with the full path to the second main.py
if [ -n "$SEND_XML_DATA" ]; then
    date '+%m/%d/%y %H:%M:%S Running second process...'
    python3 $SEND_XML_DATA
    SECOND_code=$?
    if [ $SECOND_code != 0 ]; then
        date '+%m/%d/%y %H:%M:%S Error in second process run'
        exit 1
    fi
fi

#######################################################################################################################################################################
