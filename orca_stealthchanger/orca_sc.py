import re
import sys

# Settings:
cooldown_rows = 10000       # How many rows between same the previous tool being used again at a toolchange
cooldown_temp = 150         # Temperature to cool down to
preheat_rows = 2000         # How many rows before toolchange to start pre-heating
led_effects = False         # Use led effects (currently for 3x RGB, dragonburner)
z_offset_adjust = False     # If gcode should be z-adjusted, check the end to change templates


# Function to find tool changes in a G-code file
def find_tool_changes(file_path):
    toolchanges = {}

    # Open the file in read mode
    with open(file_path, 'r') as f:
        # Iterate over each line in the file
        for lineno, line in enumerate(f, start=1):
            # Use regular expression to find tool changes
            match = re.match(r'^T(\d)$', line.strip())
            if match:
                # Extract tool number from the match
                toolnr = match.group(1)
                # Store line number with tool number as key
                if toolnr not in toolchanges:
                    toolchanges[toolnr] = []
                toolchanges[toolnr].append(lineno)
    return toolchanges
    
def find_parameters(file_path):
    nozzle_temperatures = {}
    filament_colors = {}
    filament_type = ""
    with open(file_path, 'r') as f:
        lines = f.readlines()[-500:]
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

def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    red = int(hex_color[0:2], 16) / 255.0
    green = int(hex_color[2:4], 16) / 255.0
    blue = int(hex_color[4:6], 16) / 255.0
    return f"RED={red:.2f} GREEN={green:.2f} BLUE={blue:.2f}"

def find_in_file(start_line, regex):
    with open(file_path, 'r') as f:
        current_line = 0
        for line in f:
            current_line += 1
            if current_line > start_line:
                if re.match(regex, line.strip()):
                    return current_line
    return 0

def insert_temps(file_path):
    with open(file_path, "r") as f:
        contents = f.readlines()
    
    # Loop through tool numbers
    modified_lines = {}
    
    for toolnr, line_numbers in toolchanges.items():
        # Iterate through line numbers
        for i, lineno in enumerate(line_numbers):
            # Cooldown - Check if the heater won't be used in along time or not at all
            if lineno==line_numbers[-1]: # Last hit, won't be used again?
                next_tool_found = 0
                next_tool_row = find_in_file(lineno,'^T\d$')
                if next_tool_found == 0 and next_tool_row > 0: # Checking if there'll be another toolchange
                    modified_lines[next_tool_row-1] = []
                    modified_lines[next_tool_row-1].append(f"M104 T{toolnr} S0 ; Turning off tool as it's not used again\n") 
                            
                    next_tool_found = 1
            else:
                next_tool_row = find_in_file(lineno,'^T\d$')
                if next_tool_row > 0:
                    if line_numbers[i+1] - next_tool_row > cooldown_rows: # If next hit of current tool is > cooldown_rows from next toolchange
                        modified_lines[next_tool_row-1] = []
                        modified_lines[next_tool_row-1].append(f"M104 T{toolnr} S{cooldown_temp} ; Cooling down while tool is in long-time parking\n")                

            # Pre-heat - Set temps ahead of toolhead usage
            print_start = find_in_file(0, '(?i)print_start')
            if lineno-preheat_rows < print_start:
                preheat_row = print_start
            else:
                preheat_row = lineno - preheat_rows
                #print(f"current line: {lineno}, start preheat at: {preheat_row}")
            modified_lines[preheat_row] = []
            s_value = nozzle_temperatures[int(toolnr)]
            modified_lines[preheat_row].append(f"M104 T{toolnr} S{s_value} ; Pre-heating tool before use\n")
    
    myKeys = list(modified_lines.keys())
    myKeys.sort()
    sorted_dict = {i: modified_lines[i] for i in myKeys}
    
    indexcounter = 0
    for i,kv in sorted_dict.items():
        print(f"Line {i}: inserting {kv}")
        contents.insert(i+indexcounter, "".join(kv))
        indexcounter += 1
    
    with open(file_path, "w") as f:
        contents = "".join(contents)
        f.write(contents)        

def process_gcode_offset(file_path, z_offset_value):
    modified_lines = []
    z_move_regex = re.compile(r"(G[01]\s.*Z)([-\+]?\d*\.?\d*)(.*)")  
    with open(file_path, 'r') as f:
        lines = f.readlines()
        for i in range(len(lines) - 1):
            if lines[i].startswith("G") and "Z" in lines[i]:
                result = z_move_regex.fullmatch(lines[i].strip())
                if result:
                    adjusted_z = round(float(result.group(2)) + z_offset_value, 5)
                    lines[i] = result.group(1) + str(adjusted_z) + result.group(3) + " ; adjusted by z offset\n"
            modified_lines.append(lines[i])
            
    with open(file_path, 'w') as file:
        file.writelines(modified_lines)

def remove_m104_lines(file_path):
    with open(file_path, 'r') as f:
        lines = f.readlines()
    filtered_lines = [line for line in lines if not line.startswith("M104 S")]
    with open(file_path, 'w') as f:
        f.writelines(filtered_lines)
        
def fix_print_start(file_path):
    with open(file_path, 'r') as f:
        lines = f.readlines()
    sorted_tools = sorted(toolchanges.keys())
    start_line_index = find_in_file(0, '(?i)print_start')
    start_line = lines[start_line_index-1].strip()
    led_line = ""
    for t in sorted_tools:
        s_value = nozzle_temperatures[int(t)]
        toolnr = "".join(t)
        start_line = start_line + " T" + str(toolnr) + "_TEMP=" + str(s_value)
        if led_effects: # Sets T?_RGB Led 3 to filament color, and led 1+2 to white
            rgb_value = filament_colors[int(toolnr)]
            led_line = led_line + (f"SET_LED LED=T{toolnr}_RGB RED=1 GREEN=1 BLUE=1 INDEX=1 TRANSMIT=1\n")
            led_line = led_line + (f"SET_LED LED=T{toolnr}_RGB RED=1 GREEN=1 BLUE=1 INDEX=2 TRANSMIT=1\n")  
            led_line = led_line + (f"SET_LED LED=T{toolnr}_RGB {rgb_value} INDEX=3 TRANSMIT=1\n")
    print(f"Initial leds:\n{led_line}")            
    print(f"New print_start:\n{start_line}" + "\n")    
    lines[start_line_index-1] = led_line + start_line + '\n'

            
    with open(file_path, 'w') as f:
        f.writelines(lines)        

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: script.py file.gcode")
        sys.exit(1)
        
    file_path = sys.argv[1]

    toolchanges = find_tool_changes(file_path)
    nozzle_temperatures, filament_colors, filament_type = find_parameters(file_path)    
    fix_print_start(file_path)
    if not find_in_file(0, '(?i).*temperature_tower') >0:
        remove_m104_lines(file_path)    
        insert_temps(file_path)

    if z_offset_adjust:
        if "ASA" in filament_type or "ABS" in filament_type:
            z_offset_value = 0.01
        elif "PLA" in filament_type:
            z_offset_value = 0
        elif "TPU" in filament_type or "PET" in filament_type or "PETG" in filament_type:
            z_offset_value = 0.12
        else:
            z_offset_value = 0
        
        if not z_offset_value == 0:
            process_gcode_offset(file_path, z_offset_value)
