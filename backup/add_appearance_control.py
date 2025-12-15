#!/usr/bin/env python3
"""
Script to modify index.html to incorporate Leaflet.Control.Appearance plugin.

This script:
1. Creates a backup of the original index.html
2. Adds plugin script/CSS references
3. Modifies layer definitions to include name, color, and opacity options
4. Replaces L.control.layers() with L.control.appearance()
"""

import re
import shutil
from datetime import datetime
from pathlib import Path


class AppearanceControlModifier:
    """Modifies Leaflet map to use Control.Appearance plugin."""

    def __init__(self, html_file_path):
        self.html_file = Path(html_file_path)
        self.backup_file = None
        self.content = ""
        self.modifications = []

    def backup_original(self):
        """Create a timestamped backup of the original file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.backup_file = self.html_file.parent / f"{self.html_file.stem}.backup_{timestamp}{self.html_file.suffix}"
        shutil.copy2(self.html_file, self.backup_file)
        self.log(f"Created backup: {self.backup_file}")

    def load_content(self):
        """Load the HTML file content."""
        with open(self.html_file, 'r', encoding='utf-8') as f:
            self.content = f.read()
        self.log(f"Loaded {self.html_file} ({len(self.content)} characters)")

    def save_content(self):
        """Save the modified content back to the file."""
        with open(self.html_file, 'w', encoding='utf-8') as f:
            f.write(self.content)
        self.log(f"Saved modified content to {self.html_file}")

    def log(self, message):
        """Log a modification message."""
        print(message)
        self.modifications.append(message)

    def add_plugin_references(self):
        """Add Leaflet.Control.Appearance plugin script and CSS to <head>."""
        # Find where to insert (after existing leaflet includes)
        pattern = r'(<script src="https://cdn\.jsdelivr\.net/npm/leaflet@.*?</script>)'

        # Plugin URLs (using rawgit/jsdelivr for GitHub raw files)
        plugin_script = '''    <script src="https://cdn.jsdelivr.net/gh/Kanahiro/Leaflet.Control.Appearance@master/dist/L.Control.Appearance.js"></script>'''
        plugin_css = '''    <link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/Kanahiro/Leaflet.Control.Appearance@master/dist/L.Control.Appearance.css"/>'''

        # Insert after the Leaflet script
        def insert_after_leaflet(match):
            return match.group(1) + '\n' + plugin_script

        self.content = re.sub(pattern, insert_after_leaflet, self.content, count=1)

        # Insert CSS after Leaflet CSS
        css_pattern = r'(<link rel="stylesheet" href="https://cdn\.jsdelivr\.net/npm/leaflet@.*?/>)'

        def insert_css_after_leaflet(match):
            return match.group(1) + '\n' + plugin_css

        self.content = re.sub(css_pattern, insert_css_after_leaflet, self.content, count=1)

        self.log("Added Leaflet.Control.Appearance plugin references")

    def extract_layer_info(self):
        """Extract information about all layers from the HTML."""
        # Extract GeoJSON layer IDs
        geojson_pattern = r'var (geo_json_[a-f0-9]+) = L\.geoJson'
        geojson_layers = re.findall(geojson_pattern, self.content)

        # Extract tile layer IDs
        tile_pattern = r'var (tile_layer_[a-f0-9]+) = L\.tileLayer'
        tile_layers = re.findall(tile_pattern, self.content)

        # Extract layer control mapping
        layer_control_pattern = r'var layer_control_.*?_layers = \{(.*?)\};'
        layer_control_match = re.search(layer_control_pattern, self.content, re.DOTALL)

        layer_info = {
            'geojson_layers': geojson_layers,
            'tile_layers': tile_layers,
            'layer_names': {}
        }

        if layer_control_match:
            control_content = layer_control_match.group(1)

            # Extract base layer names
            base_pattern = r'base_layers\s*:\s*\{(.*?)\}'
            base_match = re.search(base_pattern, control_content, re.DOTALL)
            if base_match:
                name_pattern = r'"([^"]+)"\s*:\s*(tile_layer_[a-f0-9]+)'
                for name, var_id in re.findall(name_pattern, base_match.group(1)):
                    layer_info['layer_names'][var_id] = name

            # Extract overlay names
            overlay_pattern = r'overlays\s*:\s*\{(.*?)\}'
            overlay_match = re.search(overlay_pattern, control_content, re.DOTALL)
            if overlay_match:
                name_pattern = r'"([^"]+)"\s*:\s*(geo_json_[a-f0-9]+)'
                for name, var_id in re.findall(name_pattern, overlay_match.group(1)):
                    # Decode HTML entities
                    name = name.replace('\\u003e', '>')
                    layer_info['layer_names'][var_id] = name

        self.log(f"Found {len(tile_layers)} tile layers and {len(geojson_layers)} GeoJSON layers")
        return layer_info

    def extract_layer_styles(self, layer_id):
        """Extract fillColor and fillOpacity from a layer's styler function."""
        pattern = rf'function {layer_id}_styler\(feature\) \{{.*?return \{{([^}}]+)\}};'
        match = re.search(pattern, self.content, re.DOTALL)

        if match:
            style_content = match.group(1)

            # Extract fillColor
            color_match = re.search(r'"fillColor"\s*:\s*"([^"]+)"', style_content)
            fill_color = color_match.group(1) if color_match else '#000000'

            # Extract fillOpacity
            opacity_match = re.search(r'"fillOpacity"\s*:\s*([\d.]+)', style_content)
            fill_opacity = float(opacity_match.group(1)) if opacity_match else 0.6

            return fill_color, fill_opacity

        return '#000000', 0.6

    def modify_geojson_layers(self, layer_info):
        """Add name, color, and opacity options to GeoJSON layer definitions."""
        for layer_id in layer_info['geojson_layers']:
            layer_name = layer_info['layer_names'].get(layer_id, layer_id)
            fill_color, fill_opacity = self.extract_layer_styles(layer_id)

            # Find the layer definition
            pattern = rf'(var {layer_id} = L\.geoJson\(null, \{{)'

            # Add options object with name, color, opacity
            options_code = f'''
                name: "{layer_name}",
                color: "{fill_color}",
                opacity: {fill_opacity},'''

            replacement = rf'\1{options_code}'
            self.content = re.sub(pattern, replacement, self.content)

        self.log(f"Modified {len(layer_info['geojson_layers'])} GeoJSON layers with appearance options")

    def create_layer_arrays(self, layer_info):
        """Create JavaScript code to organize layers into arrays."""
        # Build baseLayers array
        base_layers_code = "        var baseLayers = [\n"
        for tile_id in layer_info['tile_layers']:
            base_layers_code += f"            {tile_id},\n"
        base_layers_code += "        ];\n\n"

        # Build uneditableOverlays array (empty for now)
        uneditable_code = "        var uneditableOverlays = [];\n\n"

        # Build overlays array
        overlays_code = "        var overlays = [\n"
        for geo_id in layer_info['geojson_layers']:
            overlays_code += f"            {geo_id},\n"
        overlays_code += "        ];\n\n"

        return base_layers_code + uneditable_code + overlays_code

    def replace_layer_control(self, layer_info):
        """Replace L.control.layers() with L.control.appearance()."""
        # First, add the layer arrays before the layer control
        layer_arrays = self.create_layer_arrays(layer_info)

        # Find the layer control definition
        control_pattern = r'var layer_control_[a-f0-9]+_layers = \{.*?\};.*?let layer_control_[a-f0-9]+ = L\.control\.layers\(.*?\)\.addTo\(map_[a-f0-9]+\);'

        # New appearance control code
        appearance_control = '''var appearanceControl = L.control.appearance(
            baseLayers,
            uneditableOverlays,
            overlays,
            {
                position: 'topright',
                radioCheckbox: true,
                layerName: true,
                opacity: true,
                color: true,
                remove: true
            }
        ).addTo(map_d2a376f3bebc49e2468588d70e0e50c9);'''

        replacement = layer_arrays + appearance_control

        self.content = re.sub(control_pattern, replacement, self.content, flags=re.DOTALL)

        self.log("Replaced L.control.layers() with L.control.appearance()")

    def save_log(self):
        """Save modification log to a file."""
        log_file = self.html_file.parent / f"modification_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(log_file, 'w', encoding='utf-8') as f:
            f.write("Leaflet.Control.Appearance Modification Log\n")
            f.write("=" * 50 + "\n\n")
            for mod in self.modifications:
                f.write(f"{mod}\n")
        print(f"\nLog saved to: {log_file}")

    def process(self):
        """Execute all modification steps."""
        print("Starting Leaflet.Control.Appearance integration...\n")

        # Step 1: Backup
        self.backup_original()

        # Step 2: Load content
        self.load_content()

        # Step 3: Extract layer information
        layer_info = self.extract_layer_info()

        # Step 4: Add plugin references
        self.add_plugin_references()

        # Step 5: Modify GeoJSON layers
        self.modify_geojson_layers(layer_info)

        # Step 6: Replace layer control
        self.replace_layer_control(layer_info)

        # Step 7: Save modified content
        self.save_content()

        # Step 8: Save log
        self.save_log()

        print("\n" + "=" * 50)
        print("Modification complete!")
        print(f"Original file backed up to: {self.backup_file}")
        print(f"Modified file: {self.html_file}")
        print("=" * 50)


def main():
    """Main entry point."""
    html_file = Path(__file__).parent / "index.html"

    if not html_file.exists():
        print(f"Error: {html_file} not found!")
        return

    modifier = AppearanceControlModifier(html_file)
    modifier.process()


if __name__ == "__main__":
    main()
