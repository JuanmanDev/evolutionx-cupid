#!/bin/bash
cd /home/android/evolution-x-17
find -L kernel/ vendor/ hardware/ device/ external/ tools/ -type l 2>&1 | grep "loop detected" | awk -F "‘" '{print $2}' | awk -F "’" '{print $1}' > /mnt/c/Users/Juanm/Documents/antigravity/modest-bell/loops.txt
cat /mnt/c/Users/Juanm/Documents/antigravity/modest-bell/loops.txt | while read l; do
    if [ -n "$l" ]; then
        echo "Deleting loop: $l"
        rm "$l"
    fi
done
