import sys
import re

z_offset_adjust = True
led_effects = True
    
def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    red = int(hex_color[0:2], 16) / 255.0
    green = int(hex_color[2:4], 16) / 255.0
    blue = int(hex_color[4:6], 16) / 255.0
    return f"RED={red:.2f} GREEN={green:.2f} BLUE={blue:.2f}"

def find_nozzle_temperature_and_filament_colors(file_path):
    nozzle_temperatures = {}
    filament_colors = {}
    filament_type = ""
    with open(file_path, 'r') as file:
        lines = file.readlines()[-500:]
        for line in lines:
            if line.startswith("; nozzle_temperature ="):
                numbers = line.split('=')[1].strip().split(',')
                nozzle_temperatures.update({idx: int(val) for idx, val in enumerate(numbers)})
            elif line.startswith("; filament_colour ="):
                hexvalues = line.split('=')[1].strip().split(';')
                filament_colors.update({idx: hex_to_rgb(color) for idx, color in enumerate(hexvalues)})
            elif line.startswith("; filament_type ="):
                filvalues = line.split('=')[1].strip().split(';')
                filament_type = filvalues[0]
    return nozzle_temperatures, filament_colors, filament_type

def process_gcode(file_path, nozzle_temperatures, filament_colors, z_offset_value):
    modified_lines = []
    z_move_regex = re.compile(r"(G[01]\s.*Z)([-\+]?\d*\.?\d*)(.*)")  
    t_pattern = re.compile(r'^T\d$')    
    with open(file_path, 'r') as file:
        lines = file.readlines()
        for i in range(len(lines) - 1):
            match = re.match(t_pattern, lines[i])
            if match:        
                t_number = lines[i].strip()[1:]
                s_value = nozzle_temperatures[int(t_number)]
                rgb_value = filament_colors[int(t_number)]
                modified_lines.append(f"M104 T{t_number} S{s_value}\n")
                if led_effects: # Sets T?_RGB Led 3 to filament color, and led 1+2 to white
                    modified_lines.append(f"SET_LED LED=T{t_number}_RGB RED=1 GREEN=1 BLUE=1 INDEX=1 TRANSMIT=1\n")
                    modified_lines.append(f"SET_LED LED=T{t_number}_RGB RED=1 GREEN=1 BLUE=1 INDEX=2 TRANSMIT=1\n")  
                    modified_lines.append(f"SET_LED LED=T{t_number}_RGB {rgb_value} INDEX=3 TRANSMIT=1\n")                
            if z_offset_adjust:
                if lines[i].startswith("G") and "Z" in lines[i]:
                    result = z_move_regex.fullmatch(lines[i].strip())
                    if result:
                        adjusted_z = round(float(result.group(2)) + z_offset_value, 5)
                        lines[i] = result.group(1) + str(adjusted_z) + result.group(3) + " ; adjusted by z offset\n"
            modified_lines.append(lines[i])
    return modified_lines

def turn_off_finished_heaters(file_path):
    pattern = re.compile(r'^T\d$')

    with open(file_path, 'r') as file:
        lines = file.readlines()

    last_indices = {}
    for i, line in enumerate(lines):
        match = re.match(pattern, line)
        if match:
            key = match.group()
            last_indices[key] = i

    for key, index in last_indices.items():
        next_index = index + 1
        while next_index < len(lines) and not pattern.match(lines[next_index]):
            next_index += 1
        if next_index < len(lines):
            lines.insert(next_index, f'M104 S0 ; Turning off heater as it\'s not used anymore\n')

    with open(file_path, 'w') as file:
        file.writelines(lines)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: script.py file.gcode")
        sys.exit(1)
        
    file_path = sys.argv[1]
    turn_off_finished_heaters(file_path) 
    nozzle_temperatures, filament_colors, filament_type = find_nozzle_temperature_and_filament_colors(file_path)
    
    if "ASA" in filament_type or "ABS" in filament_type:
        z_offset_value = 0.01
    elif "PLA" in filament_type:
        z_offset_value = 0.06
    elif "TPU" in filament_type or "PET" in filament_type or "PETG" in filament_type:
        z_offset_value = 0.12
    else:
        z_offset_value = 0.0
    
    modified_lines = process_gcode(file_path, nozzle_temperatures, filament_colors, z_offset_value)
   
    with open(file_path, 'w') as file:
        file.writelines(modified_lines)
