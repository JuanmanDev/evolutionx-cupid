#!/bin/bash
cd /home/android/evolution-x

echo "Starting repo sync loop..."
until repo sync -c -j4 --force-sync --no-clone-bundle --no-tags; do
    echo "Sync failed due to rate limits or network issues. Retrying in 10 seconds..."
    sleep 10
done

echo "Sync successful! Starting build..."
source build/envsetup.sh
lunch evolution_cupid-userdebug
m clean
m evolution -j4
