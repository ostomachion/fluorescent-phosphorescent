#!/usr/bin/env python3
"""
Wrapper around jsonproc that groups consecutive fields with the same preprocessor condition.

Usage: python3 tools/jsonproc_with_grouping.py <input.json> <template.txt> <output.h>
"""

import sys
import subprocess
import re
import tempfile
import os

def group_preprocessor_blocks(content):
    """
    Group consecutive lines with the same preprocessor condition.
    
    Input:
        #if COND_A
        .field1 = value1,
        #endif //COND_A
        #if COND_A
        .field2 = value2,
        #endif //COND_A
        
    Output:
        #if COND_A
        .field1 = value1,
        .field2 = value2,
        #endif //COND_A
    """
    lines = content.split('\n')
    result = []
    i = 0
    
    while i < len(lines):
        line = lines[i]
        
        # Check if this is an #if directive
        if_match = re.match(r'^(\s*)#if\s+(.+)$', line)
        if if_match:
            indent = if_match.group(1)
            condition = if_match.group(2).strip()
            
            # Collect all lines until matching #endif
            block_lines = [line]
            i += 1
            depth = 1
            
            while i < len(lines) and depth > 0:
                current = lines[i]
                if re.match(r'^\s*#if', current):
                    depth += 1
                elif re.match(r'^\s*#endif', current):
                    depth -= 1
                    if depth == 0:
                        # Found matching endif
                        block_lines.append(current)
                        break
                block_lines.append(current)
                i += 1
            
            # Check if the next block has the same condition
            same_condition_blocks = [block_lines]
            while i + 1 < len(lines):
                next_line = lines[i + 1]
                next_if_match = re.match(r'^(\s*)#if\s+(.+)$', next_line)
                
                if next_if_match and next_if_match.group(2).strip() == condition:
                    # Same condition! Collect this block too
                    i += 1
                    next_block = [next_line]
                    i += 1
                    depth = 1
                    
                    while i < len(lines) and depth > 0:
                        current = lines[i]
                        if re.match(r'^\s*#if', current):
                            depth += 1
                        elif re.match(r'^\s*#endif', current):
                            depth -= 1
                            if depth == 0:
                                next_block.append(current)
                                break
                        next_block.append(current)
                        i += 1
                    
                    same_condition_blocks.append(next_block)
                else:
                    break
            
            # Merge all blocks with the same condition
            if len(same_condition_blocks) > 1:
                # Extract content from each block (everything except #if and #endif)
                # Also collect the indent from the first #if line
                first_if_line = block_lines[0]
                if_indent = len(first_if_line) - len(first_if_line.lstrip())
                
                all_content = []
                for block in same_condition_blocks:
                    all_content.extend(block[1:-1])  # Skip first (#if) and last (#endif)
                
                # Output merged block
                result.append(block_lines[0])  # #if line
                result.extend(all_content)
                result.append(block_lines[-1])  # #endif line
            else:
                # Just one block, output as-is
                result.extend(block_lines)
        else:
            result.append(line)
        
        i += 1
    
    return '\n'.join(result)

def main():
    if len(sys.argv) != 4:
        print("Usage: python3 jsonproc_with_grouping.py <input.json> <template.txt> <output.h>")
        sys.exit(1)
    
    input_json = sys.argv[1]
    template_file = sys.argv[2]
    output_file = sys.argv[3]
    
    # Create a temporary file for jsonproc output
    with tempfile.NamedTemporaryFile(mode='w+', suffix='.h', delete=False) as tmp:
        tmp_path = tmp.name
    
    try:
        # Run jsonproc to generate initial output
        jsonproc_path = os.path.join(os.path.dirname(__file__), 'jsonproc', 'jsonproc')
        result = subprocess.run(
            [jsonproc_path, input_json, template_file, tmp_path],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            print(f"Error running jsonproc: {result.stderr}")
            sys.exit(result.returncode)
        
        # Read the output
        with open(tmp_path, 'r') as f:
            content = f.read()
        
        # Group consecutive blocks with same condition
        grouped_content = group_preprocessor_blocks(content)
        
        # Write final output
        with open(output_file, 'w') as f:
            f.write(grouped_content)
        
        print(f"Successfully generated {output_file} with grouped preprocessor blocks")
        
    finally:
        # Clean up temporary file
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)

if __name__ == '__main__':
    main()
