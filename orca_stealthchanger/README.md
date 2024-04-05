!!HIGHLY EXPERIMENTAL!!
Use at your own risk

This script should make your orca sliced gcode files compatible with toolchangers

Features:
- Calls M104 to set temps before initiating toolchange
- Shuts down the heater after a toolhead isn't called again
- (optional) Adjust z-offset in code, might be good if you want to tweak all gcode z height independent of your tools
- (optional) Sets the LEDs upon toolchange to match filament color defined in orca (and set nozzles to white).
You might want to tweak this if you use it, currently good for Dragonburner with sequins (3 rgb leds)

If you want to disable the optional stuff just changed to "False" in the script.

How to use:
In your printing settings, add the post-processing script (I had to point at python.exe then script)

![bild](https://github.com/Martorias/random_scripts/assets/38153913/cde88ad3-8c67-4a26-84f6-4a2c8077cc71)

Printer start gcode shouldn't have to be anything special I think, as long as it matches your klipper macro.

I use PRINT_START TOOL_TEMP={first_layer_temperature[initial_tool]} TOOL=[initial_tool] BED=[first_layer_bed_temperature] CHAMBER=[chamber_temperature]

More printer settings:

![bild](https://github.com/Martorias/random_scripts/assets/38153913/70645f69-2caa-42f9-96f0-5c0be6a019d8)

![bild](https://github.com/Martorias/random_scripts/assets/38153913/f51578fa-d8f8-469f-bb90-52698e80df22)

(you might have to tweak this)

For the filaments you want to disable flushing as it's not needed (set to 0) unless you want a large prime tower
Might be a better way of doing this, not sure yet.

![bild](https://github.com/Martorias/random_scripts/assets/38153913/b149bfc5-1153-4c96-b6f7-16fd44600493)

Prime tower settings example

![bild](https://github.com/Martorias/random_scripts/assets/38153913/ab17be1b-9e0a-4d16-a062-012115e9337b)



