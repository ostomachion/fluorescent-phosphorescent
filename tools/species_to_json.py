#!/usr/bin/env python3
"""
Convert C species definitions to structured JSON format.

Usage: python3 tools/species_to_json.py <input_file.h> [output_file.json]
"""

import sys
import re
import json
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s'
)

def simplify_enum(value, prefix):
    """Remove prefix from enum and convert to kebab-case"""
    if value.startswith(prefix):
        suffix = value[len(prefix):]
        return suffix.lower().replace("_", "-")
    return value

def count_all_species_entries(c_code):
    """Count ALL species entries in the C file, including macro-based ones."""
    # Match [SPECIES_XXX] patterns
    pattern = r'\[SPECIES_([A-Z0-9_]+)\]'
    matches = re.findall(pattern, c_code)
    return matches

def parse_species_info(c_code):
    """Parse C species info structs and convert to JSON"""
    species_dict = {}
    skipped_species = []
    
    # First, count ALL species entries in the file
    all_species_entries = count_all_species_entries(c_code)
    logging.info(f"Found {len(all_species_entries)} species entries in C file")
    
    # Find all parseable species definitions (standard format)
    species_pattern = r'\[SPECIES_(\w+)\]\s*=\s*\{'
    
    matches = list(re.finditer(species_pattern, c_code))
    logging.info(f"Found {len(matches)} species with standard struct format")
    
    parseable_species = set()
    for i, match in enumerate(matches):
        species_name = match.group(1)
        start = match.end()
        
        # Find the end - match braces carefully
        brace_count = 1
        pos = start
        while pos < len(c_code) and brace_count > 0:
            if c_code[pos] == '{':
                brace_count += 1
            elif c_code[pos] == '}':
                brace_count -= 1
            pos += 1
        
        body = c_code[start:pos-1]
        
        try:
            species_data = parse_species_body(body)
            
            # Validate that we parsed something
            if not species_data:
                logging.warning(f"SKIPPED {species_name}: No fields parsed")
                skipped_species.append((species_name, "No fields parsed"))
                continue
            
            # Check for excessive raw values (might indicate parsing issues)
            raw_count = sum(1 for v in species_data.values() if isinstance(v, dict) and 'raw' in v)
            total_count = len(species_data)
            if total_count > 0 and raw_count / total_count > 0.5:
                logging.warning(f"NOTICE {species_name}: {raw_count}/{total_count} fields are raw (may need manual review)")
            
            species_dict[species_name] = species_data
            parseable_species.add(species_name)
            
        except Exception as e:
            logging.error(f"SKIPPED {species_name}: Parse error - {str(e)}")
            skipped_species.append((species_name, str(e)))
            continue
    
    # Find species that were in the file but not parsed (macro-based, etc.)
    unparsed_species = [s for s in all_species_entries if s not in parseable_species]
    
    # Summary
    logging.info(f"Successfully parsed {len(species_dict)} species")
    
    unparsed_by_prefix = {}
    if unparsed_species:
        logging.error(f"============================================================")
        logging.error(f"UNPARSED SPECIES: {len(unparsed_species)} species entries found but not converted")
        logging.error(f"These likely use macros or non-standard formats:")
        # Group by common patterns
        for name in unparsed_species:
            prefix = name.split('_')[0] if '_' in name else name
            if prefix not in unparsed_by_prefix:
                unparsed_by_prefix[prefix] = []
            unparsed_by_prefix[prefix].append(name)
        
        for prefix, names in sorted(unparsed_by_prefix.items()):
            if len(names) <= 3:
                for name in names:
                    logging.error(f"  - {name}")
            else:
                logging.error(f"  - {prefix}: {len(names)} variants ({', '.join(names[:3])}, ...)")
        logging.error(f"============================================================")
    
    if skipped_species:
        logging.warning(f"Parse errors: {len(skipped_species)} species with standard format failed to parse:")
        for name, reason in skipped_species:
            logging.warning(f"  - {name}: {reason}")
    
    # Calculate coverage
    total_entries = len(all_species_entries)
    parsed_count = len(species_dict)
    coverage_pct = (parsed_count / total_entries * 100) if total_entries > 0 else 0
    
    if coverage_pct < 100:
        logging.warning(f"Coverage: {parsed_count}/{total_entries} species ({coverage_pct:.1f}%)")
    
    return species_dict, unparsed_by_prefix

def parse_species_body(body):
    """Parse the body of a species definition"""
    species_data = {}
    
    # Split by top-level commas (not inside parens/braces/brackets)
    lines = []
    current = ""
    depth = 0
    in_string = False
    escape_next = False
    in_preprocessor = False
    
    for char in body:
        if escape_next:
            current += char
            escape_next = False
            continue
        
        if char == '\\':
            current += char
            escape_next = True
            continue
        
        if char == '"':
            in_string = not in_string
            current += char
            continue
        
        if in_string:
            current += char
            continue
        
        # Track preprocessor directives
        if char == '#' and (not current or current[-1] == '\n'):
            in_preprocessor = True
            current += char
            continue
        
        if in_preprocessor:
            current += char
            if char == '\n':
                in_preprocessor = False
            continue
        
        if char in '({[':
            depth += 1
            current += char
        elif char in ')}]':
            depth -= 1
            current += char
        elif char == ',' and depth == 0:
            if current.strip():
                lines.append(current.strip())
            current = ""
        else:
            current += char
    
    if current.strip():
        lines.append(current.strip())
    
    # Parse each line, tracking preprocessor context
    preprocessor_stack = []  # Stack of active preprocessor conditions
    conditional_fields = {}  # Track fields with multiple conditional values
    
    for line in lines:
        # Extract any preprocessor directives and the remaining content
        remaining = line
        directives_for_this_line = []  # Track all directives encountered for this line
        
        # Process all preprocessor directives in this line
        while remaining:
            # Try to match preprocessor directives
            if_match = re.match(r'^(#if(?:def|ndef)?\s+[^\n]+)(?:\n(.*))?$', remaining, re.DOTALL)
            elif_match = re.match(r'^(#elif\s+[^\n]+)(?:\n(.*))?$', remaining, re.DOTALL)
            else_match = re.match(r'^(#else)(?:\s*\n(.*))?$', remaining, re.DOTALL)
            endif_match = re.match(r'^(#endif[^\n]*)(?:\n(.*))?$', remaining, re.DOTALL)
            
            if if_match:
                directive = if_match.group(1)
                preprocessor_stack.append(directive)
                directives_for_this_line.append(directive)
                remaining = if_match.group(2) or ""
            elif elif_match:
                directive = elif_match.group(1)
                if preprocessor_stack:
                    preprocessor_stack[-1] = directive
                directives_for_this_line.append(directive)
                remaining = elif_match.group(2) or ""
            elif else_match:
                directive = else_match.group(1)
                if preprocessor_stack:
                    preprocessor_stack[-1] = directive
                directives_for_this_line.append(directive)
                remaining = else_match.group(2) or ""
            elif endif_match:
                directive = endif_match.group(1)
                if preprocessor_stack:
                    preprocessor_stack.pop()
                directives_for_this_line.append(directive)
                remaining = endif_match.group(2) or ""
            else:
                # No more preprocessor directives in this line
                break
        
        # Skip if nothing remains after preprocessing directives
        if not remaining or not remaining.strip():
            continue
        
        # Try to match field assignment in remaining content
        match = re.match(r'^\s*\.\s*(\w+)\s*=\s*(.+)$', remaining, re.DOTALL)
        if match:
            field_name = match.group(1)
            value = match.group(2).strip()
            
            # Check if this field already exists (conditional assignment)
            if field_name in species_data or field_name in conditional_fields:
                # This is a conditional field with multiple values
                if field_name not in conditional_fields:
                    # First time seeing duplicate, initialize with existing value
                    conditional_fields[field_name] = []
                    if field_name in species_data:
                        existing = species_data[field_name]
                        if isinstance(existing, dict) and 'raw' in existing:
                            conditional_fields[field_name].append(existing['raw'])
                        del species_data[field_name]
                
                # Add this conditional value with its directives
                if directives_for_this_line:
                    conditional_fields[field_name].append('\n'.join(directives_for_this_line) + '\n' + value)
                else:
                    conditional_fields[field_name].append(value)
            
            # If we're inside preprocessor block(s), wrap just the value with directives
            elif preprocessor_stack:
                # Store as raw for now, will be handled with other conditionals
                if field_name not in conditional_fields:
                    conditional_fields[field_name] = []
                
                # Reconstruct with preprocessor directives around the value only
                full_directives = directives_for_this_line if directives_for_this_line else list(preprocessor_stack)
                raw_value = '\n'.join(full_directives) + '\n' + value
                conditional_fields[field_name].append(raw_value)
            else:
                species_data[field_name] = convert_value(value, field_name)
    
    # Now handle conditional fields - combine all their values
    for field_name, values in conditional_fields.items():
        # Combine all conditional values with their directives plus #endif
        combined = '\n'.join(values) + '\n' + '#endif' * values[0].count('#if')
        species_data[field_name] = {"raw": combined}
    
    return species_data

def convert_value(value, field_name=None):
    """Convert a C value to JSON representation"""
    value = value.strip()
    
    # Check for MON_COORDS_SIZE(width, height) pattern
    coords_match = re.match(r'^MON_COORDS_SIZE\((\d+),\s*(\d+)\)$', value)
    if coords_match:
        return {
            "width": int(coords_match.group(1)),
            "height": int(coords_match.group(2))
        }
    
    # Check for ternary operators with standard config flags
    # Pattern: FLAG ? value_if_true : value_if_false
    ternary_match = re.match(r'^(.+?)\s*\?\s*(.+?)\s*:\s*(.+)$', value, re.DOTALL)
    if ternary_match:
        condition = ternary_match.group(1).strip()
        true_value = ternary_match.group(2).strip()
        false_value = ternary_match.group(3).strip()
        
        # Remove outer parentheses from condition if present
        if condition.startswith('(') and condition.endswith(')'):
            condition = condition[1:-1].strip()
        
        # Handle P_GBA_STYLE_SPECIES_GFX - true = gba style, false = upgraded/modern
        if condition == "P_GBA_STYLE_SPECIES_GFX":
            return {
                "gba": convert_value(true_value, field_name),
                "upgraded": convert_value(false_value, field_name)
            }
        
        # Handle P_GBA_STYLE_SPECIES_ICONS - true = gba style, false = upgraded
        if condition == "P_GBA_STYLE_SPECIES_ICONS":
            return {
                "gba": convert_value(true_value, field_name),
                "upgraded": convert_value(false_value, field_name)
            }
        
        # Handle P_UPDATED_STATS >= GEN_X
        stats_match = re.match(r'^P_UPDATED_STATS\s*>=\s*GEN_(\d+)$', condition)
        if stats_match:
            gen = stats_match.group(1)
            return {
                f"gen{gen}+": convert_value(true_value, field_name),
                f"gen{int(gen)-1}-": convert_value(false_value, field_name)
            }
        
        # Handle P_UPDATED_EXP_YIELDS >= GEN_X
        exp_match = re.match(r'^P_UPDATED_EXP_YIELDS\s*>=\s*GEN_(\d+)$', condition)
        if exp_match:
            gen = exp_match.group(1)
            return {
                f"gen{gen}+": convert_value(true_value, field_name),
                f"gen{int(gen)-1}-": convert_value(false_value, field_name)
            }
        
        # For any other ternary, keep as raw
        # (This preserves complex conditions we don't explicitly handle)
    
    # TRUE/FALSE -> 1/0
    if value == "TRUE":
        return 1
    elif value == "FALSE":
        return 0
    
    # Plain integers
    if re.match(r'^-?\d+$', value):
        return int(value)
    
    # Check for _("...") pattern - extract string
    string_match = re.match(r'^_\("(.+)"\)$', value, re.DOTALL)
    if string_match:
        return string_match.group(1)
    
    # Handle COMPOUND_STRING for descriptions
    if field_name == "description":
        compound_match = re.match(r'^COMPOUND_STRING\((.*)\)$', value, re.DOTALL)
        if compound_match:
            content = compound_match.group(1).strip()
            # Extract all string literals and join them
            # Pattern: "string content\n" or "string content")
            string_parts = re.findall(r'"([^"]*)"', content)
            # Join all parts - the \n at the end of each line is the actual line break
            full_text = ''.join(string_parts)
            return full_text
    
    # Handle ANIM_FRAMES for animation frames
    # Pattern: ANIM_FRAMES(ANIMCMD_FRAME(frame, duration), ...)
    if field_name == "frontAnimFrames":
        anim_match = re.match(r'^ANIM_FRAMES\((.*)\)$', value, re.DOTALL)
        if anim_match:
            content = anim_match.group(1).strip()
            # Extract all ANIMCMD_FRAME entries
            frames = []
            for frame_match in re.finditer(r'ANIMCMD_FRAME\((\d+),\s*(\d+)\)', content):
                frames.append({
                    "frame": int(frame_match.group(1)),
                    "duration": int(frame_match.group(2))
                })
            return frames
    
    # Handle EVOLUTION for evolution data
    # Pattern: EVOLUTION({EVO_TYPE, param, SPECIES_NAME}, {EVO_TYPE, param, SPECIES_NAME, CONDITIONS(...)}, ...)
    if field_name == "evolutions":
        evo_match = re.match(r'^EVOLUTION\((.*)\)$', value, re.DOTALL)
        if evo_match:
            content = evo_match.group(1).strip()
            evolutions = []
            
            # Find all evolution entries wrapped in curly braces
            # This is complex because of nested braces in CONDITIONS
            depth = 0
            current_evo = ""
            for char in content:
                if char == '{':
                    depth += 1
                    current_evo += char
                elif char == '}':
                    depth -= 1
                    current_evo += char
                    if depth == 0 and current_evo.strip():
                        # We've finished one evolution entry
                        # Parse: {EVO_TYPE, param, SPECIES_NAME} or {EVO_TYPE, param, SPECIES_NAME, CONDITIONS(...)}
                        evo_content = current_evo.strip()[1:-1]  # Remove outer braces
                        
                        # Split by commas, but be careful of nested structures
                        parts = []
                        part = ""
                        nested = 0
                        for c in evo_content:
                            if c == '(' or c == '{':
                                nested += 1
                                part += c
                            elif c == ')' or c == '}':
                                nested -= 1
                                part += c
                            elif c == ',' and nested == 0:
                                parts.append(part.strip())
                                part = ""
                            else:
                                part += c
                        if part.strip():
                            parts.append(part.strip())
                        
                        if len(parts) >= 3:
                            evo_data = {
                                "method": simplify_enum(parts[0], "EVO_"),
                                "param": parts[1].strip(),
                                "species": simplify_enum(parts[2], "SPECIES_")
                            }
                            # Check for CONDITIONS in part 3
                            if len(parts) > 3 and "CONDITIONS" in parts[3]:
                                evo_data["conditions"] = parts[3].strip()
                            evolutions.append(evo_data)
                        
                        current_evo = ""
                elif depth > 0:
                    current_evo += char
            
            return evolutions
    
    # Handle types field: MON_TYPES(TYPE_X, TYPE_Y) -> ["x", "y"]
    if field_name == "types":
        types_match = re.match(r'^MON_TYPES\((.+)\)$', value)
        if types_match:
            types_str = types_match.group(1)
            # Split by comma and extract type names
            type_list = []
            for type_part in types_str.split(','):
                type_part = type_part.strip()
                if type_part.startswith('TYPE_'):
                    type_name = type_part[5:]  # Remove "TYPE_"
                    type_list.append(type_name.lower().replace("_", "-"))
            if type_list:
                return type_list
    
    # Handle eggGroups field: MON_EGG_GROUPS(EGG_GROUP_X, EGG_GROUP_Y) -> ["x", "y"]
    if field_name == "eggGroups":
        egg_match = re.match(r'^MON_EGG_GROUPS\((.+)\)$', value)
        if egg_match:
            eggs_str = egg_match.group(1)
            # Split by comma and extract egg group names
            egg_list = []
            for egg_part in eggs_str.split(','):
                egg_part = egg_part.strip()
                if egg_part.startswith('EGG_GROUP_'):
                    egg_name = egg_part[10:]  # Remove "EGG_GROUP_"
                    egg_list.append(egg_name.lower().replace("_", "-"))
            if egg_list:
                return egg_list
    
    # Handle abilities field: { ABILITY_X, ABILITY_Y, ABILITY_Z } -> ["x", "y", "z"]
    if field_name == "abilities":
        abilities_match = re.match(r'^\{\s*(.+)\s*\}$', value)
        if abilities_match:
            abilities_str = abilities_match.group(1)
            # Split by comma and extract ability names
            ability_list = []
            for ability_part in abilities_str.split(','):
                ability_part = ability_part.strip()
                if ability_part.startswith('ABILITY_'):
                    ability_name = ability_part[8:]  # Remove "ABILITY_"
                    ability_list.append(ability_name.lower().replace("_", "-"))
            if ability_list:
                return ability_list
    
    # Handle genderRatio field patterns
    if field_name == "genderRatio":
        # MON_GENDERLESS -> "genderless"
        if value == "MON_GENDERLESS":
            return "genderless"
        # MON_MALE -> "male-only"
        if value == "MON_MALE":
            return "male-only"
        # MON_FEMALE -> "female-only"
        if value == "MON_FEMALE":
            return "female-only"
        # PERCENT_FEMALE(X) -> {"female": X}
        percent_match = re.match(r'^PERCENT_FEMALE\(([\d.]+)\)$', value)
        if percent_match:
            return {"female": float(percent_match.group(1))}
    
    # Handle enum simplification based on field name
    if field_name:
        # friendship: *_FRIENDSHIP -> kebab-case only
        if field_name == "friendship" and value.endswith("_FRIENDSHIP"):
            prefix = value[:-11]  # Remove "_FRIENDSHIP"
            return prefix.lower().replace("_", "-")
        
        # growthRate: GROWTH_* -> kebab-case only
        if field_name == "growthRate" and value.startswith("GROWTH_"):
            suffix = value[7:]  # Remove "GROWTH_"
            return suffix.lower().replace("_", "-")
        
        # bodyColor: BODY_COLOR_* -> kebab-case only
        if field_name == "bodyColor" and value.startswith("BODY_COLOR_"):
            suffix = value[11:]  # Remove "BODY_COLOR_"
            return suffix.lower().replace("_", "-")
        
        # frontAnimId: ANIM_* -> kebab-case only
        if field_name == "frontAnimId" and value.startswith("ANIM_"):
            suffix = value[5:]  # Remove "ANIM_"
            return suffix.lower().replace("_", "-")
        
        # backAnimId: BACK_ANIM_* -> kebab-case only
        if field_name == "backAnimId" and value.startswith("BACK_ANIM_"):
            suffix = value[10:]  # Remove "BACK_ANIM_"
            return suffix.lower().replace("_", "-")
        
        # pokemonJumpType: PKMN_JUMP_TYPE_* -> kebab-case only
        if field_name == "pokemonJumpType" and value.startswith("PKMN_JUMP_TYPE_"):
            suffix = value[15:]  # Remove "PKMN_JUMP_TYPE_"
            return suffix.lower().replace("_", "-")
        
        # cryId: CRY_* -> kebab-case only
        if field_name == "cryId" and value.startswith("CRY_"):
            suffix = value[4:]  # Remove "CRY_"
            return suffix.lower().replace("_", "-")
        
        # natDexNum: NATIONAL_DEX_* -> kebab-case only
        if field_name == "natDexNum" and value.startswith("NATIONAL_DEX_"):
            suffix = value[13:]  # Remove "NATIONAL_DEX_"
            return suffix.lower().replace("_", "-")
    
    # Simple identifiers (variable names) can be plain strings
    # Examples: gMonFrontPic_Abra, sAbraFormSpeciesIdTable
    if re.match(r'^[A-Za-z_][A-Za-z0-9_]*$', value):
        return value
    
    # Everything else is raw C code (expressions, function calls, arrays, etc.)
    return {"raw": value}

def find_longest_common_prefix(names):
    """Find the longest common prefix among a list of names."""
    if not names:
        return ""
    if len(names) == 1:
        return names[0]
    
    # Sort to compare first and last (they'll be most different)
    sorted_names = sorted(names)
    first = sorted_names[0]
    last = sorted_names[-1]
    
    prefix = ""
    for i in range(min(len(first), len(last))):
        if first[i] == last[i]:
            prefix += first[i]
        else:
            break
    
    # Clean up trailing underscores
    return prefix.rstrip('_')

def create_templates_from_unparsed(species_dict, unparsed_by_prefix, c_code):
    """Create template species for macro-based unparsed species groups."""
    if not unparsed_by_prefix:
        return species_dict
    
    templates_created = 0
    
    for prefix, names in unparsed_by_prefix.items():
        # Find longest common prefix for this group
        template_name = find_longest_common_prefix(names)
        
        # If all names are identical or no common prefix, use the prefix itself
        if not template_name or template_name == prefix:
            template_name = prefix
        
        # Try to extract common fields from the macro definition
        macro_pattern = rf'#define\s+{prefix}_MISC_INFO[^{{]*\{{([^}}]+?(?:\{{[^}}]*\}}[^}}]*)*)\}}'
        macro_match = re.search(macro_pattern, c_code, re.DOTALL)
        
        template_data = {
            "template": True,
            "forms": {}
        }
        
        # If we found a macro definition, try to parse its common fields
        if macro_match:
            macro_body = macro_match.group(1)
            try:
                parsed_fields = parse_species_body(macro_body)
                # Add parsed fields to template (except template marker)
                for field, value in parsed_fields.items():
                    if field != "template":
                        template_data[field] = value
                logging.info(f"Created template {template_name} with {len(parsed_fields)} fields from macro")
            except Exception as e:
                logging.debug(f"Could not parse macro fields for {prefix}: {e}")
        
        # Add all unparsed variants as forms with minimal data
        for name in names:
            # Extract form suffix
            if name.startswith(template_name + "_"):
                form_key = name[len(template_name) + 1:]
            elif name == template_name:
                # Skip the exact match, it's the base
                continue
            else:
                # Use full name if pattern doesn't match
                form_key = name
            
            # Create placeholder form with just a marker
            template_data["forms"][form_key] = {
                "raw_placeholder": True,
                "original_name": name
            }
        
        # Only create template if we have forms
        if template_data["forms"]:
            species_dict[template_name] = template_data
            templates_created += 1
            logging.info(f"Created template {template_name} with {len(template_data['forms'])} forms (macro-based)")
        else:
            logging.warning(f"No forms to create template for {template_name}")
    
    if templates_created > 0:
        logging.info(f"Created {templates_created} templates for unparsed species groups")
    
    return species_dict

def create_templates_from_parsed_groups(species_dict):
    """Create templates for parsed species that share a common prefix (like MOTHIM_PLANT, MOTHIM_SANDY, etc)."""
    # Find groups of species that share a common prefix
    prefix_groups = {}
    
    for species_name in list(species_dict.keys()):
        # Skip if already has forms or is already a template
        if "forms" in species_dict[species_name] or species_dict[species_name].get("template"):
            continue
        
        # Skip if has formSpeciesIdTable (these are handled by group_forms())
        if "formSpeciesIdTable" in species_dict[species_name]:
            continue
            
        # Extract prefix (everything before the last underscore, if meaningful)
        parts = species_name.split('_')
        if len(parts) >= 2:
            # Try different prefix lengths
            for i in range(len(parts) - 1, 0, -1):
                prefix = '_'.join(parts[:i])
                if prefix not in prefix_groups:
                    prefix_groups[prefix] = []
                prefix_groups[prefix].append(species_name)
    
    # Filter to only groups with 2+ members
    prefix_groups = {k: v for k, v in prefix_groups.items() if len(v) >= 2}
    
    if not prefix_groups:
        return species_dict
    
    # Filter to the most specific grouping (e.g., prefer "MOTHIM" over "MOTH")
    # by checking if all members actually share the exact prefix
    filtered_groups = {}
    for prefix, members in prefix_groups.items():
        if all(m.startswith(prefix + "_") for m in members):
            filtered_groups[prefix] = members
    
    if not filtered_groups:
        return species_dict
    
    logging.info(f"Found {len(filtered_groups)} parsed species groups to templatize")
    
    templates_created = 0
    for prefix, members in sorted(filtered_groups.items()):
        # Find common fields among all members
        common_fields = None
        member_datas = {}
        
        for member in members:
            member_data = species_dict[member]
            member_datas[member] = member_data
            
            if common_fields is None:
                common_fields = set(member_data.keys())
            else:
                common_fields &= set(member_data.keys())
        
        # Build template with common field values
        template_data = {"template": True, "forms": {}}
        
        for field in common_fields:
            # Check if all members have the same value
            values = [member_datas[m][field] for m in members]
            if all(v == values[0] for v in values):
                template_data[field] = values[0]
        
        # Create forms with only differing fields
        for member in members:
            # Extract form suffix
            if member.startswith(prefix + "_"):
                form_key = member[len(prefix) + 1:]
            else:
                form_key = member
            
            # For templates: forms need complete data (template base won't be generated)
            # Start with template fields, then add/override with member fields
            form_data = {}
            for field in template_data:
                if field not in ["template", "forms"]:
                    form_data[field] = template_data[field]
            
            # Add member-specific fields (override template if different)
            for field, value in member_datas[member].items():
                form_data[field] = value
            
            template_data["forms"][form_key] = form_data
            
            # Remove the original member from species_dict
            del species_dict[member]
        
        # Add the template
        species_dict[prefix] = template_data
        templates_created += 1
        logging.info(f"Created template {prefix} with {len(template_data.get('forms', {}))} forms from parsed species")
    
    if templates_created > 0:
        logging.info(f"Created {templates_created} templates from parsed species groups")
    
    return species_dict

def group_forms(species_dict):
    """Group species forms under their parent species."""
    # First pass: identify form groups by formSpeciesIdTable
    form_groups = {}  # Maps formSpeciesIdTable -> list of species names
    
    for species_name, species_data in species_dict.items():
        form_table = species_data.get('formSpeciesIdTable')
        if form_table:
            if form_table not in form_groups:
                form_groups[form_table] = []
            form_groups[form_table].append(species_name)
    
    # Log form groups
    if form_groups:
        logging.info(f"Found {len(form_groups)} form groups:")
        for table, members in form_groups.items():
            if len(members) > 1:
                logging.info(f"  {table}: {', '.join(members)}")
    
    # Second pass: restructure into parent + forms
    result = {}
    processed = set()
    forms_created = 0
    
    for species_name, species_data in species_dict.items():
        if species_name in processed:
            continue
        
        form_table = species_data.get('formSpeciesIdTable')
        
        # Check if this species is part of a form group
        if form_table and form_table in form_groups and len(form_groups[form_table]) > 1:
            form_list = form_groups[form_table]
            
            # Find the parent (base form) - usually the shortest name or one without underscore suffix
            parent_name = min(form_list, key=lambda x: (len(x), x))
            
            # If this is the parent, create the forms structure
            if species_name == parent_name:
                parent_data = species_data.copy()
                forms = {}
                
                # Determine if forms follow parent_suffix pattern or need a common prefix
                common_prefix = find_longest_common_prefix(form_list)
                uses_common_prefix = False
                
                # If parent name doesn't match common prefix, we need to store it
                if common_prefix and common_prefix != parent_name:
                    uses_common_prefix = True
                    logging.debug(f"Forms use common prefix '{common_prefix}' different from parent '{parent_name}'")
                
                # Process all forms in this group
                for form_name in form_list:
                    if form_name == parent_name:
                        continue
                    
                    processed.add(form_name)
                    form_data = species_dict.get(form_name)
                    
                    if not form_data:
                        logging.warning(f"Form {form_name} not found in species_dict")
                        continue
                    
                    # Extract form suffix (e.g., "VENUSAUR_MEGA" -> "MEGA")
                    if form_name.startswith(parent_name + "_"):
                        form_key = form_name[len(parent_name) + 1:]  # +1 for underscore
                    else:
                        # Forms don't follow parent_suffix pattern (e.g., BURMY_PLANT vs BURMY_SANDY)
                        # Find common prefix among all forms and extract the unique suffix
                        if common_prefix and form_name.startswith(common_prefix + "_"):
                            form_key = form_name[len(common_prefix) + 1:]
                            logging.debug(f"Extracted form key '{form_key}' from {form_name} using common prefix '{common_prefix}'")
                        else:
                            # Last resort: use full name
                            logging.warning(f"Form {form_name} doesn't match parent {parent_name} naming pattern, using full name")
                            form_key = form_name
                    
                    # Store complete form data (don't simplify to just differences)
                    # This matches the original C format where each species entry is complete
                    forms[form_key] = form_data
                    forms_created += 1
                
                # Add forms to parent if any exist
                if forms:
                    parent_data['forms'] = forms
                    # If forms use a different prefix than parent name, store it
                    if uses_common_prefix:
                        parent_data['formPrefix'] = common_prefix
                        logging.debug(f"Stored formPrefix '{common_prefix}' for {parent_name}")
                
                result[species_name] = parent_data
                processed.add(species_name)
            # If this is a form but we haven't seen parent yet, skip (will be processed with parent)
        else:
            # Not part of a form group, add as-is
            result[species_name] = species_data
            processed.add(species_name)
    
    logging.info(f"Grouped {forms_created} forms under their parent species")
    return result

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 tools/species_to_json.py <input_file.h> [output_file.json]")
        sys.exit(1)
    
    file_path = sys.argv[1]
    
    logging.info(f"Reading {file_path}...")
    
    # Read the file
    try:
        with open(file_path, 'r') as f:
            c_code = f.read()
    except FileNotFoundError:
        logging.error(f"Could not find file {file_path}")
        sys.exit(1)
    
    # Parse all species from the file
    logging.info("Parsing species definitions...")
    species_dict, unparsed_by_prefix = parse_species_info(c_code)
    
    # Store parse stats for final summary
    all_entries_count = len(count_all_species_entries(c_code))
    parsed_count = len(species_dict)
    unparsed_count = all_entries_count - parsed_count
    
    if not species_dict:
        logging.error("No species were successfully parsed!")
        sys.exit(1)
    
    # Create templates from parsed species with shared prefixes (like MOTHIM_PLANT, MOTHIM_SANDY)
    logging.info("Checking for parsed species groups to templatize...")
    species_dict = create_templates_from_parsed_groups(species_dict)
    
    # Create templates for unparsed macro-based species
    if unparsed_by_prefix:
        logging.info("Creating templates for unparsed species groups...")
        species_dict = create_templates_from_unparsed(species_dict, unparsed_by_prefix, c_code)
    
    # Group forms under their parent species
    logging.info("Grouping forms...")
    species_dict = group_forms(species_dict)
    
    # Output as JSON - wrap in "data" for template iteration
    output = {"data": species_dict}
    
    # Validate JSON is serializable
    try:
        json_str = json.dumps(output, indent=2)
    except Exception as e:
        logging.error(f"Failed to serialize to JSON: {e}")
        sys.exit(1)
    
    # Write to output file if specified, otherwise print to stdout
    if len(sys.argv) >= 3:
        output_path = sys.argv[2]
        logging.info(f"Writing to {output_path}...")
        try:
            with open(output_path, 'w') as f:
                f.write(json_str)
            
            file_size = len(json_str)
            logging.info(f"Successfully wrote {file_size} bytes to {output_path}")
            
            # Calculate some statistics
            total_species = len(species_dict)
            total_forms = sum(len(info.get('forms', {})) for info in species_dict.values())
            total_entries = total_species + total_forms
            
            logging.info("=" * 60)
            logging.info("CONVERSION SUMMARY:")
            logging.info(f"  Base species: {total_species}")
            logging.info(f"  Forms: {total_forms}")
            logging.info(f"  Total entries converted: {total_entries}")
            if unparsed_count > 0:
                logging.error(f"  Unparsed entries: {unparsed_count} (see ERROR messages above)")
                logging.error(f"  Coverage: {parsed_count}/{all_entries_count} ({parsed_count/all_entries_count*100:.1f}%)")
            logging.info(f"  Output size: {file_size:,} bytes ({file_size / 1024:.1f} KB)")
            logging.info("=" * 60)
            if unparsed_count > 0:
                logging.warning("⚠ Conversion completed with unparsed entries!")
                logging.warning("  Some species use macros/non-standard formats and were not converted.")
                logging.warning("  Review ERROR messages above for details.")
            else:
                logging.info("✓ Conversion completed successfully!")
            logging.info("  Next steps:")
            logging.info("  1. Review any WARNING/ERROR messages above")
            logging.info("  2. Build and test: make clean && make -j$(nproc)")
            logging.info("  3. Compare generated C with original")
            
        except Exception as e:
            logging.error(f"Failed to write output file: {e}")
            sys.exit(1)
    else:
        print(json_str)

if __name__ == '__main__':
    main()
