# !!HIGHLY EXPERIMENTAL!!
Use at your own risk

This script should make your orca sliced gcode files compatible with toolchangers

## Requirements:
Python!

## Features:
- Calls M104 to set temps before initiating toolchange
- Shuts down the heater after a toolhead isn't called again
- (optional) Adjust z-offset in code, might be good if you want to tweak all gcode z height independent of your tools
- (optional) Sets the LEDs upon toolchange to match filament color defined in orca (and set nozzles to white).  
You might want to tweak this if you use it, currently good for Dragonburner with sequins (3 rgb leds)

If you want to disable the optional stuff just change it to "**False**" in the script.

## How to use:
In your printing settings, add the post-processing script like below  
Should be <path_to_python.exe> <path_to_script.py> (or the linux equiv)  
![bild](https://github.com/Martorias/random_scripts/assets/38153913/cde88ad3-8c67-4a26-84f6-4a2c8077cc71)

Example of printer **START GCODE**
> PRINT_START TOOL_TEMP={first_layer_temperature[initial_tool]} TOOL=[initial_tool] BED=[first_layer_bed_temperature] CHAMBER=[chamber_temperature]

Printer **END GCODE**  doesn't have to be anything specific- **HOWEVER**  
If you use T# (eg. T0) in it to reset to your default toolhead, it has to be adjusted to "T0 ; something"  
Otherwise the script will (currently) think it's time to change toolhead and pre-heat it again -_-  
Anything as long as it's not only T followed by a number.  
![bild](https://github.com/Martorias/random_scripts/assets/38153913/5114c04d-8682-4184-986e-a82922a5f6d4)


More printer settings:  
![bild](https://github.com/Martorias/random_scripts/assets/38153913/70645f69-2caa-42f9-96f0-5c0be6a019d8)

![bild](https://github.com/Martorias/random_scripts/assets/38153913/f51578fa-d8f8-469f-bb90-52698e80df22)

(you might have to tweak this, I'm currently using 15 retract and -5 on restart to avoid blobs at beginning of prime)

For the filaments you want to disable flushing as it's not needed (set multiplier to 0 is the easiest ) unless you want a large prime tower  
There's probably a better way of doing this, not sure yet.  
![bild](https://github.com/Martorias/random_scripts/assets/38153913/b665695f-0697-45c4-a43e-61974bdd4175)

Adding some minimal purge per filament might be a good option as well, I use 15mm3  
![bild](https://github.com/Martorias/random_scripts/assets/38153913/d4df1dc3-1b4d-49cd-8529-3395204f9f41)


Prime tower settings example  
![bild](https://github.com/Martorias/random_scripts/assets/38153913/ab17be1b-9e0a-4d16-a062-012115e9337b)

## How it roughly works
Assuming we have both z_offset_adjust and led_effects as True, the script does (in this order)
- Searches through the file to find regex '^T\d$' (T followed by one digit) and adds them to a dictionary.  
- Searches through the end of the file to find nozzle temps, filament color and type. Specifically:  
  "; nozzle_temperature =" and splits the different tool temperatures into a list.  
  "; filament_colour =" and converts the hex colors to RGB and splits them into another list.  
  "; filament_type =" to see what filament type is used.
- Finds the "print_start" to add SET_LEDs just before (if enabled) (colors are based on filament_color)
  It then adds "T" + toolnr + "_TEMP=" + temp per each used tool, (adding T0_TEMP=230 T1_TEMP=210 etc, I'm using it for a purge macro)
- Remove all M104 lines (as they will mess up my pre-heating) **This is skipped if temperature_tower is found in the file lol**
- If enabled, depending on the filament it'll now create a **z_offset_value** (can be changed at the end of the script)  
  Finally it goes through the file and searches for '(G[01]\s.*Z)([-\+]?\d*\.?\d*)(.*)' to find G-codes moving on Z axis  
  It'll add (or subtract) the **z_offset_value** to all z-moves in the gcode.
  


