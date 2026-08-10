#!/bin/bash

if [ $# -ne 1 ]
then
    echo "Usage: ./dns_enum_zonetransfer.sh <website>"
    exit 1
fi

for i in $(host -t ns "$1" | cut -d " " -f 4)
do
    host -l "$1" "$i" | grep "has address"
done