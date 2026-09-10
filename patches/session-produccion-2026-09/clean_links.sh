#!/bin/bash
cd /home/android/evolution-x-17
find kernel/ -type l | while read l; do
    if ! readlink -f "$l" > /dev/null 2>&1; then
        echo "Removing broken symlink: $l"
        rm "$l"
    fi
done
