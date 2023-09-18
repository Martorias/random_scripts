#!/bin/bash

# REQUIREMENTS: You MUST add " #point1" through 4 behind your original numbers in your printer.cfg one time, example below:
# [quad_gantry_level]
# points:
#   50,25 #point1
#   50,250 #point2
#   250,250 #point3
#   250,25 #point4

# Set your coordinates here, the fuzz will INCREASE only so if you want a smaller number just lower the input by half the fuzz
# This are probably the only things you might want to change in this macro thing
# In this example the coordinates for the first point will change between 45,20 to 55,30
botleft="45,20"
topleft="45,245"
topright="245,20"
botright="245,20"
fuzz=10
printercfg="/home/pi/printer_data/config/printer.cfg"

# Split the input strings into arrays
IFS=',' read -ra bl <<< "$botleft"
IFS=',' read -ra tl <<< "$topleft"
IFS=',' read -ra tr <<< "$topright"
IFS=',' read -ra br <<< "$botright"

# Generate random numbers within the specified fuzz-range
blx=$((RANDOM % $fuzz + $((bl[0])))) ; bly=$((RANDOM % $fuzz + $((bl[1]))))
tlx=$((RANDOM % $fuzz + $((tl[0])))) ; tly=$((RANDOM % $fuzz + $((tl[1]))))
trx=$((RANDOM % $fuzz + $((tr[0])))) ; try=$((RANDOM % $fuzz + $((tr[1]))))
brx=$((RANDOM % $fuzz + $((br[0])))) ; bry=$((RANDOM % $fuzz + $((br[1]))))

# Find and replace the lines in printer.cfg
sed -i "s/\(.*\) [0-9]\+,[0-9]\+ \(#point1\)/\1 ${blx},${bly} \2/" "$printercfg"
sed -i "s/\(.*\) [0-9]\+,[0-9]\+ \(#point2\)/\1 ${tlx},${tly} \2/" "$printercfg"
sed -i "s/\(.*\) [0-9]\+,[0-9]\+ \(#point3\)/\1 ${trx},${try} \2/" "$printercfg"
sed -i "s/\(.*\) [0-9]\+,[0-9]\+ \(#point4\)/\1 ${brx},${bry} \2/" "$printercfg"
