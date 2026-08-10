#!/bin/bash

# takes two paramters config.txt users.txt and finds matching credentials
# Usage check
if [ $# -ne 1 ]; then
    echo "Usage: $0 <config_file>"
    exit 1
fi

config="$1"

# File check
if [ ! -f "$config" ]; then
    echo "Error: File not found: $config"
    exit 1
fi

current_user=""

awk -F'=' '{print $1 ":" $2}' "$config" \
| grep -v "^#" \
| tr -d " " \
| tr 'A-Z' 'a-z' \
| grep -E "user:|pass:" \
| while read -r line; do

    if echo "$line" | grep -q "^user:"; then
        current_user="${line#user:}"

    elif echo "$line" | grep -q "^pass:" && [ -n "$current_user" ]; then
        pass="${line#pass:}"
        echo "$current_user:$pass"
        current_user=""
    fi

done