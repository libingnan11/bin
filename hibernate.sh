#!/bin/bash

#umount
echo "Unmounting sshfs..."
mountpoints=`mount | grep sshfs | cut -f3 -d" "`
for m in $mountpoints; do
    echo " $m"
    umount $m
done

#fusermount
mountpoints=`mount | grep sshfs | cut -f3 -d" "`
if [ ! -z $mountpoints ]; then
    echo "Unmounting sshfs by 'fusermount -uz'..."
    for m in $mountpoints; do
        echo " $m"
        fusermount -uz $m
    done
fi

#kill audio/video apps and sshfs
echo "Terminating audio/video apps and sshfs"
ps aux | grep -P "vlc|rhythmbox|sshfs" | grep -v grep | awk '{print $2}' | xargs kill -s 9

#drop disk cache if little memory
#sync && echo 3 | sudo tee /proc/sys/vm/drop_caches && 

#hibernate
sleep 1;
echo "Hibernating..."
pm-hibernate

#may cause system hang
sleep 1; 
echo "Reloading ALSA..."
sudo alsa force-reload

