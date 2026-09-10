#!/bin/bash
cd /home/android/evolution-x-17
echo "Deleting all corrupted .d depfiles from power loss..."
find out/ -name "*.d" -delete
echo "Depfiles cleaned!"
