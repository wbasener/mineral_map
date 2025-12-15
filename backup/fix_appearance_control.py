#!/usr/bin/env python3
"""
Script to fix the Leaflet.Control.Appearance implementation issues.

This script fixes:
1. Wrong map ID in the appearance control
2. Missing name property on tile layers
3. Removes automatic .addTo() calls for layers (let the control manage them)
"""

import re
import shutil
from datetime import datetime
from pathlib import Path


def backup_file(file_path):
    """Create a timestamped backup."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = file_path.parent / f"{file_path.stem}.backup_{timestamp}{file_path.suffix}"
    shutil.copy2(file_path, backup)
    print(f"Created backup: {backup}")
    return backup


def fix_appearance_control(html_file_path):
    """Fix the appearance control issues."""
    html_file = Path(html_file_path)

    print("Loading index.html...")
    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find the actual map ID
    map_match = re.search(r'var (map_[a-f0-9]+) = L\.map', content)
    if not map_match:
        print("ERROR: Could not find map variable!")
        return

    actual_map_id = map_match.group(1)
    print(f"Found actual map ID: {actual_map_id}")

    # Extract layer names from the old layer control if it still exists in backup
    # We'll manually set the names for tile layers
    tile_layer_names = {
        'openstreetmap': 'OpenStreetMap',
        'Topographic Map': 'Topographic Map',
        'Light Map': 'Light Map',
        'Satellite Imagery': 'Satellite Imagery'
    }

    # Find all tile layer IDs
    tile_layers = re.findall(r'var (tile_layer_[a-f0-9]+) = L\.tileLayer', content)
    print(f"Found {len(tile_layers)} tile layers: {tile_layers}")

    # Add name property to each tile layer
    for i, layer_id in enumerate(tile_layers):
        layer_names_list = list(tile_layer_names.values())
        if i < len(layer_names_list):
            layer_name = layer_names_list[i]

            # Find the tile layer definition and add name property
            pattern = rf'(var {layer_id} = L\.tileLayer\(\s*"[^"]+",\s*\{{)'

            def add_name(match):
                return match.group(1) + f'\n  "name": "{layer_name}",'

            content = re.sub(pattern, add_name, content)
            print(f"Added name '{layer_name}' to {layer_id}")

    # Remove .addTo() calls for tile layers (except the first one which should be the default)
    # Keep only the first tile layer added to the map
    tile_layer_addto_pattern = r'tile_layer_[a-f0-9]+\.addTo\(map_[a-f0-9]+\);'
    addto_calls = re.findall(tile_layer_addto_pattern, content)

    if len(addto_calls) > 1:
        # Remove all but the first one
        for i, call in enumerate(addto_calls):
            if i > 0:  # Keep the first one
                # Comment out instead of removing
                content = content.replace(call, f'// {call} // Commented out - managed by appearance control', 1)
        print(f"Commented out {len(addto_calls) - 1} tile layer .addTo() calls")

    # Fix the map ID in the appearance control
    wrong_map_pattern = r'\.addTo\(map_[a-f0-9]+\);'

    # Find the appearance control specifically
    appearance_pattern = r'(var appearanceControl = L\.control\.appearance\(.*?\))\.addTo\((map_[a-f0-9]+)\);'

    match = re.search(appearance_pattern, content, re.DOTALL)
    if match:
        old_map_id = match.group(2)
        if old_map_id != actual_map_id:
            print(f"Fixing map ID: {old_map_id} -> {actual_map_id}")
            content = re.sub(
                r'(var appearanceControl = L\.control\.appearance\(.*?\))\.addTo\(map_[a-f0-9]+\);',
                rf'\1.addTo({actual_map_id});',
                content,
                flags=re.DOTALL
            )
        else:
            print("Map ID is already correct")
    else:
        print("WARNING: Could not find appearance control definition!")

    # Save the fixed content
    print("\nSaving fixed content...")
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(content)

    print("✓ Fix complete!")
    print("\nChanges made:")
    print(f"1. Added 'name' property to {len(tile_layers)} tile layers")
    print(f"2. Fixed map ID to: {actual_map_id}")
    print(f"3. Commented out redundant .addTo() calls for base layers")
    print("\nPlease reload index.html in your browser to test.")


def main():
    html_file = Path(__file__).parent / "index.html"

    if not html_file.exists():
        print(f"ERROR: {html_file} not found!")
        return

    # Create backup
    backup_file(html_file)

    # Apply fixes
    fix_appearance_control(html_file)


if __name__ == "__main__":
    main()
