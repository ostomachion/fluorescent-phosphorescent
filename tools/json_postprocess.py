#!/usr/bin/env python3
"""
Post-process extracted JSON to convert raw preprocessor blocks into clean field + condition pairs.

This converts:
  {"frontPicFemale": {"raw": "#if COND\nVALUE\n#endif"}}
Into:
  {"frontPicFemale": "VALUE", "frontPicFemale_condition": "COND"}
"""

import sys
import json
import re

def extract_condition_from_raw(raw_value):
    """
    Extract condition and value from a raw preprocessor block.
    
    Input: "#if P_GENDER_DIFFERENCES && !P_GBA_STYLE_SPECIES_GFX\ngMonFrontPic_MeganiumF\n#endif"
    Output: ("P_GENDER_DIFFERENCES && !P_GBA_STYLE_SPECIES_GFX", "gMonFrontPic_MeganiumF")
    
    Returns (None, raw_value) for complex conditionals with #elif or #else.
    """
    # Skip complex conditionals - keep them as raw blocks
    if '#elif' in raw_value or ('#else' in raw_value and '#endif' in raw_value):
        # Check if it's a simple #if...#else...#endif or has #elif
        # Complex conditionals should stay as raw blocks
        if '#elif' in raw_value or raw_value.count('#') > 2:  # More than just #if and #endif
            return None, raw_value
    
    # Match #if CONDITION followed by value followed by #endif (single-line value)
    match = re.match(r'#if\s+(.+?)\s*\n([^#]+?)\s*\n#endif\s*$', raw_value, re.DOTALL)
    if match:
        condition = match.group(1).strip()
        value = match.group(2).strip()
        # Make sure there are no additional preprocessor directives in the value
        if '#' not in value:
            return condition, value
    
    # If it doesn't match the simple pattern, return as-is
    return None, raw_value

def parse_value(value_str):
    """Parse a value string into appropriate JSON type."""
    # Try to parse as JSON first
    if value_str.startswith('{') or value_str.startswith('['):
        try:
            return json.loads(value_str)
        except:
            pass
    
    # MON_COORDS_SIZE(width, height) -> {"width": width, "height": height}
    coords_match = re.match(r'MON_COORDS_SIZE\((\d+),\s*(\d+)\)', value_str)
    if coords_match:
        return {"width": int(coords_match.group(1)), "height": int(coords_match.group(2))}
    
    # Plain integers
    if re.match(r'^-?\d+$', value_str):
        return int(value_str)
    
    # Otherwise return as string
    return value_str

def process_species_data(species_data):
    """Process a single species' data, converting raw blocks to field + condition pairs."""
    processed = {}
    
    for field_name, field_value in species_data.items():
        # Skip forms recursively
        if field_name == "forms":
            processed[field_name] = {}
            for form_name, form_data in field_value.items():
                processed[field_name][form_name] = process_species_data(form_data)
            continue
        
        # Handle raw values
        if isinstance(field_value, dict) and "raw" in field_value:
            raw_content = field_value["raw"]
            condition, clean_value = extract_condition_from_raw(raw_content)
            
            if condition:
                # Store as field + field_condition
                processed[field_name] = parse_value(clean_value)
                processed[f"{field_name}_condition"] = condition
            else:
                # Keep as raw if we couldn't parse it
                processed[field_name] = field_value
        else:
            # Not a raw value, keep as-is
            processed[field_name] = field_value
    
    return processed

def postprocess_json(input_file, output_file):
    """Post-process JSON file to convert raw blocks to clean structure."""
    with open(input_file, 'r') as f:
        data = json.load(f)
    
    # Process each species
    if "data" in data:
        processed_data = {}
        for species_name, species_data in data["data"].items():
            processed_data[species_name] = process_species_data(species_data)
        data["data"] = processed_data
    
    # Write output
    with open(output_file, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"Post-processed {input_file} -> {output_file}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python3 json_postprocess.py <input.json> <output.json>")
        sys.exit(1)
    
    postprocess_json(sys.argv[1], sys.argv[2])
